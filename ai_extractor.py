#!/usr/bin/env python
"""
AI-Powered Contact Extraction using OpenRouter
Uses LLMs to intelligently extract names, designations, and other contact info from HTML context
"""

import requests
import json
import os
from typing import Dict, Optional

# Try to import config for API key
try:
    from config import OPENROUTER_API_KEY as CONFIG_API_KEY
except ImportError:
    CONFIG_API_KEY = None


class AIContactExtractor:
    """
    Uses OpenRouter API to extract contact information from HTML context using AI.
    Supports multiple models: GPT-4, Claude, Llama, etc.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "openai/gpt-4o-mini"):
        """
        Initialize the AI extractor.
        
        Args:
            api_key: OpenRouter API key (or set OPENROUTER_API_KEY env var)
            model: Model to use. Options:
                - "openai/gpt-4o-mini" (Recommended: Fast, cheap, accurate)
                - "anthropic/claude-3-haiku" (Good alternative)
                - "meta-llama/llama-3.1-8b-instruct" (Free tier)
                - "google/gemini-flash-1.5" (Fast and free)
        """
        # Try multiple sources for API key: parameter > env var > config file
        self.api_key = api_key or os.environ.get('OPENROUTER_API_KEY') or CONFIG_API_KEY
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.enabled = bool(self.api_key)
        
        # Token usage tracking
        self.total_tokens_used = 0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0
        self.total_requests = 0
        
        # URL analysis tracking (separate from contact extraction)
        self.url_analysis_tokens = 0
        self.url_analysis_cost = 0.0
        self.url_analysis_requests = 0
        
        if not self.enabled:
            print("⚠️  AI extraction disabled: No OpenRouter API key found")
            print("   Set OPENROUTER_API_KEY environment variable or pass api_key parameter")
        else:
            print(f"✓ AI extraction enabled using model: {model}")
    
    def extract_contact_info(self, html_context: str, email: str, max_retries: int = 2) -> Dict:
        """
        Extract contact information from HTML context using AI.
        
        Args:
            html_context: HTML snippet containing the email and surrounding context
            email: The email address found
            max_retries: Number of retries on failure
        
        Returns:
            Dict with extracted fields: name, designation, phone, department
        """
        if not self.enabled:
            return {}
        
        # Limit context size (most models have token limits)
        if len(html_context) > 4000:
            html_context = html_context[:4000]
        
        prompt = self._build_extraction_prompt(html_context, email)
        
        for attempt in range(max_retries + 1):
            try:
                result = self._call_openrouter(prompt)
                return result
            except Exception as e:
                if attempt < max_retries:
                    print(f"  AI extraction attempt {attempt + 1} failed, retrying...")
                    continue
                else:
                    print(f"  AI extraction failed after {max_retries + 1} attempts: {e}")
                    return {}
        
        return {}
    
    def _build_extraction_prompt(self, html_context: str, email: str) -> str:
        """Build the prompt for AI extraction."""
        return f"""Extract contact information from the HTML context below. The email address "{email}" was found in this content.

Your task: Find the person's name, job title/designation, phone number, and department associated with this email.

HTML Context:
{html_context}

Instructions:
1. Look for the person's full name near the email address
2. Extract their job title, position, or designation
3. Find any phone numbers (including international formats)
4. Identify the department or unit they belong to
5. If multiple people are present, choose the one closest to the email "{email}"
6. If a field cannot be found, return null for that field

Return ONLY a JSON object with these exact fields (no other text):
{{
  "name": "Full Name or null",
  "designation": "Job Title/Position or null",
  "phone": "Phone Number or null",
  "department": "Department Name or null"
}}

