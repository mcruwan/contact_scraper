# Handling Blocked Websites - Complete Guide

## 🚫 **Problem: Website is Blocking the Scraper**

When you see **403 Forbidden** errors, it means the website has anti-bot protection that's blocking our scraper. This is very common with university websites.

## 🔍 **Why Websites Block Scrapers**

1. **Cloudflare Protection** - Most common
2. **Rate Limiting** - Too many requests too fast
3. **IP-based Blocking** - Your IP is flagged
4. **User-Agent Detection** - They detect automated tools
5. **JavaScript Challenges** - Require browser interaction
6. **Geographic Restrictions** - Location-based blocking

## 🛠️ **Solutions & Alternatives**

### **Option 1: Try Different URLs**

Some pages might be less protected:

```bash
# Try these specific URLs
python run.py https://ucsiuniversity.edu.my/faculty
python run.py https://ucsiuniversity.edu.my/staff
python run.py https://ucsiuniversity.edu.my/contact-us
python run.py https://ucsiuniversity.edu.my/directory
```

### **Option 2: Use a Different University Website**

Try websites that are more scraper-friendly:

```bash
# Test with these examples
python run.py https://example.edu/faculty --max-pages 5
python run.py https://university.edu/staff --max-pages 10
```

### **Option 3: Advanced Anti-Detection (For Experts)**

If you need to scrape protected sites, you can try:

#### **A. Use Scrapy-Playwright (JavaScript Rendering)**

```bash
pip install scrapy-playwright
playwright install
```

Then modify the spider to use Playwright for JavaScript-heavy sites.

#### **B. Use Proxies**

```python
# Add to settings.py
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
}

# Use rotating proxies
PROXY_LIST = [
    'http://proxy1:port',
    'http://proxy2:port',
]
```

#### **C. Use Residential Proxies**

For heavily protected sites, you might need residential proxies from services like:
- Bright Data
- Oxylabs
- Smartproxy

### **Option 4: Manual Data Collection**

For highly protected sites, consider:

1. **Browser Automation** with Selenium
2. **Manual collection** with browser extensions
3. **API access** if available
4. **Contact the university** directly for data

## 🎯 **Recommended Approach for UCSI University**

### **Step 1: Try Alternative URLs**

```bash
# Try these specific pages
python run.py https://ucsiuniversity.edu.my/faculty --max-pages 3
python run.py https://ucsiuniversity.edu.my/staff --max-pages 3
python run.py https://ucsiuniversity.edu.my/contact --max-pages 3
```

### **Step 2: Check if the Site is Accessible**

Open the website in your browser:
- Go to https://ucsiuniversity.edu.my
- Check if it loads normally
- Look for contact/faculty pages
- Note the exact URLs that work

### **Step 3: Try Different Times**

Some sites have different protection levels at different times:
- Try during off-peak hours
- Try on weekends
- Try from different networks

### **Step 4: Use Browser-Based Scraping**

If the site requires JavaScript, you can use:

```bash
# Install Selenium-based scraper
pip install selenium beautifulsoup4
```

## 📋 **Alternative Data Sources**

### **1. University Directories**
- LinkedIn university pages
- Academic staff directories
- Research gate profiles
- Google Scholar profiles

### **2. Official University Pages**
- Faculty pages
- Department pages
- Research center pages
- Contact pages

### **3. Third-Party Sources**
- University ranking websites
- Academic databases
- Professional networks

## 🔧 **Technical Solutions**

### **For JavaScript-Heavy Sites**

Create a Selenium-based scraper:

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

def scrape_with_selenium(url):
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(5)  # Wait for page to load
    
    # Extract contact information
    contacts = driver.find_elements(By.CLASS_NAME, "contact-card")
    for contact in contacts:
        name = contact.find_element(By.CLASS_NAME, "name").text
        email = contact.find_element(By.CLASS_NAME, "email").text
        print(f"Name: {name}, Email: {email}")
    
    driver.quit()
```

### **For Cloudflare-Protected Sites**

Use specialized tools:
- **ScrapingBee** - API service
- **ScraperAPI** - Proxy service
- **Bright Data** - Enterprise solution

## ⚖️ **Legal & Ethical Considerations**

### **Always Check:**
1. **robots.txt** - https://ucsiuniversity.edu.my/robots.txt
2. **Terms of Service** - Check what's allowed
3. **Rate Limits** - Don't overload servers
4. **Data Usage** - Respect privacy laws

### **Best Practices:**
- Use reasonable delays (3+ seconds)
- Limit concurrent requests
- Respect robots.txt
- Don't scrape personal data without permission
- Use data responsibly

## 🎯 **Quick Test Commands**

Try these to see if any work:

```bash
# Test basic connectivity
python run.py https://httpbin.org/html --max-pages 1

# Test with a different university
python run.py https://www.harvard.edu/faculty --max-pages 3

# Test with a more open site
python run.py https://example.com --max-pages 2
```

## 📞 **Contact Information Sources**

If scraping fails, try these alternatives:

1. **University Contact Pages**
2. **Department Websites**
3. **Faculty Directories**
4. **LinkedIn University Pages**
5. **Academic Databases**
6. **Research Gate**
7. **Google Scholar**

## 🚀 **Next Steps**

1. **Try the alternative URLs** above
2. **Test with different universities** to verify the scraper works
3. **Consider manual collection** for highly protected sites
4. **Use browser automation** for JavaScript-heavy sites
5. **Contact the university** directly for data access

---

**Remember:** Not all websites can be scraped easily. Some have strong protections for good reasons. Always respect the website's terms and use data ethically.

