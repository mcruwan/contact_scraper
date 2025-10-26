# 🚀 Quick Start Guide - Web Interface

## Getting Started

### Step 1: Start the Server
```bash
python app.py
```

### Step 2: Open Your Browser
Navigate to: **http://localhost:5000**

### Step 3: Configure Your Scrape
1. **Enter URL**: Type the university website (e.g., `https://sunwayuniversity.edu.my`)
2. **Set Max Pages**: Use the slider (1-500 pages)
3. **Set Workers**: Adjust concurrent threads (1-100)
4. **Enable Deep Crawl** (Optional): Toggle for recursive discovery
   - Set API requests for discovery (10-200)

### Step 4: Start Scraping
Click the **"Start Scraping"** button and watch the magic happen! ✨

### Step 5: Download Results
Once complete, download your results:
- **CSV**: For Excel/spreadsheet software
- **JSON**: For programmatic access

---

## 📊 Interface Layout

### Left Panel - Configuration
- **Target URL**: Enter the website to scrape
- **Max Pages**: Number of pages to scrape (slider)
- **Workers**: Parallel processing threads (slider)
- **Deep Crawl**: Enable/disable recursive URL discovery
- **Quick Stats**: Live counters for URLs and contacts

### Right Panel - Progress & Results
- **Progress Bar**: Visual indicator of scraping progress
- **Status Messages**: Real-time updates
- **Current URL**: Shows what's being processed
- **Results Table**: Displays all found contacts
- **Download Buttons**: Export to CSV or JSON

---

## 🎯 Recommended Settings

### Small University Sites
- **Max Pages**: 20-50
- **Workers**: 20-30
- **Deep Crawl**: Optional (20-30 requests)

### Medium University Sites
- **Max Pages**: 100-200
- **Workers**: 30-40
- **Deep Crawl**: Recommended (50-100 requests)

### Large University Sites
- **Max Pages**: 300-500
- **Workers**: 40-50
- **Deep Crawl**: Yes (100-200 requests)

---

## 💡 Pro Tips

1. **Start Small**: Test with 20 pages first to see the site structure
2. **Monitor Progress**: Watch the "Current URL" box to see what's being scraped
3. **Check Results**: Review the table before downloading
4. **Deep Crawl**: Only enable when you need comprehensive coverage
5. **Workers**: More isn't always better - respect API limits (Oxylabs: 40 req/s)

---

## 🔧 Troubleshooting

### Server Won't Start
```bash
# Check if port 5000 is already in use
netstat -ano | findstr :5000

# Install Flask if missing
pip install flask
```

### Can't Access Interface
- Ensure server is running (check terminal output)
- Try: http://127.0.0.1:5000
- Clear browser cache
- Try a different browser

### Scraping Fails
- Check Oxylabs credentials in `oxylabs_integration.py`
- Verify internet connection
- Try reducing workers
- Check if URL is accessible

### No Results Found
- Enable deep crawl
- Increase max pages
- Try a different starting URL
- Check if site has anti-bot protection

---

## 🌟 Features Explained

### Real-Time Progress
The interface updates every second showing:
- Current progress percentage
- Status messages
- URLs discovered
- Contacts found
- Current URL being processed

### Smart URL Discovery
The scraper automatically:
1. Checks sitemaps
2. Tests common URL patterns
3. Recursively crawls pages (if deep crawl enabled)
4. Prioritizes contact/staff pages

### Result Display
Results appear in a sortable table with:
- Name
- Designation
- Email (clickable mailto link)
- Phone
- University
- Source URL

---

## 📝 Example Workflow

1. **Start Server**
   ```bash
   python app.py
   ```

2. **Open Browser**
   - Go to http://localhost:5000

3. **Configure Scrape**
   - URL: `https://sunwayuniversity.edu.my`
   - Max Pages: `100`
   - Workers: `30`
   - Deep Crawl: `Enabled (50 requests)`

4. **Start & Wait**
   - Click "Start Scraping"
   - Watch progress bar
   - See contacts appear in real-time

5. **Download Results**
   - Click "CSV" or "JSON" button
   - Open in Excel or text editor

---

## 🎨 Interface Colors & Indicators

- **Blue Progress Bar**: Starting/In Progress (0-50%)
- **Yellow Progress Bar**: Making Progress (50-99%)
- **Green Progress Bar**: Complete (100%)
- **Red Alert Box**: Error occurred
- **Blue Info Box**: Currently processing URL

---

## ⚡ Keyboard Shortcuts

- **F5**: Refresh page
- **Ctrl + R**: Reload interface
- **Ctrl + S**: (Won't work - it's a web app!)

---

## 📦 Output Files

All results are saved in the `output/` directory:

### CSV File
- Filename: `contacts_YYYY-MM-DDTHH-MM-SS+00-00.csv`
- Format: Excel-compatible
- Columns: Name, Designation, Email, Phone, University, URL

### JSON File
- Filename: `raw_contacts_YYYY-MM-DDTHH-MM-SS+00-00.json`
- Format: Structured JSON
- Contains: All raw contact data

---

## 🔄 Multiple Scrapes

You can run multiple scrapes:
1. Complete current scrape
2. Change URL/settings
3. Click "Start Scraping" again
4. Each scrape creates new timestamped files

---

## 🛡️ Safety Features

- **Input Validation**: Checks URL format
- **Range Limits**: Prevents excessive settings
- **Error Handling**: Graceful failure with messages
- **Progress Tracking**: Always know what's happening
- **Thread Safe**: Single scrape at a time

---

## 📞 Need Help?

If you encounter issues:
1. Check console output in terminal
2. Review browser console (F12)
3. Verify Oxylabs credentials
4. Test with a simple URL first
5. Check the main README.md for more details

---

**Happy Scraping! 🎉**

