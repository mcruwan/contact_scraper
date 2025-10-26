# Customization Guide

This guide helps you customize the scraper for specific websites.

## For Specific Website Structures

If the default scraper doesn't work well for your target website, you can customize the CSS selectors.

### Step 1: Inspect the Website

1. Open the website in Chrome/Firefox
2. Right-click on a contact → "Inspect" or "Inspect Element"
3. Note the HTML structure and class names

### Step 2: Update Contact Selectors

Edit `uni_scraper/spiders/contact_spider.py`:

#### Finding Contact Containers

Look for the section around line 80-90 with `contact_selectors`:

```python
contact_selectors = [
    '.contact-card',      # Add your website's classes here
    '.staff-member',      # Example: '.faculty-profile'
    '.your-custom-class', # Add more as needed
]
```

**How to find your selector:**
- Look for repeated containers that wrap each contact
- Common patterns: `.card`, `.profile`, `.member`, `.person`

#### Extracting Specific Fields

Find the section around line 160-200 for field extraction:

**For Name:**
```python
name_selectors = [
    '.name::text',           # Default
    '.your-name-class::text', # Add your site's selector
    'h2.title::text',        # Example
]
```

**For Email:**
The email is extracted automatically from text, but you can improve it:
```python
# Look for mailto links (already included)
mailto_links = element.css('a[href^="mailto:"]::attr(href)').getall()

# Or specific email classes
email = element.css('.email::text').get()
```

**For Phone:**
```python
# Automatic extraction from text (already included)
# Or from tel links
tel_links = element.css('a[href^="tel:"]::attr(href)').getall()
```

**For Designation:**
```python
designation_selectors = [
    '.designation::text',
    '.job-title::text',      # Add your selectors
    '.position::text',
]
```

**For University/Department:**
```python
university_selectors = [
    '.university::text',
    '.institution::text',
    # Add your site's selector
]
```

## Example Customization

Let's say you inspect a website and find:
- Contacts are in `<div class="faculty-card">`
- Names are in `<h3 class="faculty-name">`
- Titles are in `<span class="faculty-title">`

**Update the selectors:**

```python
# Around line 85
contact_selectors = [
    '.faculty-card',  # Your specific selector
    '.contact-card',  # Keep defaults as fallback
    '.staff-member',
]

# Around line 160
name_selectors = [
    '.faculty-name::text',  # Your specific selector
    '.name::text',          # Keep defaults
    'h3::text',
]

# Around line 180
designation_selectors = [
    '.faculty-title::text',  # Your specific selector
    '.designation::text',    # Keep defaults
    '.title::text',
]
```

## Adjusting Crawl Behavior

### Change Request Speed

Edit `uni_scraper/settings.py`:

```python
# Line ~30 - Delay between requests (seconds)
DOWNLOAD_DELAY = 2  # Increase if site is sensitive

# Line ~32 - Concurrent requests
CONCURRENT_REQUESTS = 4  # Reduce to be more polite
```

### Change Crawl Depth

When running:
```bash
python run.py https://example.com --max-depth 2
```

Or in `uni_scraper/spiders/contact_spider.py`:
```python
custom_settings = {
    'DEPTH_LIMIT': 3,  # Change default depth
}
```

### Limit to Specific Paths

In `uni_scraper/spiders/contact_spider.py`, around line 50, add path filtering:

```python
def parse(self, response):
    # Only process URLs containing specific keywords
    if not any(keyword in response.url.lower() for keyword in ['staff', 'faculty', 'contact']):
        return
    
    # ... rest of the code
```

## Testing Your Changes

1. **Test with 1-2 pages:**
   ```bash
   python run.py https://example.com --max-pages 2
   ```

2. **Check the output CSV** - Are all fields populated correctly?

3. **Review the logs** - Any warnings or errors?

4. **Adjust selectors** based on what you see

5. **Test with more pages** once it's working

## Common Issues & Fixes

### Issue: No contacts found

**Fix:** Update `contact_selectors` with your site's classes

### Issue: Missing names/emails

**Fix:** Update field-specific selectors

### Issue: Too many duplicates

**Fix:** The pipeline already filters by email, but you can add more filtering

### Issue: Scraping too slow

**Fix:** Reduce `DOWNLOAD_DELAY` in settings.py

### Issue: Getting blocked

**Fix:** Increase `DOWNLOAD_DELAY`, reduce `CONCURRENT_REQUESTS`

## Advanced: Adding New Fields

To extract additional fields (e.g., office number, research area):

1. **Add to items.py:**
```python
class ContactItem(scrapy.Item):
    # ... existing fields ...
    office = scrapy.Field()
    research_area = scrapy.Field()
```

2. **Add extraction in contact_spider.py:**
```python
# Around line 220
office_selectors = ['.office::text', '.room::text']
for selector in office_selectors:
    office = element.css(selector).get()
    if office:
        contact['office'] = office.strip()
        break
```

3. **Add to output fields in settings.py:**
```python
'fields': ['name', 'email', 'phone', 'designation', 'university', 
           'department', 'office', 'research_area', 'source_url', 'scraped_date'],
```

## Need More Help?

1. Check Scrapy selectors guide: https://docs.scrapy.org/en/latest/topics/selectors.html
2. Use CSS selector reference: https://www.w3schools.com/cssref/css_selectors.asp
3. Test selectors in browser console: `document.querySelectorAll('.your-selector')`

---

Remember: Test with small page limits first! 🎯