Rules:
- Name should NOT contain the email address
- Avoid generic terms like "Contact Us" or "Email"
- For names with titles (Dr., Prof.), include the title
- Phone should be in original format
- Keep it concise and accurate"""
    
    def _call_openrouter(self, prompt: str, timeout: int = 30) -> Dict:
        """
        Call OpenRouter API to get AI response.
        
        Args:
            prompt: The extraction prompt
            timeout: Request timeout in seconds
        
        Returns:
            Extracted contact information as dict
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/university-contact-scraper",  # Optional: for OpenRouter analytics
            "X-Title": "University Contact Scraper"  # Optional: app name
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1,  # Low temperature for consistent extraction
            "max_tokens": 300,   # Enough for contact info
            "response_format": {"type": "json_object"} if "gpt" in self.model else None
        }
        
        # Remove response_format for models that don't support it
        if payload["response_format"] is None:
            del payload["response_format"]
        
        response = requests.post(
            self.base_url,
            headers=headers,
            json=payload,
            timeout=timeout
        )
        
        if response.status_code != 200:
            raise Exception(f"OpenRouter API error {response.status_code}: {response.text}")
        
        result = response.json()
        
        # Track token usage from response
        if "usage" in result:
            usage = result["usage"]
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            total_tokens = usage.get("total_tokens", prompt_tokens + completion_tokens)
            
            self.total_input_tokens += prompt_tokens
            self.total_output_tokens += completion_tokens
            self.total_tokens_used += total_tokens
            self.total_requests += 1
            
            # Calculate cost based on model pricing (per 1M tokens)
            cost = self._calculate_cost(prompt_tokens, completion_tokens)
            self.total_cost += cost
        
        # Extract the response content
        content = result["choices"][0]["message"]["content"]
        
        # Parse JSON from response
        try:
            # Sometimes models wrap JSON in markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            extracted_data = json.loads(content)
            
            # Clean and validate extracted data
            return self._clean_extracted_data(extracted_data)
            
        except json.JSONDecodeError as e:
            print(f"  Failed to parse AI response as JSON: {e}")
            print(f"  Raw response: {content[:200]}")
            return {}
    
    def _clean_extracted_data(self, data: Dict) -> Dict:
        """
        Clean and validate extracted data.
        
        Args:
            data: Raw extracted data from AI
        
        Returns:
            Cleaned data with None for invalid fields
        """
        cleaned = {
            'name': None,
            'designation': None,
            'phone': None,
            'department': None
        }
        
        # Clean name
        name = data.get('name')
        if name and isinstance(name, str):
            name = name.strip()
            # Reject if it looks like an email or contains @
            if name and len(name) > 2 and '@' not in name.lower():
                # Reject common non-names
                if not any(bad in name.lower() for bad in ['contact', 'email', 'click here', 'n/a', 'null', 'none']):
                    cleaned['name'] = name
        
        # Clean designation
        designation = data.get('designation')
        if designation and isinstance(designation, str):
            designation = designation.strip()
            if designation and len(designation) > 2 and designation.lower() not in ['n/a', 'null', 'none']:
                cleaned['designation'] = designation
        
        # Clean phone
        phone = data.get('phone')
        if phone and isinstance(phone, str):
            phone = phone.strip()
            if phone and len(phone) >= 7 and phone.lower() not in ['n/a', 'null', 'none']:
                cleaned['phone'] = phone
        
        # Clean department
        department = data.get('department')
        if department and isinstance(department, str):
            department = department.strip()
            if department and len(department) > 2 and department.lower() not in ['n/a', 'null', 'none']:
                cleaned['department'] = department
        
        return cleaned
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Calculate the actual cost for a request based on token usage.
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
        
        Returns:
            Cost in USD
        """
        # Pricing per 1M tokens (as of 2024)
        pricing = {
            "openai/gpt-4o-mini": {"input": 0.15, "output": 0.60},
            "openai/gpt-4o": {"input": 2.50, "output": 10.00},
            "openai/gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
            "anthropic/claude-3-haiku": {"input": 0.25, "output": 1.25},
            "anthropic/claude-3-sonnet": {"input": 3.00, "output": 15.00},
            "meta-llama/llama-3.1-8b-instruct": {"input": 0.06, "output": 0.06},
            "meta-llama/llama-3.1-70b-instruct": {"input": 0.35, "output": 0.40},
            "google/gemini-flash-1.5": {"input": 0.075, "output": 0.30},
            "google/gemini-pro-1.5": {"input": 1.25, "output": 5.00}
        }
        
        model_pricing = pricing.get(self.model, {"input": 0.15, "output": 0.60})
        
        input_cost = (input_tokens * model_pricing["input"]) / 1_000_000
        output_cost = (output_tokens * model_pricing["output"]) / 1_000_000
        
        return input_cost + output_cost
    
    def get_usage_stats(self) -> Dict:
        """
        Get current usage statistics.
        
        Returns:
            Dict with usage stats including tokens and cost
        """
        return {
            'total_requests': self.total_requests,
            'total_tokens': self.total_tokens_used,
            'input_tokens': self.total_input_tokens,
            'output_tokens': self.total_output_tokens,
            'total_cost': round(self.total_cost, 6),
            'avg_tokens_per_request': round(self.total_tokens_used / max(1, self.total_requests), 1),
            'model': self.model,
            'url_analysis': {
                'requests': self.url_analysis_requests,
                'tokens': self.url_analysis_tokens,
                'cost': round(self.url_analysis_cost, 6)
            }
        }
    
    def analyze_urls_for_contacts(self, urls: list, max_retries: int = 2) -> list:
        """
        Analyze a batch of URLs to predict which ones likely contain contact information.
        
        Args:
            urls: List of URLs to analyze
            max_retries: Number of retries on failure
        
        Returns:
            List of dicts with url, likelihood (0-1), and reasoning
        """
        if not self.enabled or not urls:
            return []
        
        # Limit batch size for token efficiency
        if len(urls) > 50:
            print(f"  Analyzing URLs in batches of 50...")
            results = []
            for i in range(0, len(urls), 50):
                batch = urls[i:i+50]
                batch_results = self.analyze_urls_for_contacts(batch, max_retries)
                results.extend(batch_results)
            return results
        
        prompt = self._build_url_analysis_prompt(urls)
        
        for attempt in range(max_retries + 1):
            try:
                result = self._call_openrouter_for_urls(prompt)
                return result
            except Exception as e:
                if attempt < max_retries:
                    print(f"  URL analysis attempt {attempt + 1} failed, retrying...")
                    continue
                else:
                    print(f"  URL analysis failed after {max_retries + 1} attempts: {e}")
                    return []
        
        return []
    
    def _build_url_analysis_prompt(self, urls: list) -> str:
        """Build prompt for URL analysis."""
        urls_list = "\n".join(f"{i+1}. {url}" for i, url in enumerate(urls))
        
        return f"""Analyze these {len(urls)} university website URLs and predict the likelihood (0.0 to 1.0) that each URL contains contact information (emails, phone numbers, staff profiles).

