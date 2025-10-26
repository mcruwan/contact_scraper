"""
Contact Spider - Main spider for scraping contact information.

This spider crawls through all pages of a given domain and extracts
contact details including name, email, phone, designation, and university.
"""

import scrapy
import re
from urllib.parse import urljoin, urlparse
from uni_scraper.items import ContactItem


class ContactSpider(scrapy.Spider):
    name = 'contact_spider'
    
    custom_settings = {
        'DEPTH_LIMIT': 5,  # Maximum depth to crawl
        'CLOSESPIDER_PAGECOUNT': 0,  # 0 means no limit, set to limit pages
    }
    
    def __init__(self, start_url=None, allowed_domain=None, *args, **kwargs):
        super(ContactSpider, self).__init__(*args, **kwargs)
        
        if not start_url:
            raise ValueError("start_url is required. Use: -a start_url=https://example.com")
        
        self.start_urls = [start_url]
        
        # Extract domain from start_url if not provided
        if allowed_domain:
            self.allowed_domains = [allowed_domain]
        else:
            parsed_uri = urlparse(start_url)
            domain = parsed_uri.netloc
            # Remove 'www.' prefix if present
            domain = domain.replace('www.', '')
            self.allowed_domains = [domain]
        
        self.logger.info(f"Starting spider with URL: {start_url}")
        self.logger.info(f"Allowed domains: {self.allowed_domains}")
        
        # Email pattern for extraction
        self.email_pattern = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        )
        
        # Phone pattern for extraction (supports various formats)
        self.phone_pattern = re.compile(
            r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}|\+?\d{10,}'
        )
    
    def parse(self, response):
        """
        Main parsing method. Extracts contacts and follows links.
        """
        self.logger.info(f"Crawling: {response.url}")
        
        # Extract contacts from current page
        yield from self.extract_contacts(response)
        
        # Follow all links on the same domain
        for link in response.css('a::attr(href)').getall():
            # Convert relative URLs to absolute
            absolute_url = urljoin(response.url, link)
            
            # Check if URL is within allowed domains
            parsed = urlparse(absolute_url)
            domain = parsed.netloc.replace('www.', '')
            
            if domain in self.allowed_domains or any(d in domain for d in self.allowed_domains):
                yield response.follow(link, callback=self.parse)
    
    def extract_contacts(self, response):
        """
        Extract contact information from the page.
        This method tries multiple strategies to find contacts.
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
        # Only use if the page looks like a contact/staff/directory page
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
            # Get text before email
            text_parts = text_content.split(contact['email'])[0].split()
            # Take last 2-4 words before email as potential name
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


