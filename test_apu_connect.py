#!/usr/bin/env python
"""
Test APU Connect URL specifically with Oxylabs
"""

import requests
import base64
import json
import re
from bs4 import BeautifulSoup


def test_apu_connect():
    """Test the APU connect URL specifically."""
    
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
    test_url = "https://www.apu.edu.my/connect"
    
    # Try different payload configurations
    payloads = [
        {
            "name": "Basic Universal",
            "payload": {
                "source": "universal",
                "url": test_url,
                "render": "html",
                "geo_location": "my"
            }
        },
        {
            "name": "Universal with Parse",
            "payload": {
                "source": "universal",
                "url": test_url,
                "render": "html",
                "geo_location": "my",
                "parse": True
            }
        },
        {
            "name": "Universal without Parse",
            "payload": {
                "source": "universal",
                "url": test_url,
                "render": "html",
                "geo_location": "my",
                "parse": False
            }
        },
        {
            "name": "Universal with Custom Headers",
            "payload": {
                "source": "universal",
                "url": test_url,
                "render": "html",
                "geo_location": "my",
                "parse": False,
                "custom_headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
            }
        }
    ]
    
    print("=" * 80)
    print("Testing APU Connect URL with Oxylabs")
    print("=" * 80)
    print(f"URL: {test_url}")
    print(f"Username: {username}")
    print("=" * 80)
    
    for i, config in enumerate(payloads, 1):
        print(f"\n--- Test {i}: {config['name']} ---")
        
        try:
            response = requests.post(base_url, headers=headers, json=config['payload'], timeout=60)
            
            print(f"Response Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("results") and len(result["results"]) > 0:
                    content_data = result["results"][0]
                    
                    print(f"+ Success - Status: {content_data.get('status_code')}")
                    print(f"  Parse Status: {content_data.get('content', {}).get('parse_status_code', 'N/A')}")
                    print(f"  Job ID: {content_data.get('job_id')}")
                    
                    # Check content
                    content = content_data.get('content', {})
                    if isinstance(content, str) and len(content) > 100:
                        print(f"  + Got content: {len(content)} characters")
                        
                        # Parse with BeautifulSoup
                        soup = BeautifulSoup(content, 'html.parser')
                        
                        # Look for contact information
                        all_text = soup.get_text()
                        
                        # Search for emails
                        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
                        emails = email_pattern.findall(all_text)
                        
                        # Search for phones
                        phone_pattern = re.compile(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}|\+?\d{10,}')
                        phones = phone_pattern.findall(all_text)
                        
                        print(f"  Found {len(emails)} email addresses:")
                        for email in emails[:10]:
                            print(f"    - {email}")
                        
                        print(f"  Found {len(phones)} phone numbers:")
                        for phone in phones[:10]:
                            print(f"    - {phone}")
                        
                        # Look for specific contact elements
                        contact_elements = soup.find_all(['a', 'div', 'span'], string=re.compile(r'@|phone|contact|email', re.I))
                        print(f"  Found {len(contact_elements)} contact-related elements")
                        
                        # Show first few contact elements
                        for elem in contact_elements[:5]:
                            print(f"    - {elem.get_text().strip()[:100]}...")
                        
                        return True  # Success!
                        
                    elif isinstance(content, dict):
                        print(f"  Content structure: {list(content.keys())}")
                        if 'html' in content:
                            print(f"  + Got HTML: {len(content['html'])} characters")
                        elif 'text' in content:
                            print(f"  + Got text: {len(content['text'])} characters")
                        else:
                            print(f"  Content: {content}")
                    else:
                        print(f"  Content type: {type(content)}, length: {len(str(content))}")
                else:
                    print("- No results returned")
            else:
                print(f"- Error {response.status_code}: {response.text[:200]}")
                
        except Exception as e:
            print(f"- Exception: {e}")
    
    print("\n" + "=" * 80)
    print("Testing Complete!")
    print("=" * 80)
    return False


if __name__ == "__main__":
    success = test_apu_connect()
    if success:
        print("\nSUCCESS: Found contact information!")
    else:
        print("\nFAILED: No contact information found.")
