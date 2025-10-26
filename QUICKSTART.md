# Quick Start Guide

## Installation (One-Time Setup)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage (Simple 3-Step Process)

### Step 1: Run the scraper with your URL

```bash
python run.py https://your-university-website.com/contacts
```

### Step 2: Wait for completion

The scraper will:
- ✓ Visit all pages on the domain
- ✓ Extract contact information
- ✓ Clean and validate data
- ✓ Remove duplicates
- ✓ Save results automatically

### Step 3: Check your results

Open the `output/` folder to find:
- `contacts_TIMESTAMP.csv` - Open in Excel
- `contacts_TIMESTAMP.json` - For programming

## Common Options

**Limit pages to scrape:**
```bash
python run.py https://example.com/contacts --max-pages 50
```

**Control crawl depth:**
```bash
python run.py https://example.com/contacts --max-depth 3
```

**Custom output name:**
```bash
python run.py https://example.com/contacts --output my_results
```

## Tips

1. **Start small** - Test with `--max-pages 5` first
2. **Be patient** - Large sites take time (1-2 seconds per page)
3. **Check logs** - Watch console output for progress
4. **Be respectful** - Don't overload servers

## Example

```bash
# Test run (scrape 10 pages)
python run.py https://example.edu/faculty --max-pages 10

# Full run
python run.py https://example.edu/faculty --max-pages 100 --output faculty_2024
```

## Need Help?

Check the full `README.md` for detailed documentation.

---

That's it! Simple and powerful. 🚀

