# Project Summary: University Contact Scraper

## ✅ What Has Been Built

A **professional, production-ready web scraper** using Scrapy framework that:

### Core Features
- 🔍 **Automatically crawls** through all pages of a given domain
- 📧 **Extracts contact details**: name, email, phone, designation, university, department
- 🧹 **Cleans data** automatically (removes whitespace, validates emails, formats phones)
- 🚫 **Filters duplicates** based on email addresses
- 💾 **Exports to CSV & JSON** with timestamps
- 🤝 **Respectful crawling** (obeys robots.txt, rate limiting, auto-throttling)
- ⚡ **HTTP caching** to avoid redundant requests
- 🔄 **Automatic retries** for failed requests
- 📊 **Multiple extraction strategies** for maximum compatibility

### What Makes It Professional

1. **Standards-Compliant**
   - Follows Scrapy best practices
   - Proper project structure
   - Clean, documented code
   - Type hints and docstrings

2. **Robust & Reliable**
   - Multiple fallback strategies for finding contacts
   - Error handling throughout
   - Automatic retries on failures
   - Request timeout handling

3. **Ethical & Respectful**
   - Obeys robots.txt
   - 1-second delay between requests
   - Auto-throttling based on server load
   - Proper User-Agent identification

4. **Production-Ready**
   - Configurable settings
   - Logging and monitoring
   - Data validation pipeline
   - Duplicate filtering

## 📁 Project Structure

```
uni_scraper/
├── 📄 README.md                    # Full documentation
├── 📄 QUICKSTART.md                # Quick start guide
├── 📄 CUSTOMIZATION_GUIDE.md       # How to customize
├── 📄 example_usage.txt            # Usage examples
├── 📄 requirements.txt             # Dependencies
├── 📄 run.py                       # Simple runner script ⭐
├── 📄 scrapy.cfg                   # Scrapy config
├── 📄 .gitignore                   # Git ignore file
├── 📁 output/                      # Output directory
└── 📁 uni_scraper/                 # Main package
    ├── items.py                    # Data models
    ├── pipelines.py                # Data cleaning
    ├── settings.py                 # Configuration
    ├── middlewares.py              # Custom middlewares
    └── spiders/
        └── contact_spider.py       # Main spider ⭐
```

## 🚀 How to Use

### Installation (One-Time)
```bash
pip install -r requirements.txt
```

### Basic Usage
```bash
# Simple - scrape all pages
python run.py https://example.com/contacts

# With limits
python run.py https://example.com/contacts --max-pages 50

# Custom output
python run.py https://example.com/contacts --output my_results
```

### Command Options
- `--max-pages N`  : Limit number of pages to scrape
- `--max-depth N`  : Limit crawl depth (default: 5)
- `--output NAME`  : Custom output filename
- `--domain DOMAIN`: Restrict to specific domain

## 📤 Output

Results are saved in `output/` directory:

**CSV File** (e.g., `contacts_2024-10-25.csv`):
```csv
name,email,phone,designation,university,department,source_url,scraped_date
John Doe,john@example.edu,555-1234,Professor,Example University,CS,https://...,2024-10-25 20:30:00
```

**JSON File** (e.g., `contacts_2024-10-25.json`):
```json
[
  {
    "name": "John Doe",
    "email": "john@example.edu",
    "phone": "555-1234",
    "designation": "Professor",
    "university": "Example University",
    "department": "CS",
    "source_url": "https://...",
    "scraped_date": "2024-10-25 20:30:00"
  }
]
```

## 🎯 Key Components

### 1. Spider (`contact_spider.py`)
- **3 extraction strategies** for maximum compatibility
- Smart contact detection using multiple CSS selectors
- Automatic pagination handling
- Follows all links within domain

### 2. Data Pipeline (`pipelines.py`)
- **DataCleaningPipeline**: Cleans text, validates emails, formats phones
- **DuplicateFilterPipeline**: Removes duplicate contacts

### 3. Settings (`settings.py`)
- Respectful crawling configuration
- Auto-throttling enabled
- HTTP caching enabled
- Multiple output formats

### 4. Runner (`run.py`)
- Simple command-line interface
- Argument parsing
- Clear progress feedback

## 🛠️ Customization

The scraper works out-of-the-box for most websites, but you can customize:

1. **CSS Selectors** - Update in `contact_spider.py` for your specific site
2. **Crawl Speed** - Adjust `DOWNLOAD_DELAY` in `settings.py`
3. **Output Format** - Modify `FEEDS` in `settings.py`
4. **New Fields** - Add to `items.py` and extraction logic

See `CUSTOMIZATION_GUIDE.md` for detailed instructions.

## ⚠️ Important Notes

### Legal & Ethical
- ✅ Only scrape sites you have permission to scrape
- ✅ Respect robots.txt rules (enforced automatically)
- ✅ Use reasonable rate limits (configured by default)
- ✅ Comply with data protection laws

### Best Practices
- 🧪 Always test with `--max-pages 5` first
- ⏱️ Be patient - scraping takes time (1-2 sec per page)
- 📊 Review output files after each run
- 🔧 Customize selectors if needed for specific sites

## 📚 Documentation Files

1. **README.md** - Comprehensive documentation
2. **QUICKSTART.md** - Get started in 3 steps
3. **CUSTOMIZATION_GUIDE.md** - Customize for your site
4. **example_usage.txt** - Command examples

## 🐛 Troubleshooting

**No contacts found?**
→ Check logs, may need to update CSS selectors in `contact_spider.py`

**Too slow?**
→ Reduce `DOWNLOAD_DELAY` in `settings.py`

**Getting blocked?**
→ Increase delays, reduce concurrent requests

**JavaScript-heavy site?**
→ May need Scrapy-Playwright for JS rendering

## 🎓 Learning Resources

- Scrapy docs: https://docs.scrapy.org/
- CSS selectors: https://www.w3schools.com/cssref/css_selectors.asp
- Python regex: https://docs.python.org/3/library/re.html

## 📝 Example Workflow

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Test with small sample
python run.py https://example.edu/faculty --max-pages 5

# 3. Review output/contacts_TIMESTAMP.csv

# 4. If good, run full scrape
python run.py https://example.edu/faculty --max-pages 100 --output faculty_2024

# 5. Open CSV in Excel or process JSON programmatically
```

## 🎉 You're Ready!

Just provide the URL and run:
```bash
python run.py YOUR_URL_HERE
```

The scraper will handle the rest! 

---

**Built with ❤️ using Scrapy framework**


