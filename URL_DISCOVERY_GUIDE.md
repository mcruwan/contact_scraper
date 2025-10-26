# 🔍 URL Discovery System - Complete Guide

## Overview

The URL discovery system is like **exploring a library** to find all the books (web pages) before you start reading them. It uses three intelligent methods to find contact-related pages on university websites.

## 📚 The Library Analogy

### How It Works:
1. **Start at the main entrance** (homepage: `https://www.ucsiuniversity.edu.my/`)
2. **Check the master directory** (sitemap.xml) - if it exists, it lists ALL pages
3. **Look at common sections** (pattern-based discovery) - check typical locations
4. **Walk around and follow signs** (deep crawling) - explore systematically

---

## 🎯 Three Discovery Methods

### Method 1: Sitemap Discovery (The Master Directory)

**What it does:** Looks for `sitemap.xml` files that contain ALL website URLs

**How it works:**
```python
# Check common sitemap locations
sitemap_locations = [
    "/sitemap.xml",
    "/sitemap_index.xml", 
    "/sitemaps/sitemap.xml",
    "/sitemap/sitemap.xml"
]

# If found, extract ALL URLs from XML
for loc in soup.find_all('loc'):
    url = loc.get_text().strip()
    discovered_urls.add(url)
```

**Pros:**
- ✅ Most comprehensive (finds ALL pages)
- ✅ Fast (one API call gets everything)
- ✅ Includes individual staff profiles

**Cons:**
- ❌ Not all websites have sitemaps
- ❌ Can be very large (thousands of URLs)

**When used:** Only for large scrapes (>50 pages)

---

### Method 2: Pattern-Based Discovery (Check Common Sections)

**What it does:** Generates likely URLs based on common patterns

**Common patterns:**
```python
patterns = [
    "/staff",           # Staff directory
    "/staff-directory", # Alternative staff directory
    "/faculty",         # Faculty directory
    "/faculty-directory", # Alternative faculty directory
    "/people",          # People directory
    "/team",            # Team directory
    "/directory",       # General directory
    "/our-staff",       # Our staff page
    "/our-faculty",     # Our faculty page
    "/about/staff",     # About staff section
    "/about/faculty"    # About faculty section
]
```

**How it works:**
```python
# Generate URLs without making API calls
for pattern in patterns:
    test_url = f"https://{base_domain}{pattern}"
    if test_url not in discovered_urls:
        pattern_urls.append(test_url)
```

**Pros:**
- ✅ Very fast (no API calls)
- ✅ Covers most common contact pages
- ✅ Always works

**Cons:**
- ❌ May include non-existent URLs
- ❌ Misses individual staff profiles
- ❌ Limited to common patterns

**When used:** Always (for all scrapes)

---

### Method 3: Deep Crawling (Walk Around and Follow Signs)

**What it does:** Visits pages and follows links to discover new URLs

**How it works:**
```python
# Visit each page in the queue
for current_url in urls_to_process:
    # Fetch the page
    content = fetch_page_with_oxylabs(current_url)
    
    # Find all links on the page
    for link in soup.find_all('a', href=True):
        href = link['href']
        full_url = urljoin(current_url, href)
        
        # Add valid URLs to discovery queue
        if is_valid_url(full_url):
            discovered_urls.add(full_url)
            urls_to_process.append(full_url)
```

**Priority System:**
- **High Priority:** Staff/faculty URLs processed first
- **Regular Priority:** Other URLs processed later
- **Smart Queue:** Priority URLs added to front of queue

**Pros:**
- ✅ Finds individual staff profiles
- ✅ Discovers hidden pages
- ✅ Most thorough method

**Cons:**
- ❌ Slow (many API calls)
- ❌ Can be expensive
- ❌ May hit rate limits

**When used:** 
- Small scrapes (≤50 pages): **SKIPPED** (too slow)
- Medium scrapes (51-100 pages): **Limited** (20 requests)
- Large scrapes (>100 pages): **Full** (50 requests)

---

## ⚡ Speed Optimization Strategy

### Adaptive Discovery Limits

| Pages | Sitemap | Patterns | Deep Crawling | Total Discovery Time |
|-------|---------|----------|---------------|-------------------|
| **≤50** | ❌ SKIP | ✅ YES | ❌ SKIP | **~1 second** |
| **51-100** | ❌ SKIP | ✅ YES | 🔶 LIMITED (20) | **~30 seconds** |
| **>100** | ✅ YES | ✅ YES | 🔶 FULL (50) | **~2-3 minutes** |

### Why This Works:

**Small Scrapes (≤50 pages):**
- Pattern-based URLs are usually enough
- Deep crawling is overkill and slow
- **Result:** Fast scraping, good coverage

