# 🎯 AI URL Prioritization Guide

## Overview

The AI URL Prioritization feature uses artificial intelligence to intelligently filter and prioritize URLs before scraping, significantly improving efficiency and reducing costs.

## 🚀 How It Works

### Phase 1: Keyword-Based Scoring (Always Active)
- URLs are analyzed using keyword patterns
- High-priority URLs (score >= 60): contact, staff, faculty, directory pages
- Medium-priority URLs (score 20-59): about, department, team pages
- Low-priority URLs (score < 20): news, events, blog pages

### Phase 2: AI Smart Filtering (Optional)
- **AI analyzes medium/low confidence URLs** to predict contact information likelihood
- High-confidence URLs skip AI analysis (already trusted)
- AI returns likelihood scores (0.0 to 1.0) for each URL
- URLs are re-ranked based on combined keyword + AI scores

### Phase 3: Intelligent Scraping
- Only the most promising URLs are scraped
- Saves API calls by filtering out unlikely pages
- Typical cost: ~$0.001 per 50 URLs analyzed

## 📊 Benefits

### Cost Savings
- **Reduces unnecessary scraping** of irrelevant pages
- AI analysis costs ~$0.001/50 URLs
- Can save $0.05-0.20 per university by avoiding 50-200 low-value pages

### Efficiency
- **Focuses on high-value pages first**
- Batch processing: analyzes up to 50 URLs at once
- Typical analysis time: 2-5 seconds for 50 URLs

### Accuracy
- **Hybrid approach** combines keyword patterns + AI intelligence
- AI catches edge cases that keywords miss
- Identifies staff profiles even without "staff" in URL

## 🎛️ Usage

### Command Line
```bash
# Enable AI URL filtering
python oxylabs_integration.py https://university.edu 50 --ai-url-filter

# Use with other options
python oxylabs_integration.py https://university.edu 50 --deep-crawl=50 --ai-url-filter --use-ai
```

### Web Interface
1. Go to http://localhost:5000
2. Enable "**AI URL Prioritization (Smart Filter)**" checkbox
3. Configure other settings
4. Click "Start Scraping"

## 💰 Cost Estimation

### Typical Costs
- **URL Analysis**: $0.001 per 50 URLs
- **Example**: Analyzing 200 URLs = $0.004
- **Contact Extraction**: $0.001-0.003 per contact (separate cost)

### Cost Breakdown by University Size
| University Type | URLs Discovered | AI Analysis Cost | Estimated Savings |
|----------------|----------------|------------------|-------------------|
| Small (< 100 URLs) | 80 | $0.002 | $0.03-0.05 |
| Medium (100-500 URLs) | 250 | $0.005 | $0.10-0.15 |
| Large (500+ URLs) | 800 | $0.016 | $0.30-0.50 |

## 🧠 AI Model Options

The system uses the same model for both URL analysis and contact extraction:

```bash
# Fast and cheap (recommended)
--ai-model=openai/gpt-4o-mini

# More accurate for complex cases
--ai-model=anthropic/claude-3-haiku

# Free tier available
--ai-model=meta-llama/llama-3.1-8b-instruct

# Fast and free
--ai-model=google/gemini-flash-1.5
```

## 📈 Performance Metrics

The system tracks:
- **URL Analysis Requests**: Number of AI calls for URL filtering
- **Tokens Used**: Total tokens for URL analysis (separate from extraction)
- **Analysis Cost**: Cost for URL prioritization
- **Upgraded URLs**: URLs promoted by AI
- **Downgraded URLs**: URLs deprioritized by AI

## 🎯 When to Use AI URL Filtering

### ✅ Recommended For:
- **Large universities** (500+ discovered URLs)
- **Unknown website structures** (non-standard layouts)
- **Limited scraping budgets** (want to maximize ROI)
- **High-precision needs** (only want the best pages)

### ❌ Not Needed For:
- **Small sites** (< 50 URLs total)
- **Well-structured sites** (clear /staff/ and /contact/ pages)
- **Unlimited budgets** (scraping all pages is fine)

