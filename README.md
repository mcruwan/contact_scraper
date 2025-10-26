# 🎓 University Contact Scraper

A powerful web scraping tool designed to extract contact information (emails, phone numbers, names, and designations) from university websites. Features both a **command-line interface** and a **modern web interface**.

---

## ✨ Features

- 🌐 **Dual Interface**: Command-line and web-based UI
- 🚀 **Parallel Scraping**: Multi-threaded processing with Oxylabs API
- 🔍 **Smart URL Discovery**: Multiple strategies (sitemap, patterns, deep crawling)
- 🎯 **URL Prioritization**: Focuses on contact and staff directory pages
- 📊 **Real-time Progress**: Live updates on scraping progress
- 💾 **Multiple Formats**: Export to CSV and JSON
- 🔄 **IP Rotation**: Random geo-location for each request
- 📧 **Context-Aware Extraction**: Intelligently extracts names and titles

---

## 📋 Prerequisites

- Python 3.7+
- Oxylabs API credentials
- Active internet connection

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the project
cd uni_scraper

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Oxylabs Credentials

Edit `oxylabs_integration.py` and add your credentials:

```python
self.username = 'your_username'
self.password = 'your_password'
```

### 3. Run the Application

#### **Option A: Web Interface** (Recommended)

```bash
python app.py
```

Then open your browser to: **http://localhost:5000**

#### **Option B: Command Line**

```bash
python oxylabs_integration.py <URL> <MAX_PAGES> [OPTIONS]
```

**Examples:**
```bash
# Basic scraping (20 pages, 30 workers)
python oxylabs_integration.py https://example.edu 20 --workers=30

# With deep crawling (50 additional API calls for discovery)
python oxylabs_integration.py https://example.edu 100 --workers=30 --deep-crawl=50

# Large scrape (500 pages, 40 workers, deep crawling)
python oxylabs_integration.py https://example.edu 500 --workers=40 --deep-crawl=100
```

---

## 🖥️ Web Interface Guide

### Main Features

1. **Configuration Panel** (Left Side)
   - **Target URL**: Enter the university website
   - **Max Pages**: Number of pages to scrape (1-500)
   - **Workers**: Concurrent threads (1-100)
   - **Deep Crawl**: Enable recursive URL discovery
     - Specify number of API calls for discovery (10-200)

2. **Progress Monitor** (Right Side)
   - Real-time progress bar
   - Current URL being processed
   - Status messages
   - Error notifications

3. **Quick Stats**
   - URLs discovered counter
   - Contacts found counter

4. **Results Display**
   - Tabular view of all contacts
   - Download buttons for CSV and JSON

### Typical Workflow

1. Enter university URL (e.g., `https://example.edu`)
2. Adjust parameters:
   - **Small sites**: 20-50 pages, 30 workers
   - **Medium sites**: 100-200 pages, 40 workers, enable deep crawl
   - **Large sites**: 300+ pages, 50+ workers, deep crawl with 100+ requests
3. Click **"Start Scraping"**
4. Monitor progress in real-time
5. Download results when complete

---

## 🔧 Command-Line Reference

### Basic Syntax
```bash
python oxylabs_integration.py <URL> <MAX_PAGES> [OPTIONS]
```

### Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `URL` | Yes | - | Target university website |
| `MAX_PAGES` | Yes | - | Maximum pages to scrape |
| `--workers=N` | No | 30 | Number of concurrent workers (1-100) |
| `--deep-crawl[=N]` | No | Disabled | Enable deep crawling with N API calls |

### Examples

```bash
# Quick test (20 pages)
python oxylabs_integration.py https://sunwayuniversity.edu.my 20

# Medium scrape with more workers
python oxylabs_integration.py https://www.ucsiuniversity.edu.my 100 --workers=40

# Large scrape with deep crawling
python oxylabs_integration.py https://example.edu 500 --workers=50 --deep-crawl=100

# Deep crawl with default requests (50)
python oxylabs_integration.py https://example.edu 100 --deep-crawl
```

---

## 📁 Output Files

Results are saved in the `output/` directory:

### CSV Format (`contacts_TIMESTAMP.csv`)
```csv
Name,Designation,Email,Phone,University,URL
Dr. John Doe,Professor,[email protected],+1-234-567-8900,Example University,https://...
```

### JSON Format (`raw_contacts_TIMESTAMP.json`)
```json
{
  "url": "https://...",
  "contacts": [
    {
      "name": "Dr. John Doe",
      "designation": "Professor",
      "email": "[email protected]",
      "phone": "+1-234-567-8900"
    }
  ]
}
```

---

## 🔍 How URL Discovery Works

The scraper uses a multi-strategy approach:

### 1. **Sitemap Discovery**
- Checks common sitemap locations (`/sitemap.xml`, `/sitemap_index.xml`)
- Parses XML sitemaps
- Handles HTML-wrapped sitemaps

### 2. **Pattern-Based Discovery**
- Generates URLs based on common patterns:
  - `/contact`, `/contact-us`, `/directory`
  - `/staff`, `/faculty`, `/people`
  - `/about/staff`, `/team`

### 3. **Deep Crawling** (Optional)
- Recursively follows links on discovered pages
- Prioritizes staff/faculty URLs
- Configurable API call limit

### 4. **URL Prioritization**
- Scores URLs based on relevance keywords
- Higher priority for: `contact`, `directory`, `staff`, `faculty`
- Individual profile pages ranked higher

---

## ⚙️ Configuration Tips

### Choosing Parameters

| Site Size | Max Pages | Workers | Deep Crawl |
|-----------|-----------|---------|------------|
| Small (<100 pages) | 20-50 | 20-30 | Optional (20-30 requests) |
| Medium (100-1000 pages) | 100-200 | 30-40 | Recommended (50-100 requests) |
| Large (>1000 pages) | 300-500 | 40-50 | Yes (100-200 requests) |

### Performance Notes

- **Workers**: Higher = faster, but respect API rate limits (Oxylabs: 40 req/s)
- **Deep Crawl**: Uses additional API calls but discovers more URLs
- **Max Pages**: Balance between coverage and API usage

---

## 🛠️ Troubleshooting

### Common Issues

1. **"No contacts found"**
   - Try enabling deep crawl
   - Increase max pages
   - Check if site has anti-bot protection

2. **"Connection timeout"**
   - Check internet connection
   - Verify Oxylabs credentials
   - Reduce number of workers

3. **"Rate limit exceeded"**
   - Reduce workers
   - Check Oxylabs account limits

4. **Web interface not loading**
   - Ensure Flask is installed: `pip install flask`
   - Check if port 5000 is available
   - Try: `python app.py`

---

## 📊 Performance Metrics

Typical performance (with 30 workers):
- **URL Discovery**: 2-5 seconds (without deep crawl)
- **Scraping Rate**: ~25-35 pages/second
- **100 pages**: ~3-5 seconds
- **500 pages**: ~15-20 seconds

---

## 🤝 Contributing

For improvements or issues:
1. Test thoroughly with different university sites
2. Document any new patterns or strategies
3. Optimize for speed and accuracy

---

## 📝 License

This tool is for educational and research purposes. Respect robots.txt and terms of service of target websites.

---

## 🔗 Resources

- [Oxylabs Documentation](https://oxylabs.io/docs)
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Flask Documentation](https://flask.palletsprojects.com/)

---

**Happy Scraping! 🚀**
