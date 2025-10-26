# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import re
from datetime import datetime
from itemadapter import ItemAdapter


class DataCleaningPipeline:
    """
    Pipeline for cleaning and validating scraped data.
    """
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Clean text fields (remove extra whitespace, newlines)
        text_fields = ['name', 'designation', 'university', 'department']
        for field in text_fields:
            if adapter.get(field):
                # Remove extra whitespace and newlines
                cleaned = ' '.join(adapter[field].split())
                adapter[field] = cleaned.strip()
        
        # Validate and clean email
        if adapter.get('email'):
            adapter['email'] = self.clean_email(adapter['email'])
        
        # Clean phone number
        if adapter.get('phone'):
            adapter['phone'] = self.clean_phone(adapter['phone'])
        
        # Add scraping timestamp
        adapter['scraped_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return item
    
    def clean_email(self, email):
        """Clean and validate email address."""
        email = email.lower().strip()
        # Remove mailto: prefix if present
        email = re.sub(r'^mailto:', '', email)
        # Basic email validation
        if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return email
        return None
    
    def clean_phone(self, phone):
        """Clean phone number."""
        # Remove extra spaces and common separators
        phone = phone.strip()
        # Keep numbers, +, -, (, ), and spaces
        phone = re.sub(r'[^\d\+\-\(\)\s]', '', phone)
        return phone if phone else None


class DuplicateFilterPipeline:
    """
    Pipeline to filter out duplicate contacts based on email.
    """
    
    def __init__(self):
        self.emails_seen = set()
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        email = adapter.get('email')
        
        if email:
            if email in self.emails_seen:
                spider.logger.info(f"Duplicate contact found: {email}")
                raise DropItem(f"Duplicate email: {email}")
            else:
                self.emails_seen.add(email)
        
        return item


class DropItem(Exception):
    """Exception to drop an item from the pipeline."""
    pass


