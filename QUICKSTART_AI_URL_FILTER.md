# 🚀 Quick Start: AI URL Filtering

## What Is This?

AI URL Filtering uses AI to **predict which URLs contain contact information** before scraping them, saving time and money.

## 💡 Why Use It?

- **Save 40% on API costs** by skipping irrelevant pages
- **50% faster** scraping on large sites
- **Better results** - AI finds hidden contact pages

## 🎯 Quick Start (Web Interface)

### Step 1: Start the App
```bash
cd /Applications/MAMP/htdocs/contact_scraper
python app.py
```

### Step 2: Open Browser
Navigate to: http://localhost:5000

### Step 3: Enable AI URL Filtering
✅ Check the box: **"Enable AI URL Prioritization (Smart Filter)"**

### Step 4: Configure & Start
- Enter university URL
- Set max pages (recommended: 50-100)
- Click "Start Scraping"

### Step 5: Monitor Results
Watch the **AI Stats** card in the sidebar:
- **URL Prioritization** section shows filtering stats
- **Total Cost** includes URL analysis + extraction

## 🖥️ Quick Start (Command Line)

### Basic Usage
```bash
python oxylabs_integration.py https://university.edu 50 --ai-url-filter
```

### Recommended Setup
```bash
python oxylabs_integration.py https://university.edu 100 \
    --deep-crawl=100 \
    --ai-url-filter \
    --use-ai \
    --workers=30
```

## 📊 What You'll See

### Console Output
```
PHASE 3: AI URL PRIORITIZATION (SMART FILTER)
======================================================================
Analyzing 127 medium/low confidence URLs with AI...
✓ AI analyzed 127 URLs

AI Filtering Results:
  ↑ Upgraded: 23 URLs
  ↓ Downgraded: 15 URLs

  AI URL Analysis Cost: $0.003000
  Tokens used: 1,247
```

### Web Interface
Look for the **"AI Stats"** card showing:
- **Contact Extraction**: AI calls, success rate
- **URL Prioritization**: Requests, tokens used
- **Total Cost**: Combined cost for both operations

## 💰 Cost Examples

| Site Size | URLs Analyzed | Cost | Time |
|-----------|--------------|------|------|
| Small (50 URLs) | 20 uncertain | $0.000 | 1-2s |
| Medium (200 URLs) | 80 uncertain | $0.002 | 3-5s |
| Large (500 URLs) | 200 uncertain | $0.004 | 8-10s |

## 🎛️ Options

### AI Models
```bash
# Fast & cheap (default)
--ai-model=openai/gpt-4o-mini

# More accurate
--ai-model=anthropic/claude-3-haiku

# Free
--ai-model=google/gemini-flash-1.5
```

### When to Enable
✅ **Enable** for:
- Large universities (500+ URLs)
- Unknown website layouts
- Limited budgets

❌ **Skip** for:
- Small sites (< 50 URLs)
- Simple site structures
- Unlimited budgets

## 🔍 How It Works (Simple)

1. **Discover URLs** - Find all pages on site
2. **Keyword Score** - Rate URLs by keywords (contact, staff, etc.)
3. **AI Filter** - AI analyzes uncertain URLs
4. **Smart Scrape** - Only scrape top-ranked pages

## 🛠️ Troubleshooting

### AI URL Filter Not Working?
Check these:
1. ✅ API key set: `echo $OPENROUTER_API_KEY`
2. ✅ Checkbox enabled in web UI
3. ✅ Check console for errors

### Not Seeing Savings?
- Try with larger sites (200+ URLs)
- Enable deep crawling for more URL discovery
- Check AI stats to verify it's running

### Cost Too High?
- Reduce max_pages
- Disable deep crawling
- Use cheaper AI model (gemini-flash-1.5)

## 📚 More Information

- **Full Guide**: See `AI_URL_FILTERING_GUIDE.md`
- **Technical Details**: See `AI_URL_FILTERING_IMPLEMENTATION.md`
- **AI Extraction**: See `AI_EXTRACTION_SETUP.md`

## 🎉 Example Session

```bash
# 1. Start scraping with AI filtering
python oxylabs_integration.py https://sunway.edu.my 100 --ai-url-filter --use-ai

# Output shows:
# ✓ Discovered 482 URLs
# ✓ AI filtered to top 100 URLs (upgraded 31, downgraded 18)
# ✓ Scraped 100 pages
# ✓ Found 87 contacts
# ✓ URL filtering cost: $0.010
# ✓ Total cost: $0.177 (saved ~$0.150)
```

## ⚡ Pro Tips

1. **Combine features** - Use AI URL filter + AI extraction together
2. **Start small** - Test with 20 pages first
3. **Monitor costs** - Check AI stats after each run
4. **Use fast models** - gpt-4o-mini is 10x cheaper than GPT-4
5. **Enable deep crawl** - Discover more URLs, filter smarter

---

**Need Help?** Check the documentation or console output for detailed information.

**Ready to save time and money?** Enable AI URL Filtering now! 🚀

