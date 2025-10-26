# 🎯 Solution: Extracting Names and Designations

## Problem
Currently, the scraper only extracts **emails** but leaves **names**, **designations**, **phone numbers**, and other fields empty.

## Why This Happens
1. **Different HTML Structures**: Each university website has unique HTML layout
2. **Contextual Distance**: Names/titles are often far from email links in the HTML
3. **Selector Mismatch**: Our CSS selectors (`.name`, `.designation`) don't match the actual classes used
4. **Plain Text Emails**: Emails in plain text (not `mailto:` links) have no surrounding HTML structure

---

## 🔧 **Solution Options**

### **Option 1: Enhanced Contextual Extraction** (Quick Fix)
Improve the existing scraper to better find names near emails.

**Pros:**
- ✅ No additional API costs
- ✅ Works with current setup
- ✅ Fast implementation

**Cons:**
- ❌ Not 100% accurate
- ❌ Depends on website structure
- ❌ May miss some names

**Implementation:**
I'll enhance the contextual extraction with:
- Smarter proximity search (look at parent/sibling elements)
- Better name pattern recognition (Dr., Prof., Mr., Ms.)
- Improved HTML traversal logic
- Phone number extraction from surrounding text

---

### **Option 2: Oxylabs Custom Parser** (Most Accurate) ⭐
Use Oxylabs' AI-powered parsing to extract structured data.

**Pros:**
- ✅ Most accurate extraction
- ✅ Handles different website structures
- ✅ Extracts full contact cards
- ✅ Professional results

**Cons:**
- ❌ Requires custom parser setup
- ❌ May use more API quota
- ❌ Site-specific configuration needed

**How it works:**
Define the data structure you want, and Oxylabs' AI extracts it:
```python
parsing_instructions = {
    "contacts": {
        "_fns": [{
            "_fn": "xpath_one",
            "_args": ["//div[contains(@class, 'contact')]"]
        }],
        "_items": {
            "name": {
                "_fns": [{
                    "_fn": "xpath_one",
                    "_args": [".//h3 | .//strong"]
                }]
            },
            "email": {
                "_fns": [{
                    "_fn": "xpath_one",
                    "_args": [".//a[contains(@href, 'mailto:')]/@href"]
                }]
            }
        }
    }
}
```

---

### **Option 3: LLM-Based Extraction** (Most Flexible)
Send the HTML to an AI model (like Claude or GPT) to extract contacts.

**Pros:**
- ✅ Handles ANY website structure
- ✅ Very intelligent extraction
- ✅ Can understand context and relationships
- ✅ Extracts even complex data

**Cons:**
- ❌ Additional API costs (OpenAI/Anthropic)
- ❌ Slower (one page at a time)
- ❌ More expensive per page
- ❌ Rate limits

**How it works:**
Send HTML to AI with prompt:
```
"Extract all contact information from this HTML including names, 
emails, phone numbers, and job titles. Return as JSON."
```

---

## 🚀 **Recommended Approach**

### **Immediate Solution: Enhanced Contextual Extraction**

I'll implement this now with these improvements:

1. **Smarter Name Detection**
   - Look for titles: Dr., Prof., Professor, Dean, etc.
   - Detect capitalized names (John Smith, Mary Johnson)
   - Check parent/sibling elements more thoroughly

2. **Better Phone Extraction**
   - Find `tel:` links
   - Detect phone patterns in surrounding text
   - Check nearby elements for contact info

3. **Improved Context Radius**
   - Expand search to grandparent elements
   - Check adjacent list items
   - Look at entire card/section containers

4. **Name Pattern Recognition**
   - Use regex to find names: `[A-Z][a-z]+ [A-Z][a-z]+`
   - Filter out common words (Contact, Email, Phone)
   - Prioritize text with titles (Dr., Prof.)

---

## 📊 **Expected Improvement**

### Before Enhancement:
```csv
email,phone,name,designation
[email protected],,,
```

### After Enhancement:
```csv
email,phone,name,designation
[email protected],+1-234-567-8900,Dr. John Smith,Professor of Computer Science
```

**Estimated Success Rate:**
- Names: 40-60% (up from 0%)
- Designations: 30-50% (up from 0%)
- Phone: 20-40% (up from 0%)

---

## 🎯 **Long-Term Solution**

### **Hybrid Approach:**
1. **Primary**: Enhanced contextual extraction (fast, free)
2. **Fallback**: For pages with no names found, use LLM extraction
3. **Optimization**: Learn patterns from successful extractions

### **Site-Specific Optimization:**
Create custom extraction rules for frequently scraped universities:
```python
site_configs = {
    "ucsiuniversity.edu.my": {
        "name_selector": ".staff-name",
        "designation_selector": ".staff-title",
        "phone_selector": ".contact-phone"
    },
    "sunwayuniversity.edu.my": {
        "name_selector": "h2.faculty-name",
        "designation_selector": ".position"
    }
}
```

---

## ⚡ **Let's Implement Enhanced Extraction Now**

Would you like me to:
1. ✅ **Implement Enhanced Contextual Extraction** (Recommended - immediate improvement)
2. Set up Oxylabs Custom Parser (better accuracy, site-specific)
3. Implement LLM-based extraction (most flexible, higher cost)
4. Create a hybrid approach (best of all worlds)

**I recommend starting with Option 1** - it will give you immediate improvement (40-60% name extraction vs 0% now) without any additional costs or complexity.

Shall I implement the enhanced contextual extraction now?