URLs to analyze:
{urls_list}

Consider:
- URLs with "contact", "staff", "faculty", "directory", "people" are likely (0.8-1.0)
- URLs with "about", "team", "profile", "email" are moderately likely (0.5-0.8)
- URLs with names (john-doe, jane-smith) in staff/faculty paths are likely (0.7-0.9)
- URLs with "news", "events", "blog", "courses", "programs" are unlikely (0.1-0.3)
- Homepage and general pages are low (0.2-0.4)

Return ONLY a JSON array (no other text):
[
  {{"url": "exact_url_from_list", "likelihood": 0.95, "reason": "staff directory page"}},
  {{"url": "exact_url_from_list", "likelihood": 0.15, "reason": "news archive"}}
]

Return one object for each URL in the same order."""
    
    def _call_openrouter_for_urls(self, prompt: str, timeout: int = 30) -> list:
        """Call OpenRouter API for URL analysis."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/university-contact-scraper",
            "X-Title": "University Contact Scraper - URL Analysis"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1,
            "max_tokens": 2000,
            "response_format": {"type": "json_object"} if "gpt" in self.model else None
        }
        
        if payload["response_format"] is None:
            del payload["response_format"]
        
        response = requests.post(
            self.base_url,
            headers=headers,
            json=payload,
            timeout=timeout
        )
        
        if response.status_code != 200:
            raise Exception(f"OpenRouter API error {response.status_code}: {response.text}")
        
        result = response.json()
        
        # Track URL analysis token usage separately
        if "usage" in result:
            usage = result["usage"]
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            total_tokens = usage.get("total_tokens", prompt_tokens + completion_tokens)
            
            self.url_analysis_tokens += total_tokens
            self.url_analysis_requests += 1
            
            cost = self._calculate_cost(prompt_tokens, completion_tokens)
            self.url_analysis_cost += cost
        
        content = result["choices"][0]["message"]["content"]
        
        # Parse JSON
        try:
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            # Handle both array and object with array
            parsed = json.loads(content)
            if isinstance(parsed, dict) and 'urls' in parsed:
                return parsed['urls']
            elif isinstance(parsed, dict) and 'results' in parsed:
                return parsed['results']
            elif isinstance(parsed, list):
                return parsed
            else:
                print(f"  Unexpected JSON structure: {type(parsed)}")
                return []
                
        except json.JSONDecodeError as e:
            print(f"  Failed to parse URL analysis response: {e}")
            print(f"  Raw response: {content[:200]}")
            return []
    
    def get_cost_estimate(self, num_requests: int) -> Dict:
        """
        Estimate the cost for a given number of AI extraction requests.
        
        Args:
            num_requests: Number of expected AI extraction calls
        
        Returns:
            Dict with cost estimates for different models
        """
        # Approximate costs per 1M tokens (as of 2024)
        costs = {
            "openai/gpt-4o-mini": {"input": 0.15, "output": 0.60, "tokens_per_request": 2000},
            "anthropic/claude-3-haiku": {"input": 0.25, "output": 1.25, "tokens_per_request": 2000},
            "meta-llama/llama-3.1-8b-instruct": {"input": 0.06, "output": 0.06, "tokens_per_request": 2000},
            "google/gemini-flash-1.5": {"input": 0.075, "output": 0.30, "tokens_per_request": 2000}
        }
        
        estimates = {}
        for model, pricing in costs.items():
            total_tokens = num_requests * pricing["tokens_per_request"]
            input_cost = (total_tokens * pricing["input"]) / 1_000_000
            output_cost = (total_tokens * 0.15 * pricing["output"]) / 1_000_000  # Assume 15% output
            total_cost = input_cost + output_cost
            
            estimates[model] = {
                "total_cost": round(total_cost, 4),
                "per_request": round(total_cost / num_requests, 6)
            }
        
        return estimates


