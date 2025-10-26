"""
Oxylabs-Enhanced Contact Spider

This spider uses Oxylabs Web Scraper API to bypass anti-bot protection
and scrape protected websites like UCSI University.
"""

import scrapy
import requests
import base64
import time
import re
from urllib.parse import urljoin, urlparse
from uni_scraper.items import ContactItem


class OxylabsContactSpider(scrapy.Spider):
    name = 'oxylabs_contact_spider'
    
    def __init__(self, start_url=None, allowed_domain=None, username=None, password=None, *args, **kwargs):
        super(OxylabsContactSpider, self).__init__(*args, **kwargs)
        
        if not start_url:
            raise ValueError("start_url is required. Use: -a start_url=https://example.com")
        
        if not username or not password:
            raise ValueError("Oxylabs credentials required. Use: -a username=your_username -a password=your_password")
        
        self.start_urls = [start_url]
        self.username = username
        self.password = password
        
        # Extract domain from start_url if not provided
        if allowed_domain:
            self.allowed_domains = [allowed_domain]
        else:
            parsed_uri = urlparse(start_url)
            domain = parsed_uri.netloc
            domain = domain.replace('www.', '')
            self.allowed_domains = [domain]
        
        self.logger.info(f"Starting Oxylabs spider with URL: {start_url}")
        self.logger.info(f"Allowed domains: {self.allowed_domains}")
        
        # Oxylabs API configuration
        self.oxylabs_url = "https://realtime.oxylabs.io/v1/queries"
        self.auth_string = base64.b64encode(f"{username}:{password}".encode()).decode()
        self.headers = {
            "Authorization": f"Basic {self.auth_string}",
            "Content-Type": "application/json"
        }
        
        # Email and phone patterns
        self.email_pattern = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        )
        self.phone_pattern = re.compile(
            r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}|\+?\d{10,}'
        )
    
    def start_requests(self):
        """
        Start requests using Oxylabs API instead of direct HTTP requests.
        """
        for url in self.start_urls:
            # Create a fake request that will be handled by parse_with_oxylabs
            yield scrapy.Request(
                url=url,
                callback=self.parse_with_oxylabs,
                meta={'original_url': url},
                dont_filter=True
            )
    
    def parse_with_oxylabs(self, response):
        """
        Parse response using Oxylabs API to bypass anti-bot protection.
        """
        original_url = response.meta.get('original_url', response.url)
        self.logger.info(f"Processing {original_url} via Oxylabs API")
        
        # Use Oxylabs API to get the page content
        oxylabs_result = self.scrape_with_oxylabs(original_url)
        
        if oxylabs_result and oxylabs_result.get('content'):
            # Create a fake response object with the Oxylabs content
            fake_response = scrapy.http.HtmlResponse(
                url=original_url,
                body=oxylabs_result['content'].encode('utf-8'),
                encoding='utf-8'
            )
            
            # Extract contacts from the content
            yield from self.extract_contacts(fake_response)
            
            # Find and follow links for pagination
            yield from self.find_and_follow_links(fake_response)
        else:
            self.logger.warning(f"Failed to get content for {original_url} via Oxylabs")
    
    def scrape_with_oxylabs(self, url):
        """
        Scrape a URL using Oxylabs API.
        """
        payload = {
            "source": "universal",
            "url": url,
            "render": "html",
            "geo_location": "us",
            "parse": True,
            "context": [
                {
                    "key": "page_type",
                    "value": "university_contact"
                }
            ]
        }
        
        try:
            response = requests.post(
                self.oxylabs_url,
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("results") and len(result["results"]) > 0:
                    return result["results"][0]
                else:
                    self.logger.warning(f"No results returned for {url}")
                    return None
            else:
                self.logger.error(f"Oxylabs API error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error calling Oxylabs API for {url}: {e}")
            return None
    
    def extract_contacts(self, response):
        """
        Extract contact information from the response.
        """
        # Strategy 1: Look for common contact container classes
        contact_selectors = [
            '.contact-card', '.contact-info', '.contact', '.person-card',
            '.staff-member', '.faculty-member', '.team-member', '.profile',
            '.employee', '.directory-entry', '[class*="contact"]',
            '[class*="staff"]', '[class*="faculty"]', '[class*="member"]'
        ]
        
        for selector in contact_selectors:
            contact_elements = response.css(selector)
            if contact_elements:
                self.logger.info(f"Found {len(contact_elements)} contacts using selector: {selector}")
                for element in contact_elements:
                    contact = self.extract_contact_from_element(element, response.url)
                    if contact and (contact.get('email') or contact.get('phone')):
                        yield contact
                return  # If we found contacts with this selector, stop trying others
        
        # Strategy 2: Look for structured data (tables, lists)
        table_rows = response.css('table tr, .directory-list li, ul.contacts li')
        if table_rows:
            for row in table_rows:
                contact = self.extract_contact_from_element(row, response.url)
                if contact and (contact.get('email') or contact.get('phone')):
                    yield contact
            return
        
        # Strategy 3: Page-wide extraction (last resort)
        page_text = response.url.lower()
        if any(keyword in page_text for keyword in ['contact', 'staff', 'faculty', 'directory', 'people', 'team', 'about']):
            self.logger.info("Using page-wide extraction strategy")
            contact = self.extract_contact_from_element(response, response.url)
            if contact and (contact.get('email') or contact.get('phone')):
                yield contact
    
    def extract_contact_from_element(self, element, source_url):
        """
        Extract contact information from a specific element.
        """
        contact = ContactItem()
        contact['source_url'] = source_url
        
        # Get all text from the element
        text_content = ' '.join(element.css('*::text').getall())
        
        # Extract email
        emails = self.email_pattern.findall(text_content)
        contact['email'] = emails[0] if emails else None
        
        # Also check for mailto links
        if not contact['email']:
            mailto_links = element.css('a[href^="mailto:"]::attr(href)').getall()
            if mailto_links:
                contact['email'] = mailto_links[0].replace('mailto:', '').strip()
        
        # Extract phone
        phones = self.phone_pattern.findall(text_content)
        contact['phone'] = ''.join(phones[0]) if phones else None
        
        # Also check for tel links
        if not contact['phone']:
            tel_links = element.css('a[href^="tel:"]::attr(href)').getall()
            if tel_links:
                contact['phone'] = tel_links[0].replace('tel:', '').strip()
        
        # Extract name (try various selectors)
        name_selectors = [
            '.name::text', '.person-name::text', 'h1::text', 'h2::text', 
            'h3::text', 'h4::text', '.title::text', '[class*="name"]::text',
            'strong::text', 'b::text'
        ]
        for selector in name_selectors:
            name = element.css(selector).get()
            if name and len(name.strip()) > 2:
                contact['name'] = name.strip()
                break
        
        # If no name found, try to extract from text near email
        if not contact.get('name') and contact.get('email'):
            text_parts = text_content.split(contact['email'])[0].split()
            potential_name = ' '.join(text_parts[-4:]) if len(text_parts) >= 2 else None
            if potential_name and 5 < len(potential_name) < 50:
                contact['name'] = potential_name.strip()
        
        # Extract designation/title
        designation_selectors = [
            '.designation::text', '.title::text', '.position::text', 
            '.job-title::text', '[class*="designation"]::text',
            '[class*="position"]::text', '[class*="role"]::text'
        ]
        for selector in designation_selectors:
            designation = element.css(selector).get()
            if designation:
                contact['designation'] = designation.strip()
                break
        
        # Extract university
        university_selectors = [
            '.university::text', '.institution::text', '.organization::text',
            '[class*="university"]::text', '[class*="institution"]::text'
        ]
        for selector in university_selectors:
            university = element.css(selector).get()
            if university:
                contact['university'] = university.strip()
                break
        
        # Extract department
        department_selectors = [
            '.department::text', '.dept::text', '[class*="department"]::text'
        ]
        for selector in department_selectors:
            department = element.css(selector).get()
            if department:
                contact['department'] = department.strip()
                break
        
        return contact
    
    def find_and_follow_links(self, response):
        """
        Find and follow links for pagination.
        """
        # Look for pagination links
        pagination_selectors = [
            'a[href*="page"]', 'a[href*="next"]', 'a[href*="more"]',
            '.pagination a', '.pager a', '.next', '.more'
        ]
        
        for selector in pagination_selectors:
            links = response.css(selector + '::attr(href)').getall()
            for link in links:
                absolute_url = urljoin(response.url, link)
                parsed = urlparse(absolute_url)
                domain = parsed.netloc.replace('www.', '')
                
                if domain in self.allowed_domains or any(d in domain for d in self.allowed_domains):
                    yield scrapy.Request(
                        url=absolute_url,
                        callback=self.parse_with_oxylabs,
                        meta={'original_url': absolute_url}
                    )