## 🔧 Advanced Configuration

### Batch Size
- URLs analyzed in batches of 50
- Larger batches may be split automatically
- Configurable in `ai_extractor.py`

### Confidence Threshold
- High-confidence URLs (score >= 60) skip AI
- Medium/low URLs (score < 60) analyzed by AI
- Adjustable in `oxylabs_integration.py`

### Re-Ranking Logic
```python
# AI boost calculation
ai_boost = int(ai_likelihood * 100)  # 0.0-1.0 → 0-100
final_score = max(keyword_score, ai_boost)

# Example:
# URL: "https://uni.edu/people/profiles/john-smith"
# Keyword score: 40 (medium - has "people")
# AI likelihood: 0.85 (high confidence - staff profile)
# Final score: 85 (takes higher value)
```

## 📊 Statistics Display

### Web Interface
- **URL Prioritization section** shows:
  - AI requests made
  - Tokens used for URL analysis
  - Separate from contact extraction stats

### Console Output
```
PHASE 3: AI URL PRIORITIZATION (SMART FILTER)
======================================================================
Analyzing 127 medium/low confidence URLs with AI...
✓ AI analyzed 127 URLs

AI Filtering Results:
  ↑ Upgraded: 23 URLs
  ↓ Downgraded: 15 URLs

  Top upgraded URLs:
    https://uni.edu/people/faculty/jane-doe... (AI: 0.92)
    https://uni.edu/departments/cs/contacts... (AI: 0.88)

  AI URL Analysis Cost: $0.003000
  Tokens used: 1,247
```

## 🔍 Behind the Scenes

### AI Prompt Strategy
The AI receives a batch of URLs and considers:
- Presence of keywords (staff, faculty, contact, people)
- URL structure patterns (profile paths, directory pages)
- Common academic website conventions
- Negative signals (news, blog, events)

### Response Format
```json
[
  {
    "url": "https://uni.edu/staff/directory",
    "likelihood": 0.95,
    "reason": "staff directory page"
  },
  {
    "url": "https://uni.edu/news/2024",
    "likelihood": 0.15,
    "reason": "news archive"
  }
]
```

## 🛠️ Troubleshooting

### AI URL Filter Not Working
1. Check API key is set: `echo $OPENROUTER_API_KEY`
2. Verify checkbox is enabled in web UI
3. Check console logs for errors

### Unexpected Results
- AI may occasionally mis-classify URLs
- Hybrid approach ensures keyword scores provide baseline
- High-confidence URLs always scraped (AI bypass)

### Cost Too High
- Reduce max_pages to limit URL discovery
- Disable deep crawling (`--no-deep-crawl`)
- Use free/cheaper AI models

## 🎓 Best Practices

1. **Start with AI filtering disabled** - understand baseline behavior
2. **Enable for large sites** - where filtering provides clear value
3. **Monitor costs** - check AI stats after each run
4. **Combine with deep crawling** - discover more, filter smarter
5. **Use fast models** - gpt-4o-mini or gemini-flash-1.5

## 📚 Related Features

- **AI Contact Extraction** - AI-powered name/phone extraction
- **Deep Crawling** - Discover more URLs via API
- **Parallel Processing** - Fast scraping with multiple workers

## 🎉 Example Workflow

```bash
# Optimal setup for large university
python oxylabs_integration.py https://university.edu 100 \
    --deep-crawl=100 \
    --ai-url-filter \
    --use-ai \
    --ai-model=openai/gpt-4o-mini \
    --workers=30

# Expected results:
# - Discovers 500-1000 URLs via deep crawling
# - AI filters to top 100 URLs
# - Scrapes only the most promising pages
# - Total AI cost: ~$0.010 (URL filtering) + $0.050 (extraction)
# - Time saved: 5-10 minutes vs scraping all URLs
```

## 🔮 Future Enhancements

Potential improvements:
- Confidence score display in web UI
- URL similarity clustering
- Historical success rate tracking
- Custom domain-specific patterns
- A/B testing AI vs keyword-only

---

**Happy Scraping! 🎯🚀**