def test_ai_extraction():
    """Test the AI extraction with a sample HTML snippet."""
    
    sample_html = """
    <div class="staff-profile">
        <h2>Dr. Jane Smith</h2>
        <p class="title">Associate Professor, Computer Science</p>
        <p>Email: <a href="mailto:jane.smith@university.edu">jane.smith@university.edu</a></p>
        <p>Phone: +1-555-123-4567</p>
        <p>Department of Computer Science and Engineering</p>
    </div>
    """
    
    print("\n" + "="*70)
    print("Testing AI Contact Extraction")
    print("="*70)
    
    extractor = AIContactExtractor()
    
    if not extractor.enabled:
        print("\n❌ Cannot test: No API key configured")
        print("\nTo enable AI extraction:")
        print("  1. Get an API key from https://openrouter.ai")
        print("  2. Set environment variable:")
        print("     export OPENROUTER_API_KEY='your-api-key-here'")
        return
    
    print(f"\nModel: {extractor.model}")
    print(f"\nSample HTML:\n{sample_html}\n")
    print("Extracting contact information...")
    
    result = extractor.extract_contact_info(sample_html, "jane.smith@university.edu")
    
    print("\n" + "="*70)
    print("Extraction Result:")
    print("="*70)
    print(json.dumps(result, indent=2))
    
    # Show cost estimate
    print("\n" + "="*70)
    print("Cost Estimates (for 100 extractions):")
    print("="*70)
    estimates = extractor.get_cost_estimate(100)
    for model, cost in estimates.items():
        print(f"\n{model}:")
        print(f"  Total: ${cost['total_cost']:.4f}")
        print(f"  Per request: ${cost['per_request']:.6f}")


if __name__ == "__main__":
    test_ai_extraction()

