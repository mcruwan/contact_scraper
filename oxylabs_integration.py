#!/usr/bin/env python
"""
Oxylabs Web Scraper API Integration for University Contact Scraper

This script integrates Oxylabs API to bypass anti-bot protection
and scrape protected websites like UCSI University.
"""

import requests
import json
import base64
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from uni_scraper.spiders.contact_spider import ContactSpider

# Import AI extraction (optional)
try:
    from ai_extractor import AIContactExtractor
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("⚠️  AI extraction not available (ai_extractor.py not found)")


class OxylabsScraper:
    """
    Oxylabs Web Scraper API integration for bypassing anti-bot protection.
    Now with AI-powered contact extraction!
    """
    
    def __init__(self, username, password, use_ai=True, ai_model="openai/gpt-4o-mini"):
        self.username = username
        self.password = password
        self.base_url = "https://realtime.oxylabs.io/v1/queries"
        self.auth_string = base64.b64encode(f"{username}:{password}".encode()).decode()
        self.headers = {
            "Authorization": f"Basic {self.auth_string}",
            "Content-Type": "application/json"
        }
        
        # Initialize AI extractor
        self.use_ai = use_ai and AI_AVAILABLE
        self.ai_extractor = None
        self.ai_extractions_count = 0
        self.ai_success_count = 0
        
        if self.use_ai:
            try:
                self.ai_extractor = AIContactExtractor(model=ai_model)
                if self.ai_extractor.enabled:
                    print(f"✓ AI-powered extraction enabled with {ai_model}")
                else:
                    self.use_ai = False
                    print("⚠️  AI extraction disabled: No API key configured")
            except Exception as e:
                self.use_ai = False
                print(f"⚠️  AI extraction disabled: {e}")
    
    def scrape_url(self, url, render_js=True, country="us"):
        """
        Scrape a single URL using Oxylabs API with advanced anti-detection.
        
        Args:
            url (str): URL to scrape
            render_js (bool): Whether to render JavaScript
            country (str): Country code for proxy location (random if 'random')
        
        Returns:
            dict: Scraped content and metadata
        """
        import random
        
        # Rotate country locations to avoid detection
        if country == "random" or country is None:
            countries = ['us', 'gb', 'ca', 'au', 'de', 'fr', 'sg', 'jp', 'my', 'nl', 'se']
            country = random.choice(countries)
        
        payload = {
            "source": "universal",
            "url": url,
            "render": "html",
            "geo_location": country,  # Rotates with each request
            "parse": False,
            "render_options": {
                "wait": 1000
            },
            "context": [
                {
                    "key": "page_type",
                    "value": "university_contact"
                }
            ]
        }
        
        # Add session support for cookies/state (optional)
        if hasattr(self, 'use_session') and self.use_session:
            if not hasattr(self, 'session_id'):
                import uuid
                self.session_id = str(uuid.uuid4())
            payload["session_id"] = self.session_id
        
        try:
            print(f"Scraping {url} via Oxylabs...")
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=120  # Increase timeout to 2 minutes
            )
            
            print(f"Oxylabs API Response Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Oxylabs API Response: {json.dumps(result, indent=2)[:500]}...")
                
                if result.get("results") and len(result["results"]) > 0:
                    return result["results"][0]
                else:
                    print(f"No results returned for {url}")
                    return None
            else:
                print(f"Error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def extract_contacts_from_html(self, html_content, source_url):
        """
        Extract contact information from HTML content.
        """
        from bs4 import BeautifulSoup
        import re
        
        # Handle different content formats from Oxylabs
        if isinstance(html_content, dict):
            # If content is a dict, look for HTML in different possible keys
            if 'html' in html_content:
                html_content = html_content['html']
            elif 'content' in html_content:
                html_content = html_content['content']
            elif 'text' in html_content:
                html_content = html_content['text']
            else:
                print(f"Unknown content format: {list(html_content.keys())}")
                return []
        
        # Ensure html_content is a string
        if not isinstance(html_content, str):
            html_content = str(html_content)
        
        print(f"Processing HTML content: {len(html_content)} characters")
        
        # Save raw HTML for inspection in output folder (optional)
        import os
        os.makedirs('output', exist_ok=True)
        
        # Only save raw HTML if explicitly requested
        if hasattr(self, 'save_html') and self.save_html:
            html_file = f"output/raw_html_{time.strftime('%Y%m%d_%H%M%S')}.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"Raw HTML saved to: {html_file}")
        else:
            print("Raw HTML saving disabled (use --save-html to enable)")
        
        soup = BeautifulSoup(html_content, 'html.parser')
        contacts = []
        
        # Email pattern
        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        # Phone pattern
        phone_pattern = re.compile(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}|\+?\d{10,}')
        
        # Look for contact containers (be more specific to avoid navigation menus)
        contact_selectors = [
            '.contact-card', '.contact-info', '.person-card',
            '.staff-member', '.faculty-member', '.team-member', '.profile',
            '.employee', '.directory-entry', '.counselor', '.advisor',
            '.staff-card', '.faculty-card', '.person-profile',
            '[class*="staff-member"]', '[class*="faculty-member"]', 
            '[class*="person-card"]', '[class*="contact-card"]',
            '[class*="team-member"]', '[class*="employee"]'
        ]
        
        for selector in contact_selectors:
            contact_elements = soup.select(selector)
            if contact_elements:
                print(f"Found {len(contact_elements)} contacts using selector: {selector}")
                for element in contact_elements:
                    contact = self.extract_contact_from_element(element, source_url, email_pattern, phone_pattern)
                    if contact and (contact.get('email') or contact.get('phone')):
                        contacts.append(contact)
                break  # If we found contacts with this selector, stop trying others
        
        # If no specific containers found, try contextual extraction
        if not contacts:
            print("Using contextual extraction strategy")
            
            # Find all email links and extract context around them
            import re
            mailto_links = soup.find_all('a', href=re.compile(r'^mailto:', re.I))
            
            if mailto_links:
                print(f"Found {len(mailto_links)} mailto links")
                for mailto_link in mailto_links:
                    email = mailto_link.get('href', '').replace('mailto:', '').strip()
                    if email and '@' in email:
                        # Extract context around the email
                        contact = self.extract_contact_from_context(mailto_link, email, source_url, soup)
                        if contact:
                            contacts.append(contact)
            
            # If no mailto links, try finding emails in text with context
            if not contacts:
                print("Searching for emails in text with context")
                all_text = soup.get_text()
                emails = email_pattern.findall(all_text)
                
                if emails:
                    print(f"Found {len(emails)} email addresses in text")
                    # For each email, try to find context
                    for email in set(emails):  # Use set to avoid duplicates
                        contact = self.find_email_context(soup, email, source_url, email_pattern, phone_pattern)
                        if contact:
                            contacts.append(contact)
        
        return contacts
    
    def extract_contact_from_context(self, email_element, email, source_url, soup):
        """
        ENHANCED: Extract contact details by analyzing context around an email link.
        Uses multiple strategies including AI-powered extraction as fallback.
        """
        import re
        
        contact = {
            'name': None,
            'email': email,
            'phone': None,
            'designation': None,
            'university': None,
            'department': None,
            'source_url': source_url,
            'scraped_date': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Strategy 1: Try to extract from mailto username as fallback
        if email and '@' in email:
            username = email.split('@')[0]
            # Convert firstname.lastname or firstname_lastname to "Firstname Lastname"
            if '.' in username or '_' in username:
                parts = username.replace('_', '.').split('.')
                if len(parts) >= 2 and all(len(p) > 1 and p.replace('-', '').isalpha() for p in parts):
                    fallback_name = ' '.join(p.capitalize() for p in parts)
                    contact['name'] = fallback_name  # Use as fallback, will be overwritten if better name found
        
        # Strategy 2: Check parent containers (up to 3 levels)
        for parent_level in range(3):
            parent = email_element
            for _ in range(parent_level + 1):
                parent = parent.find_parent()
                if not parent:
                    break
            
            if parent:
                # Extract phone numbers
                if not contact['phone']:
                    tel_links = parent.find_all('a', href=re.compile(r'^tel:'))
                    if tel_links:
                        contact['phone'] = tel_links[0]['href'].replace('tel:', '').strip()
                
                # Look for headings (names often in headings)
                for heading_tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    heading = parent.find(heading_tag)
                    if heading:
                        heading_text = heading.get_text(strip=True)
                        if heading_text and self.looks_like_name(heading_text):
                            contact['name'] = heading_text  # Override fallback name
                            break
                
                # Look for tags with name-related classes
                for tag in parent.find_all(['strong', 'b', 'span', 'div', 'p']):
                    tag_classes = ' '.join(tag.get('class', [])).lower()
                    
                    # Check for name-related classes
                    if any(x in tag_classes for x in ['name', 'staff', 'faculty', 'person', 'profile', 'author', 'contact-name']):
                        text = tag.get_text(strip=True)
                        if text and self.looks_like_name(text):
                            contact['name'] = text  # Override fallback name
                    
                    # Check for designation-related classes
                    if any(x in tag_classes for x in ['title', 'position', 'designation', 'role', 'job']):
                        text = tag.get_text(strip=True)
                        if text and self.looks_like_designation(text):
                            contact['designation'] = text
        
        # Strategy 3: AI-powered extraction (if enabled and heuristics found insufficient data)
        if self.use_ai and self.ai_extractor:
            # Use AI if we have email but missing name, or if name looks suspicious
            needs_ai = (
                not contact.get('name') or 
                '@' in (contact.get('name') or '') or
                len(contact.get('name') or '') < 3
            )
            
            if needs_ai:
                try:
                    # Get HTML context (parent with more context)
                    context_element = email_element
                    for _ in range(2):  # Go up 2 levels for better context
                        parent = context_element.find_parent()
                        if parent:
                            context_element = parent
                    
                    html_context = str(context_element)[:4000]  # Limit size
                    
                    # Call AI extraction
                    self.ai_extractions_count += 1
                    ai_result = self.ai_extractor.extract_contact_info(html_context, email)
                    
                    # Use AI results to fill missing fields
                    if ai_result:
                        if ai_result.get('name') and not contact.get('name'):
                            contact['name'] = ai_result['name']
                            self.ai_success_count += 1
                        if ai_result.get('designation') and not contact.get('designation'):
                            contact['designation'] = ai_result['designation']
                        if ai_result.get('phone') and not contact.get('phone'):
                            contact['phone'] = ai_result['phone']
                        if ai_result.get('department') and not contact.get('department'):
                            contact['department'] = ai_result['department']
                        
                        print(f"  ✓ AI extracted: {ai_result.get('name', 'N/A')}")
                    
                except Exception as e:
                    print(f"  ⚠️  AI extraction failed: {e}")
        
        return contact if contact.get('email') else None
    
    def find_email_context(self, soup, email, source_url, email_pattern, phone_pattern):
        """
        ENHANCED: Find context around an email address found in plain text.
        Uses fallback name extraction from email if no name found in context.
        """
        import re
        
        contact = {
            'name': None,
            'email': email,
            'phone': None,
            'designation': None,
            'university': None,
            'department': None,
            'source_url': source_url,
            'scraped_date': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Fallback: Extract name from email username
        if email and '@' in email:
            username = email.split('@')[0]
            if '.' in username or '_' in username:
                parts = username.replace('_', '.').split('.')
                if len(parts) >= 2 and all(len(p) > 1 and p.replace('-', '').isalpha() for p in parts):
                    contact['name'] = ' '.join(p.capitalize() for p in parts)
        
        # Find elements containing this email
        all_text_elements = soup.find_all(text=re.compile(re.escape(email)))
        
        for text_elem in all_text_elements:
            parent = text_elem.find_parent()
            if parent:
                # Look for phone in parent
                if not contact['phone']:
                    tel_links = parent.find_all('a', href=re.compile(r'^tel:'))
                    if tel_links:
                        contact['phone'] = tel_links[0]['href'].replace('tel:', '').strip()
                
                # Check grandparent for better context
                grandparent = parent.find_parent()
                context_element = grandparent if grandparent else parent
                
                # Look for headings
                for heading_tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    heading = context_element.find(heading_tag)
                    if heading:
                        heading_text = heading.get_text(strip=True)
                        if self.looks_like_name(heading_text):
                            contact['name'] = heading_text  # Override fallback
                            break
                
                # Get surrounding text lines
                parent_text = context_element.get_text(separator='\n', strip=True)
                lines = [l.strip() for l in parent_text.split('\n') if l.strip()]
                
                # Find the line with the email
                for i, line in enumerate(lines):
                    if email in line:
                        # Look for name in previous lines (up to 3 lines before)
                        for j in range(max(0, i-3), i):
                            potential_name = lines[j].strip()
                            if potential_name and self.looks_like_name(potential_name):
                                contact['name'] = potential_name  # Override fallback
                                break
                        
                        # Look for designation (current line and next 2 lines)
                        for j in range(i, min(len(lines), i+3)):
                            potential_designation = lines[j].strip()
                            if potential_designation and self.looks_like_designation(potential_designation):
                                contact['designation'] = potential_designation
                                break
                        
                        break
        
        return contact if contact.get('email') else None
    
    def looks_like_name(self, text):
        """
        Check if text looks like a person's name.
        """
        import re
        
        if not text or len(text) < 3 or len(text) > 100:
            return False
        
        # Filter out common non-name patterns
        exclude_keywords = [
            'email', 'phone', 'contact', 'enquiry', 'inquiry', 'general', 'information',
            'click', 'here', 'http', 'www', 'subject', 'message', 'please', 'copyright',
            'university', 'college', 'school', 'department', 'faculty', 'office'
        ]
        
        text_lower = text.lower()
        if any(keyword in text_lower for keyword in exclude_keywords):
            return False
        
        # Check for common title patterns
        title_patterns = [
            r'^(Dr\.?|Prof\.?|Professor|Mr\.?|Mrs\.?|Ms\.?|Miss)\s+[A-Z]',
            r'^[A-Z][a-z]+\s+[A-Z]',  # First Last
            r'^[A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z]',  # First Middle Last
        ]
        
        for pattern in title_patterns:
            if re.match(pattern, text):
                return True
        
        # Check if it has title case and reasonable word count
        words = text.split()
        if 2 <= len(words) <= 5:
            # Check if most words start with capital letter
            capitalized = sum(1 for word in words if word and word[0].isupper())
            if capitalized >= len(words) * 0.5:
                return True
        
        return False
    
    def looks_like_designation(self, text):
        """
        Check if text looks like a job designation/title.
        """
        if not text or len(text) < 5 or len(text) > 150:
            return False
        
        designation_keywords = [
            'professor', 'lecturer', 'dean', 'head', 'director', 'manager', 'coordinator',
            'senior', 'junior', 'associate', 'assistant', 'officer', 'executive',
            'lead', 'leader', 'chief', 'specialist', 'consultant', 'advisor', 'counselor',
            'program', 'programme', 'faculty', 'department', 'academic', 'research'
        ]
        
        text_lower = text.lower()
        if any(keyword in text_lower for keyword in designation_keywords):
            return True
        
        return False
    
    def extract_contact_from_element(self, element, source_url, email_pattern, phone_pattern):
        """
        Extract contact information from a specific element.
        """
        import re
        
        contact = {
            'name': None,
            'email': None,
            'phone': None,
            'designation': None,
            'university': None,
            'department': None,
            'source_url': source_url,
            'scraped_date': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Get all text from the element
        text_content = element.get_text()
        
        # Extract email
        emails = email_pattern.findall(text_content)
        contact['email'] = emails[0] if emails else None
        
        # Also check for mailto links
        if not contact['email']:
            mailto_links = element.find_all('a', href=re.compile(r'^mailto:'))
            if mailto_links:
                contact['email'] = mailto_links[0]['href'].replace('mailto:', '').strip()
        
        # Extract phone
        phones = phone_pattern.findall(text_content)
        contact['phone'] = ''.join(phones[0]) if phones else None
        
        # Also check for tel links
        if not contact['phone']:
            tel_links = element.find_all('a', href=re.compile(r'^tel:'))
            if tel_links:
                contact['phone'] = tel_links[0]['href'].replace('tel:', '').strip()
        
        # Extract name (try various selectors)
        name_selectors = [
            '.name', '.person-name', 'h1', 'h2', 'h3', 'h4', 
            '.title', '[class*="name"]', 'strong', 'b'
        ]
        for selector in name_selectors:
            name_elem = element.select_one(selector)
            if name_elem and name_elem.get_text().strip():
                contact['name'] = name_elem.get_text().strip()
                break
        
        # Extract designation
        designation_selectors = [
            '.designation', '.title', '.position', '.job-title',
            '[class*="designation"]', '[class*="position"]', '[class*="role"]'
        ]
        for selector in designation_selectors:
            designation_elem = element.select_one(selector)
            if designation_elem and designation_elem.get_text().strip():
                contact['designation'] = designation_elem.get_text().strip()
                break
        
        # Extract university
        university_selectors = [
            '.university', '.institution', '.organization',
            '[class*="university"]', '[class*="institution"]'
        ]
        for selector in university_selectors:
            university_elem = element.select_one(selector)
            if university_elem and university_elem.get_text().strip():
                contact['university'] = university_elem.get_text().strip()
                break
        
        # Extract department
        department_selectors = [
            '.department', '.dept', '[class*="department"]'
        ]
        for selector in department_selectors:
            department_elem = element.select_one(selector)
            if department_elem and department_elem.get_text().strip():
                contact['department'] = department_elem.get_text().strip()
                break
        
        return contact
    
    def scrape_single_url(self, url, index, total):
        """
        Scrape a single URL (used for parallel processing) with rotating IPs.
        """
        print(f"[{index}/{total}] Scraping: {url}")
        
        # Use random country to rotate IP/location for each request
        result = self.scrape_url(url, country="random")
        if result and result.get('content'):
            contacts = self.extract_contacts_from_html(result['content'], url)
            print(f"[{index}/{total}] + Found {len(contacts)} contacts")
            return contacts
        else:
            print(f"[{index}/{total}] - Failed")
            return []
    
    def scrape_multiple_urls(self, urls, output_file="oxylabs_contacts.json", max_workers=20):
        """
        Scrape multiple URLs in parallel and save results.
        Oxylabs allows 40 requests/second, so using 20-30 parallel workers is safe.
        """
        all_contacts = []
        total_urls = len(urls)
        
        print(f"\n{'='*70}")
        print(f"Starting parallel scraping with {max_workers} workers")
        print(f"Processing {total_urls} URLs (up to {max_workers} at a time)")
        print(f"{'='*70}")
        
        start_time = time.time()
        
        # Use ThreadPoolExecutor for parallel requests
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_url = {
                executor.submit(self.scrape_single_url, url, i+1, total_urls): url 
                for i, url in enumerate(urls)
            }
            
            # Collect results as they complete
            completed = 0
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    contacts = future.result()
                    all_contacts.extend(contacts)
                    completed += 1
                except Exception as e:
                    print(f"Error processing {url}: {e}")
                    completed += 1
        
        elapsed_time = time.time() - start_time
        print(f"\n{'='*70}")
        print(f"Scraping completed in {elapsed_time:.2f} seconds")
        print(f"Average: {elapsed_time/total_urls:.2f} seconds per URL")
        
        # Show AI extraction statistics with actual usage
        if self.use_ai and self.ai_extractions_count > 0:
            print(f"\n{'='*70}")
            print(f"AI EXTRACTION STATISTICS")
            print(f"{'='*70}")
            print(f"  Model: {self.ai_extractor.model}")
            print(f"  Total AI calls: {self.ai_extractions_count}")
            print(f"  Successful extractions: {self.ai_success_count}")
            print(f"  Success rate: {(self.ai_success_count/self.ai_extractions_count*100):.1f}%")
            
            # Get actual usage stats from AI extractor
            if self.ai_extractor:
                usage_stats = self.ai_extractor.get_usage_stats()
                print(f"\nToken Usage:")
                print(f"  Input tokens: {usage_stats['input_tokens']:,}")
                print(f"  Output tokens: {usage_stats['output_tokens']:,}")
                print(f"  Total tokens: {usage_stats['total_tokens']:,}")
                print(f"  Avg tokens/request: {usage_stats['avg_tokens_per_request']:.1f}")
                print(f"\nActual Cost: ${usage_stats['total_cost']:.6f}")
                print(f"  (≈ ${usage_stats['total_cost']*1000:.3f} per 1000 extractions)")
            
            print(f"{'='*70}")
        
        print(f"{'='*70}")
        
        # Phase 1: Save raw data to JSON (with duplicates)
        import os
        os.makedirs('output', exist_ok=True)
        timestamp = time.strftime('%Y-%m-%dT%H-%M-%S+00-00')
        
        # Save raw JSON data first
        json_file = f"output/raw_contacts_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(all_contacts, f, indent=2, ensure_ascii=False)
        
        print(f"\n=== SCRAPING COMPLETE ===")
        print(f"Total contacts found: {len(all_contacts)}")
        print(f"Raw data saved to: {json_file}")
        
        # Phase 2: Clean data and create CSV
        if all_contacts:
            print("Cleaning data and removing duplicates...")
            unique_contacts = clean_and_deduplicate_contacts(all_contacts)
            
            # Save clean CSV
            csv_file = f"output/contacts_{timestamp}.csv"
            import csv
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=unique_contacts[0].keys())
                writer.writeheader()
                writer.writerows(unique_contacts)
            
            print(f"Unique contacts: {len(unique_contacts)}")
            print(f"Duplicates removed: {len(all_contacts) - len(unique_contacts)}")
            print(f"Clean CSV saved to: {csv_file}")
        else:
            print("No contacts found to clean.")
        
        return all_contacts


def clean_and_deduplicate_contacts(contacts):
    """
    Clean and remove duplicates from contact data.
    """
    unique_contacts = []
    seen_emails = set()
    
    for contact in contacts:
        # Clean the contact data
        cleaned_contact = clean_contact_data(contact)
        
        # Only deduplicate based on email (not source URL)
        email = cleaned_contact.get('email', '')
        
        if email and email not in seen_emails:
            seen_emails.add(email)
            unique_contacts.append(cleaned_contact)
    
    return unique_contacts


def clean_contact_data(contact):
    """
    Clean individual contact data.
    """
    cleaned = {}
    
    # Clean email
    email = contact.get('email')
    if email and isinstance(email, str) and '@' in email:
        email = email.strip()
        # Remove any extra text before email
        email_parts = email.split('@')
        if len(email_parts) == 2:
            cleaned['email'] = email_parts[0].strip() + '@' + email_parts[1].strip()
        else:
            cleaned['email'] = email
    else:
        cleaned['email'] = None
    
    # Clean phone
    phone = contact.get('phone')
    if phone and isinstance(phone, str):
        phone = phone.strip()
        if phone and len(phone) >= 7 and not phone.isdigit():
            cleaned['phone'] = phone
        else:
            cleaned['phone'] = None
    else:
        cleaned['phone'] = None
    
    # Clean name
    name = contact.get('name')
    if name and isinstance(name, str):
        name = name.strip()
        if name and len(name) > 2:
            cleaned['name'] = name
        else:
            cleaned['name'] = None
    else:
        cleaned['name'] = None
    
    # Clean designation
    designation = contact.get('designation')
    if designation and isinstance(designation, str):
        designation = designation.strip()
        if designation and len(designation) > 2:
            cleaned['designation'] = designation
        else:
            cleaned['designation'] = None
    else:
        cleaned['designation'] = None
    
    # Clean university
    university = contact.get('university')
    if university and isinstance(university, str):
        university = university.strip()
        if university and len(university) > 2:
            cleaned['university'] = university
        else:
            cleaned['university'] = None
    else:
        cleaned['university'] = None
    
    # Clean department
    department = contact.get('department')
    if department and isinstance(department, str):
        department = department.strip()
        if department and len(department) > 2:
            cleaned['department'] = department
        else:
            cleaned['department'] = None
    else:
        cleaned['department'] = None
    
    # Keep source URL and date as is
    cleaned['source_url'] = contact.get('source_url', '')
    cleaned['scraped_date'] = contact.get('scraped_date', '')
    
    return cleaned


def discover_urls_via_sitemap(start_url, base_domain, headers, base_url):
    """
    Try to discover URLs via sitemap.xml - most comprehensive method.
    """
    from urllib.parse import urljoin
    import requests
    from bs4 import BeautifulSoup
    
    sitemap_urls = []
    sitemap_locations = [
        "/sitemap.xml",
        "/sitemap_index.xml",
        "/sitemaps/sitemap.xml",
        "/sitemap/sitemap.xml"
    ]
    
    print("Checking for sitemaps...")
    
    for sitemap_path in sitemap_locations:
        sitemap_url = f"https://{base_domain}{sitemap_path}"
        try:
            # Use Oxylabs to fetch sitemap
            payload = {
                "source": "universal",
                "url": sitemap_url,
                "render": "html",
                "geo_location": "my",
                "parse": False
            }
            
            response = requests.post(base_url, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("results") and len(result["results"]) > 0:
                    content = result["results"][0].get('content', '')
                    
                    if isinstance(content, str) and 'xml' in content.lower()[:100]:
                        # Try to extract XML from HTML wrapper
                        if '<sitemap' in content.lower() or '<urlset' in content.lower():
                            # Find the actual XML content within HTML
                            import re
                            xml_match = re.search(r'<(sitemap|urlset)[^>]*>.*?</\1>', content, re.DOTALL | re.IGNORECASE)
                            if xml_match:
                                xml_content = xml_match.group(0)
                            else:
                                xml_content = content
                        else:
                            xml_content = content
                        
                        # Parse XML sitemap
                        soup = BeautifulSoup(xml_content, 'xml')
                        
                        # Extract URLs from <loc> tags
                        for loc in soup.find_all('loc'):
                            url = loc.get_text().strip()
                            if url:
                                sitemap_urls.append(url)
                        
                        if sitemap_urls:
                            print(f"  + Found sitemap at {sitemap_url}")
                            print(f"  + Extracted {len(sitemap_urls)} URLs from sitemap")
                            return sitemap_urls
                        else:
                            # Try parsing as HTML table (some sites render sitemaps as HTML tables)
                            all_tags = [tag.name for tag in soup.find_all()]
                            if 'table' in all_tags and 'td' in all_tags:
                                # Look for URLs in table cells
                                for td in soup.find_all('td'):
                                    text = td.get_text().strip()
                                    if text and ('http' in text or text.startswith('/')):
                                        if text.startswith('http'):
                                            sitemap_urls.append(text)
                                        elif text.startswith('/'):
                                            sitemap_urls.append(f"https://{base_domain}{text}")
                                
                                if sitemap_urls:
                                    print(f"  + Found sitemap at {sitemap_url} (HTML table format)")
                                    print(f"  + Extracted {len(sitemap_urls)} URLs from sitemap table")
                                    return sitemap_urls
        except Exception as e:
            continue
    
    print("  - No sitemap found")
    return []


def discover_urls_by_patterns(start_url, base_domain, discovered_urls):
    """
    Generate potential staff/faculty directory URLs without making API calls.
    These will be added to the crawl queue for verification during normal crawling.
    """
    print("\nGenerating staff/faculty directory patterns...")
    
    # Common patterns for staff directories and contact pages (most likely to exist)
    patterns = [
        # Contact pages (HIGHEST PRIORITY)
        "/contact",
        "/contact-us",
        "/contactus",
        "/contacts",
        "/get-in-touch",
        "/reach-us",
        
        # Staff directories
        "/staff",
        "/staff-directory",
        "/faculty",
        "/faculty-directory",
        "/people",
        "/team",
        "/directory",
        "/our-staff",
        "/our-faculty",
        "/about/staff",
        "/about/faculty",
        
        # Additional contact-related patterns
        "/about/contact",
        "/about/contacts",
        "/support",
        "/help"
    ]
    
    pattern_urls = []
    
    for pattern in patterns:
        test_url = f"https://{base_domain}{pattern}"
        
        if test_url not in discovered_urls:
            pattern_urls.append(test_url)
    
    print(f"  Generated {len(pattern_urls)} potential staff directory URLs")
    print(f"  (Will be validated during crawling)")
    return pattern_urls


def discover_urls(start_url, max_pages=20, max_discovery=2000, enable_deep_crawl=False, deep_crawl_requests=50, enable_ai_url_filter=False, ai_extractor=None):
    """
    Enhanced URL discovery with multiple methods:
    1. Sitemap.xml discovery (most comprehensive)
    2. Pattern-based discovery (staff/faculty directories)
    3. Deep crawling (OPTIONAL - controlled by enable_deep_crawl parameter)
    4. AI URL prioritization (OPTIONAL - uses AI to filter likely contact pages)
    
    Phase 1: Discover ALL URLs up to max_discovery limit
    Phase 2: Prioritize and return top max_pages URLs
    Phase 3: AI filtering (optional) - Analyze medium-confidence URLs
    
    Args:
        start_url: The starting URL to discover from
        max_pages: Maximum number of pages to discover
        max_discovery: Maximum total URLs to discover (default: 2000)
        enable_deep_crawl: Whether to enable deep crawling (default: False)
        deep_crawl_requests: Number of API requests for deep crawling (default: 50)
        enable_ai_url_filter: Whether to use AI to prioritize URLs (default: False)
        ai_extractor: Optional AIContactExtractor instance (for shared stats tracking)
    """
    from urllib.parse import urljoin, urlparse
    import requests
    import base64
    from bs4 import BeautifulSoup
    import time
    
    # Oxylabs credentials
    username = "mcruwan_6Grof"
    password = "NewAdmin_123"
    
    # API configuration
    base_url = "https://realtime.oxylabs.io/v1/queries"
    auth_string = base64.b64encode(f"{username}:{password}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth_string}",
        "Content-Type": "application/json"
    }
    
    discovered_urls = set([start_url])
    urls_to_process = [start_url]
    processed_urls = set()
    base_domain = urlparse(start_url).netloc
    
    print(f"\n{'='*70}")
    print(f"PHASE 1: ENHANCED URL DISCOVERY")
    print(f"{'='*70}")
    print(f"Starting URL: {start_url}")
    print(f"Base domain: {base_domain}")
    print(f"Max URLs to discover: {max_discovery}")
    print(f"Target pages to scrape: {max_pages}")
    print(f"{'='*70}\n")
    
    # Method 1: Sitemap discovery (ENABLED for all scrapes - fast and comprehensive)
    print("=" * 70)
    print("METHOD 1: SITEMAP DISCOVERY")
    print("=" * 70)
    try:
        sitemap_urls = discover_urls_via_sitemap(start_url, base_domain, headers, base_url)
        if sitemap_urls:
            # Filter sitemap URLs to same domain and limit for small scrapes
            added_count = 0
            for url in sitemap_urls:
                parsed = urlparse(url)
                if parsed.netloc == base_domain:
                    discovered_urls.add(url)
                    urls_to_process.append(url)
                    added_count += 1
                    
                    # Limit sitemap URLs for small scrapes to avoid overwhelming
                    if max_pages <= 50 and added_count >= max_pages * 3:
                        print(f"Limited sitemap results to {added_count} URLs for fast processing")
                        break
                        
            print(f"Added {added_count} URLs from sitemap\n")
        else:
            print("No sitemap found or sitemap empty\n")
    except Exception as e:
        print(f"Sitemap discovery failed: {e}")
        print("Continuing without sitemap...\n")
    
    # Method 2: Pattern-based discovery (FAST - no API calls)
    print("=" * 70)
    print("METHOD 2: PATTERN-BASED DISCOVERY")
    print("=" * 70)
    pattern_urls = discover_urls_by_patterns(start_url, base_domain, discovered_urls)
    for url in pattern_urls:
        if url not in discovered_urls:
            discovered_urls.add(url)
            urls_to_process.insert(0, url)  # Add to front for priority
    print()
    
    # Method 3: Deep crawling (OPTIONAL - controlled by parameter)
    print("=" * 70)
    print("METHOD 3: DEEP CRAWLING")
    print("=" * 70)
    
    # Check if deep crawling is enabled via parameter
    if not enable_deep_crawl:
        print("Deep crawling DISABLED (use --deep-crawl to enable)")
        print(f"Using {len(discovered_urls)} URLs from sitemap and patterns")
        print("(Add --deep-crawl=N to discover more URLs via API calls)\n")
        max_discovery_requests = 0  # Skip discovery entirely
    else:
        max_discovery_requests = min(deep_crawl_requests, 100)  # Cap at 100 for safety
        print(f"Deep crawling ENABLED: {max_discovery_requests} API requests")
        print(f"Current URLs discovered: {len(discovered_urls)}")
    
    discovery_count = 0
    
    # Prioritize staff/faculty directory URLs in processing queue
    staff_keywords = ['staff', 'faculty', 'directory', 'people', 'team', 'professor', 'lecturer', 'academic']
    
    def is_staff_url(url):
        """Check if URL is likely a staff/faculty page"""
        url_lower = url.lower()
        return any(keyword in url_lower for keyword in staff_keywords)
    
    # Separate high-priority URLs (staff directories) from others
    priority_queue = [url for url in urls_to_process if is_staff_url(url)]
    regular_queue = [url for url in urls_to_process if not is_staff_url(url)]
    urls_to_process = priority_queue + regular_queue
    
    if max_discovery_requests > 0:
        print(f"Priority URLs (staff/faculty): {len(priority_queue)}")
        print(f"Regular URLs: {len(regular_queue)}")
        print(f"Starting discovery...\n")
    
    while urls_to_process and len(discovered_urls) < max_discovery and discovery_count < max_discovery_requests and max_discovery_requests > 0:
        current_url = urls_to_process.pop(0)
        
        if current_url in processed_urls:
            continue
            
        processed_urls.add(current_url)
        discovery_count += 1
        
        # Show if this is a priority URL
        is_priority = is_staff_url(current_url)
        priority_marker = "[PRIORITY] " if is_priority else ""
        print(f"{priority_marker}[{discovery_count}/{max_discovery_requests}] Discovering: {current_url[:80]}...")
        
        try:
            # Use Oxylabs to get the page
            payload = {
                "source": "universal",
                "url": current_url,
                "render": "html",
                "geo_location": "my",
                "parse": False,
                "render_options": {
                    "wait": 500  # Reduced wait for faster discovery
                }
            }
            
            response = requests.post(base_url, headers=headers, json=payload, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("results") and len(result["results"]) > 0:
                    content_data = result["results"][0]
                    content = content_data.get('content', {})
                    
                    if isinstance(content, str) and len(content) > 100:
                        # Parse HTML to find links
                        soup = BeautifulSoup(content, 'html.parser')
                        
                        new_urls_found = 0
                        
                        # Find all links
                        for link in soup.find_all('a', href=True):
                            href = link['href']
                            full_url = urljoin(current_url, href)
                            
                            # Clean URL (keep query parameters for staff profiles)
                            parsed_url = urlparse(full_url)
                            clean_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
                            if parsed_url.query:
                                clean_url += f"?{parsed_url.query}"
                            
                            # Check if it's a valid URL from the same domain
                            if (parsed_url.netloc == base_domain and 
                                clean_url not in discovered_urls and
                                not any(ext in clean_url.lower() for ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.rar', '.jpg', '.png', '.gif', '.css', '.js', '.svg', '.ico']) and
                                not clean_url.startswith('mailto:') and
                                not clean_url.startswith('tel:') and
                                not clean_url.endswith('#')):  # Skip fragment-only URLs
                                
                                discovered_urls.add(clean_url)
                                
                                # Prioritize staff URLs by adding them to front of queue
                                if is_staff_url(clean_url):
                                    urls_to_process.insert(0, clean_url)  # Add to front
                                    new_urls_found += 1
                                else:
                                    urls_to_process.append(clean_url)  # Add to back
                        
                        if new_urls_found > 0:
                            print(f"   > Found {new_urls_found} priority URLs | Total: {len(discovered_urls)}")
                        else:
                            print(f"   > Total URLs discovered: {len(discovered_urls)}")
                    else:
                        print(f"   > No content")
                else:
                    print(f"   > No results")
            else:
                print(f"   > Error {response.status_code}")
                
        except Exception as e:
            print(f"   > Error: {e}")
        
        # Adaptive delay: shorter for priority URLs
        time.sleep(0.5 if is_priority else 1)
    
    print(f"\n{'='*70}")
    print(f"Discovery complete! Found {len(discovered_urls)} total URLs")
    print(f"{'='*70}\n")
    
    # Phase 2: Prioritize URLs based on keywords
    print(f"PHASE 2: URL PRIORITIZATION")
    print(f"{'='*70}")
    
    # Expanded keywords for contact pages (with priority scores)
    keyword_scores = {
        # Highest priority (score: 120) - Individual staff profiles
        'professor': 120, 'lecturer': 120, 'dr-': 120, 'prof-': 120,
        'associate-professor': 120, 'assistant-professor': 120,
        
        # High priority (score: 100) - Directories
        'contact': 100, 'contacts': 100, 'contact-us': 100, 'contactus': 100,
        'directory': 100, 'staff-directory': 100, 'faculty-directory': 100,
        'people-directory': 100,
        
        # Medium-high priority (score: 80) - Staff/Faculty pages
        'staff': 80, 'faculty': 80, 'team': 80, 'people': 80,
        'employee': 80, 'personnel': 80, 'academic-staff': 80,
        'faculty-members': 80, 'teaching-staff': 80, 'research-staff': 80,
        
        # Medium priority (score: 60) - Departments/Units
        'about': 60, 'about-us': 60, 'aboutus': 60,
        'department': 60, 'departments': 60, 'school': 60,
        'administration': 60, 'management': 60, 'leadership': 60,
        'dean': 60, 'head': 60, 'director': 60, 'institute': 60,
        
        # Low-medium priority (score: 40) - Support/Services
        'office': 40, 'offices': 40, 'support': 40,
        'service': 40, 'help': 40, 'enquiry': 40,
        'enquiries': 40, 'inquiry': 40, 'advisor': 40,
        'counselor': 40, 'counsellor': 40,
        
        # Low priority (score: 20) - Profiles/Bios
        'profile': 20, 'bio': 20, 'biography': 20,
        'member': 20, 'research': 20, 'academic': 20
    }
    
    # Score each URL
    url_scores = []
    for url in discovered_urls:
        url_lower = url.lower()
        score = 0
        matched_keywords = []
        
        for keyword, keyword_score in keyword_scores.items():
            if keyword in url_lower:
                score += keyword_score
                matched_keywords.append(keyword)
        
        url_scores.append({
            'url': url,
            'score': score,
            'keywords': matched_keywords
        })
    
    # Sort by score (highest first)
    url_scores.sort(key=lambda x: x['score'], reverse=True)
    
    # Separate high-priority and other URLs
    high_priority = [item for item in url_scores if item['score'] >= 60]
    medium_priority = [item for item in url_scores if 20 <= item['score'] < 60]
    low_priority = [item for item in url_scores if 0 < item['score'] < 20]
    no_priority = [item for item in url_scores if item['score'] == 0]
    
    print(f"High priority URLs (score >= 60): {len(high_priority)}")
    print(f"Medium priority URLs (20-59): {len(medium_priority)}")
    print(f"Low priority URLs (1-19): {len(low_priority)}")
    print(f"No keywords found: {len(no_priority)}")
    print(f"{'='*70}\n")
    
    # Show top prioritized URLs
    if high_priority:
        print("Top 10 prioritized URLs:")
        for i, item in enumerate(high_priority[:10], 1):
            keywords_str = ', '.join(item['keywords'][:3])
            print(f"  {i}. [Score: {item['score']}] {item['url']}")
            print(f"     Keywords: {keywords_str}")
        print()
    
    # Combine all URLs in priority order
    prioritized_urls = (
        [item['url'] for item in high_priority] +
        [item['url'] for item in medium_priority] +
        [item['url'] for item in low_priority] +
        [item['url'] for item in no_priority]
    )
    
    # Phase 3: AI URL Filtering (Optional - Smart prioritization)
    if enable_ai_url_filter:
        print(f"\n{'='*70}")
        print(f"PHASE 3: AI URL PRIORITIZATION (SMART FILTER)")
        print(f"{'='*70}")
        
        try:
            from ai_extractor import AIContactExtractor
            
            # Use provided AI extractor or create new one
            if ai_extractor is None:
                ai_extractor = AIContactExtractor()
                print("  (Using new AI extractor instance)")
            
            if ai_extractor.enabled:
                # Analyze uncertain URLs (medium + low + no priority)
                uncertain_urls = (
                    [item for item in medium_priority] +
                    [item for item in low_priority] +
                    [item for item in no_priority]
                )
                
                if uncertain_urls:
                    print(f"Analyzing {len(uncertain_urls)} medium/low confidence URLs with AI...")
                    print(f"(High-confidence URLs with score >= 60 skip AI analysis)")
                    
                    # Get just the URLs
                    urls_to_analyze = [item['url'] for item in uncertain_urls]
                    
                    # AI batch analysis
                    ai_results = ai_extractor.analyze_urls_for_contacts(urls_to_analyze)
                    
                    if ai_results:
                        print(f"✓ AI analyzed {len(ai_results)} URLs")
                        
                        # Update scores based on AI predictions
                        ai_scores_map = {r['url']: r for r in ai_results}
                        
                        upgraded_urls = []
                        downgraded_urls = []
                        
                        for item in uncertain_urls:
                            url = item['url']
                            if url in ai_scores_map:
                                ai_score = ai_scores_map[url]
                                ai_likelihood = ai_score.get('likelihood', 0)
                                
                                # Convert AI likelihood (0-1) to score (0-100) and boost
                                ai_boost = int(ai_likelihood * 100)
                                old_score = item['score']
                                item['score'] = max(old_score, ai_boost)  # Take higher score
                                item['ai_likelihood'] = ai_likelihood
                                item['ai_reason'] = ai_score.get('reason', '')
                                
                                # Track significant changes
                                if ai_likelihood >= 0.7 and old_score < 60:
                                    upgraded_urls.append(f"{url[:60]}... (AI: {ai_likelihood:.2f})")
                                elif ai_likelihood < 0.3 and old_score >= 40:
                                    downgraded_urls.append(f"{url[:60]}... (AI: {ai_likelihood:.2f})")
                        
                        # Re-sort all URLs by updated scores
                        all_items = high_priority + uncertain_urls
                        all_items.sort(key=lambda x: x['score'], reverse=True)
                        
                        # Show AI filtering results
                        print(f"\nAI Filtering Results:")
                        print(f"  ↑ Upgraded: {len(upgraded_urls)} URLs")
                        print(f"  ↓ Downgraded: {len(downgraded_urls)} URLs")
                        
                        if upgraded_urls:
                            print(f"\n  Top upgraded URLs:")
                            for url in upgraded_urls[:3]:
                                print(f"    {url}")
                        
                        # Update prioritized_urls with re-sorted list
                        prioritized_urls = [item['url'] for item in all_items]
                        
                        # Show AI cost
                        usage = ai_extractor.get_usage_stats()
                        url_analysis_cost = usage['url_analysis']['cost']
                        print(f"\n  AI URL Analysis Cost: ${url_analysis_cost:.6f}")
                        print(f"  Tokens used: {usage['url_analysis']['tokens']:,}")
                        
                    else:
                        print("  ⚠️  AI analysis returned no results, using keyword scores")
                else:
                    print("No uncertain URLs to analyze (all are high-confidence)")
            else:
                print("⚠️  AI extraction not available, using keyword-based prioritization only")
                
        except Exception as e:
            print(f"⚠️  AI URL filtering failed: {e}")
            print("Continuing with keyword-based prioritization...")
        
        print(f"{'='*70}\n")
    
    # Return top max_pages URLs
    final_urls = prioritized_urls[:max_pages]
    
    print(f"Returning top {len(final_urls)} URLs for scraping from {len(prioritized_urls)} discovered.")
    if enable_ai_url_filter:
        print(f"  (AI-enhanced prioritization applied)")
    else:
        print(f"  (Keyword-based prioritization only)")
    print(f"{'='*70}\n")
    
    return final_urls, len(prioritized_urls)


def main():
    """
    Main function to run Oxylabs scraping.
    Automatically discovers and crawls all pages within the given domain.
    """
    import sys
    from urllib.parse import urljoin, urlparse
    import time
    
    # Check if URL is provided as command line argument
    if len(sys.argv) < 2:
        print("Usage: python oxylabs_integration.py <WEBSITE_URL> [max_pages] [OPTIONS]")
        print("\nExamples:")
        print("  python oxylabs_integration.py https://sunwayuniversity.edu.my/")
        print("  python oxylabs_integration.py https://sunwayuniversity.edu.my/ 50")
        print("  python oxylabs_integration.py https://sunwayuniversity.edu.my/ 100 --workers=30")
        print("  python oxylabs_integration.py https://sunwayuniversity.edu.my/ 200 --deep-crawl=50")
        print("  python oxylabs_integration.py https://example.com/contact 1 --direct")
        print("\nThe scraper will automatically discover and crawl all pages within the domain.")
        print("Output: CSV file saved to output/contacts_TIMESTAMP.csv")
        print("\nOptions:")
        print("  --save-html       Save raw HTML for debugging")
        print("  --workers=N       Number of parallel workers (default: 20, max: 30)")
        print("  --deep-crawl[=N]  Enable deep crawling with N API requests (default: 50)")
        print("  --direct          Skip URL discovery, scrape the provided URL directly")
        print("  --use-ai          Enable AI-powered name extraction (requires OpenRouter API key)")
        print("  --no-ai           Disable AI extraction (use only heuristics)")
        print("  --ai-model=MODEL  AI model to use (default: openai/gpt-4o-mini)")
        print("  --ai-url-filter   Enable AI URL prioritization (smart filtering)")
        print("  --no-url-filter   Disable AI URL filtering (keyword-based only)")
        print("\nAI Models:")
        print("  openai/gpt-4o-mini              Fast, cheap, accurate (recommended)")
        print("  anthropic/claude-3-haiku        Good for complex text")
        print("  meta-llama/llama-3.1-8b-instruct Free tier available")
        print("  google/gemini-flash-1.5         Fast and free")
        print("\nNotes:")
        print("  - Sitemap & pattern discovery: ALWAYS enabled (fast, no API cost)")
        print("  - Deep crawling: OPTIONAL (uses API calls, finds hidden pages)")
        print("  - AI extraction: Uses OpenRouter API (set OPENROUTER_API_KEY env var)")
        print("  - Your Oxylabs plan supports 40 requests/second")
        sys.exit(1)
    
    # Get URL from command line
    target_url = sys.argv[1]
    max_pages = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 20
    save_html = '--save-html' in sys.argv
    skip_discovery = '--direct' in sys.argv
    
    # Parse AI arguments
    use_ai = True  # Default: enabled if API key is available
    if '--no-ai' in sys.argv:
        use_ai = False
    elif '--use-ai' in sys.argv:
        use_ai = True
    
    # Parse AI URL filter arguments
    enable_ai_url_filter = False  # Default: disabled (opt-in feature)
    if '--ai-url-filter' in sys.argv:
        enable_ai_url_filter = True
    elif '--no-url-filter' in sys.argv:
        enable_ai_url_filter = False
    
    ai_model = "openai/gpt-4o-mini"  # Default model
    for arg in sys.argv:
        if arg.startswith('--ai-model='):
            ai_model = arg.split('=', 1)[1]
    
    # Parse workers argument
    max_workers = 20  # Default (safe for 40 req/s)
    for arg in sys.argv:
        if arg.startswith('--workers='):
            try:
                max_workers = int(arg.split('=')[1])
                max_workers = min(max_workers, 30)  # Cap at 30 to stay under 40 req/s limit
            except:
                pass
    
    # Parse deep-crawl argument
    enable_deep_crawl = False
    deep_crawl_requests = 50  # Default
    for arg in sys.argv:
        if arg == '--deep-crawl':
            enable_deep_crawl = True
        elif arg.startswith('--deep-crawl='):
            enable_deep_crawl = True
            try:
                deep_crawl_requests = int(arg.split('=')[1])
                deep_crawl_requests = max(1, min(deep_crawl_requests, 100))  # Cap between 1-100
            except:
                pass
    
    # Oxylabs credentials
    username = "mcruwan_6Grof"
    password = "NewAdmin_123"
    
    # Initialize Oxylabs scraper with AI support
    scraper = OxylabsScraper(username, password, use_ai=use_ai, ai_model=ai_model)
    scraper.save_html = save_html  # Pass the save_html flag
    
    # Decide whether to discover URLs or scrape directly
    if skip_discovery:
        print(f"\n{'='*70}")
        print("DIRECT SCRAPING MODE (No URL Discovery)")
        print(f"{'='*70}")
        print(f"Target URL: {target_url}")
        print(f"{'='*70}\n")
        urls_to_scrape = [target_url]
    else:
        # Discover URLs to scrape from the main site
        print(f"Discovering URLs from: {target_url}")
        urls_to_scrape, total_discovered = discover_urls(
            target_url, 
            max_pages, 
            enable_deep_crawl=enable_deep_crawl, 
            deep_crawl_requests=deep_crawl_requests,
            enable_ai_url_filter=enable_ai_url_filter
        )
        print(f"Found {len(urls_to_scrape)} URLs to scrape from {total_discovered} discovered.")
    
    print("=" * 70)
    print("Oxylabs Web Scraper API Integration - Full Site Crawl")
    print("=" * 70)
    print(f"Username: {username}")
    print(f"Starting URL: {target_url}")
    print(f"Max pages: {max_pages}")
    print(f"URLs to scrape: {len(urls_to_scrape)}")
    print(f"Parallel workers: {max_workers}")
    print(f"Deep crawling: {'ENABLED (' + str(deep_crawl_requests) + ' requests)' if enable_deep_crawl else 'DISABLED'}")
    print(f"AI URL Filter: {'ENABLED' if enable_ai_url_filter else 'DISABLED'}")
    print(f"IP Rotation: ENABLED (random country per request)")
    print(f"AI Extraction: {'ENABLED (' + ai_model + ')' if scraper.use_ai else 'DISABLED'}")
    print("=" * 70)
    
    # Start scraping
    contacts = scraper.scrape_multiple_urls(urls_to_scrape, max_workers=max_workers)
    
    # Display sample results
    if contacts:
        print("\n=== SAMPLE RESULTS ===")
        for i, contact in enumerate(contacts[:3], 1):
            print(f"\nContact {i}:")
            for key, value in contact.items():
                if value:
                    print(f"  {key}: {value}")
    else:
        print("\nNo contacts found. The website might still be blocking requests.")
        print("Try different URLs or check your Oxylabs account status.")


if __name__ == "__main__":
    main()
