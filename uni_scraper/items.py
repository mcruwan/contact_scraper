# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ContactItem(scrapy.Item):
    """
    Data model for contact information.
    """
    # Personal Information
    name = scrapy.Field()
    email = scrapy.Field()
    phone = scrapy.Field()
    
    # Professional Information
    designation = scrapy.Field()
    university = scrapy.Field()
    department = scrapy.Field()
    
    # Metadata
    source_url = scrapy.Field()
    scraped_date = scrapy.Field()
    
    def __repr__(self):
        """Simple representation showing name and email."""
        return f"ContactItem(name={self.get('name')}, email={self.get('email')})"