**Medium Scrapes (51-100 pages):**
- Need some discovery but not too much
- Limited deep crawling finds more pages
- **Result:** Balanced speed and coverage

**Large Scrapes (>100 pages):**
- Need comprehensive discovery
- Sitemap + deep crawling finds everything
- **Result:** Maximum coverage, slower but thorough

---

## 🎯 URL Prioritization System

### Keyword Scoring

URLs are scored based on how likely they are to contain contact information:

```python
keyword_scores = {
    # Highest priority (score: 120) - Individual profiles
    'professor': 120, 'lecturer': 120, 'dr-': 120, 'prof-': 120,
    'associate-professor': 120, 'assistant-professor': 120,
    
    # High priority (score: 100) - Directories
    'contact': 100, 'contacts': 100, 'contact-us': 100,
    'directory': 100, 'staff-directory': 100, 'faculty-directory': 100,
    
    # Medium-high priority (score: 80) - Staff pages
    'staff': 80, 'faculty': 80, 'team': 80, 'people': 80,
    'employee': 80, 'personnel': 80, 'academic-staff': 80,
    
    # Medium priority (score: 60) - Departments
    'about': 60, 'department': 60, 'school': 60,
    'administration': 60, 'management': 60, 'leadership': 60,
    
    # Low priority (score: 20) - General pages
    'profile': 20, 'bio': 20, 'research': 20, 'academic': 20
}
```

### Priority Processing

1. **Score each URL** based on keywords
2. **Sort by score** (highest first)
3. **Process high-priority URLs first**
4. **Add new priority URLs to front of queue**

---

## 📊 Real-World Examples

### Example 1: Small Scrape (20 pages)

**Input:** `https://www.ucsiuniversity.edu.my/` (20 pages)

**Process:**
```
METHOD 1: SITEMAP - SKIPPED (≤50 pages)
METHOD 2: PATTERNS - Generated 11 URLs
METHOD 3: DEEP CRAWL - SKIPPED (≤50 pages)

Result: 11 URLs ready for scraping
Time: ~1 second discovery + 36 seconds scraping = 37 seconds total
```

**URLs Found:**
- `/staff-directory` (score: 340)
- `/faculty-directory` (score: 340) 
- `/directory` (score: 160)
- `/about/faculty` (score: 140)
- `/about/staff` (score: 140)
- `/our-staff` (score: 80)
- `/faculty` (score: 80)
- `/team` (score: 80)
- `/people` (score: 80)
- `/our-faculty` (score: 80)
- `/staff` (score: 80)

### Example 2: Large Scrape (200 pages)

**Input:** `https://sunwayuniversity.edu.my/` (200 pages)

**Process:**
```
METHOD 1: SITEMAP - Found 1500+ URLs
METHOD 2: PATTERNS - Generated 11 URLs  
METHOD 3: DEEP CRAWL - 50 requests, found 200+ more URLs

Result: 1700+ URLs, top 200 selected for scraping
Time: ~3 minutes discovery + 5 minutes scraping = 8 minutes total
```

---

## 🔧 Configuration Options

### Command Line Usage

```bash
# Small scrape (fast, pattern-based only)
python oxylabs_integration.py https://example.com/ 20 --workers=30

# Medium scrape (limited discovery)
python oxylabs_integration.py https://example.com/ 75 --workers=30

# Large scrape (full discovery)
python oxylabs_integration.py https://example.com/ 200 --workers=30

# Direct mode (skip discovery entirely)
python oxylabs_integration.py https://example.com/contact 1 --direct
```

### Parameters

- `max_pages`: Number of pages to scrape
- `--workers=N`: Number of parallel workers (default: 20, max: 30)
- `--direct`: Skip URL discovery, scrape provided URL directly
- `--save-html`: Save raw HTML for debugging

---

## 🎯 Best Practices

### For Maximum Speed:
- Use `--direct` for single pages
- Keep `max_pages` ≤ 50 for fastest discovery
- Use 30 workers for maximum parallelization

### For Maximum Coverage:
- Use `max_pages` > 100 to enable sitemap discovery
- Allow time for deep crawling
- Check results and adjust patterns if needed

### For Specific Sites:
- Test with small scrapes first
- Use `--save-html` to debug discovery issues
- Adjust patterns based on site structure

---

## 🚀 Performance Summary

| Scenario | Discovery Time | Scraping Time | Total Time | Coverage |
|----------|---------------|---------------|------------|----------|
| **1 page (direct)** | 0s | 18s | 18s | Single page |
| **20 pages** | 1s | 36s | 37s | Good |
| **50 pages** | 1s | 90s | 91s | Good |
| **100 pages** | 30s | 180s | 210s | Very Good |
| **200 pages** | 180s | 300s | 480s | Excellent |

**The system automatically chooses the best strategy based on your needs!** 🎉
