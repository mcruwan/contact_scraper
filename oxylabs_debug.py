#!/usr/bin/env python
"""
Oxylabs Debug Script - Shows what content we're getting and improves extraction
"""

import requests
import base64
import json
import re
from bs4 import BeautifulSoup


def test_oxylabs_api():
    """Test Oxylabs API and show what content we get."""
    
    # Oxylabs credentials
    username = "mcruwan_6Grof"
    password = "NewAdmin_123"
    
    # API configuration
    base_url = "https://realtime.oxylabs.io/v1/queries"
    auth_string = base64.b64encode(f"{username}:{password}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth_string}",
        "Content-Type": "application/json"
    }
    
    # Test URL
    test_url = "https://ucsiuniversity.edu.my"
    
    payload = {
        "source": "universal",
        "url": test_url,
        "render": "html",
        "geo_location": "us",
        "parse": True,
        "context": [
            {
                "key": "page_type",
                "value": "university_contact"
            }
        ]
    }
    
    print("=" * 70)
    print("Oxylabs API Debug - UCSI University")
    print("=" * 70)
    print(f"Testing URL: {test_url}")
    print(f"Username: {username}")
    print("=" * 70)
    
    try:
        print("Sending request to Oxylabs API...")
        response = requests.post(base_url, headers=headers, json=payload, timeout=60)
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("results") and len(result["results"]) > 0:
                content_data = result["results"][0]
                
                print(f"Job ID: {content_data.get('job_id')}")
                print(f"Status Code: {content_data.get('status_code')}")
                print(f"Parse Status: {content_data.get('content', {}).get('parse_status_code')}")
                print(f"URL: {content_data.get('url')}")
                
                # Get the actual HTML content - check different possible structures
                html_content = None
                
                if 'content' in content_data:
                    if isinstance(content_data['content'], str):
                        html_content = content_data['content']
                    elif 'html' in content_data['content']:
                        html_content = content_data['content']['html']
                    elif 'text' in content_data['content']:
                        html_content = content_data['content']['text']
                
                if html_content:
                    print(f"\nHTML Content Length: {len(html_content)} characters")
                    
                    # Show first 1000 characters
                    print("\nFirst 1000 characters of HTML:")
                    print("-" * 50)
                    print(html_content[:1000])
                    print("-" * 50)
                    
                    # Parse with BeautifulSoup
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    # Look for any text that might contain contact info
                    all_text = soup.get_text()
                    
                    # Search for emails
                    email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
                    emails = email_pattern.findall(all_text)
                    
                    # Search for phones
                    phone_pattern = re.compile(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}|\+?\d{10,}')
                    phones = phone_pattern.findall(all_text)
                    
                    print(f"\nFound {len(emails)} email addresses:")
                    for email in emails[:10]:  # Show first 10
                        print(f"  - {email}")
                    
                    print(f"\nFound {len(phones)} phone numbers:")
                    for phone in phones[:10]:  # Show first 10
                        print(f"  - {phone}")
                    
                    # Look for specific elements that might contain contact info
                    print("\nLooking for contact-related elements...")
                    
                    # Check for common contact selectors
                    contact_selectors = [
                        'a[href^="mailto:"]',
                        'a[href^="tel:"]',
                        '.contact',
                        '.email',
                        '.phone',
                        '.staff',
                        '.faculty',
                        '.person'
                    ]
                    
                    for selector in contact_selectors:
                        elements = soup.select(selector)
                        if elements:
                            print(f"Found {len(elements)} elements with selector '{selector}'")
                            for i, elem in enumerate(elements[:3]):  # Show first 3
                                print(f"  {i+1}. {elem.get_text().strip()[:100]}...")
                    
                    # Look for any links
                    links = soup.find_all('a', href=True)
                    print(f"\nFound {len(links)} total links")
                    
                    # Look for contact-related links
                    contact_links = []
                    for link in links:
                        href = link.get('href', '')
                        text = link.get_text().strip().lower()
                        if any(keyword in href.lower() or keyword in text for keyword in 
                               ['contact', 'staff', 'faculty', 'email', 'phone', 'directory']):
                            contact_links.append((href, text))
                    
                    print(f"Found {len(contact_links)} contact-related links:")
                    for href, text in contact_links[:10]:  # Show first 10
                        print(f"  - {href} ({text})")
                    
                else:
                    print("No HTML content found in response")
                    print("Content structure:")
                    print(json.dumps(content_data.get('content', {}), indent=2))
                    print("\nFull response structure:")
                    print(json.dumps(content_data, indent=2)[:2000])
                    
            else:
                print("No results in response")
                print("Full response:")
                print(json.dumps(result, indent=2))
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_oxylabs_api()
