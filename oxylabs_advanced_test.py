#!/usr/bin/env python
"""
Advanced Oxylabs Test - Try different source types and configurations
"""

import requests
import base64
import json
import time


def test_oxylabs_different_sources():
    """Test different Oxylabs source types to find the best one."""
    
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
    
    # Different source types to try
    source_configs = [
        {
            "name": "Universal (Default)",
            "payload": {
                "source": "universal",
                "url": test_url,
                "render": "html",
                "geo_location": "us",
                "parse": True
            }
        },
        {
            "name": "Universal with JavaScript",
            "payload": {
                "source": "universal",
                "url": test_url,
                "render": "html",
                "geo_location": "us",
                "parse": False,
                "render_options": {
                    "wait": 3000
                }
            }
        },
        {
            "name": "Google Search",
            "payload": {
                "source": "google_search",
                "query": "site:ucsiuniversity.edu.my contact faculty staff",
                "geo_location": "us"
            }
        },
        {
            "name": "Universal with Malaysia location",
            "payload": {
                "source": "universal",
                "url": test_url,
                "render": "html",
                "geo_location": "my",  # Malaysia
                "parse": False
            }
        },
        {
            "name": "Universal with different user agent",
            "payload": {
                "source": "universal",
                "url": test_url,
                "render": "html",
                "geo_location": "us",
                "parse": False,
                "custom_headers": {
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
            }
        }
    ]
    
    print("=" * 80)
    print("Advanced Oxylabs Testing - Different Source Types")
    print("=" * 80)
    print(f"Testing URL: {test_url}")
    print(f"Username: {username}")
    print("=" * 80)
    
    for i, config in enumerate(source_configs, 1):
        print(f"\n--- Test {i}: {config['name']} ---")
        
        try:
            response = requests.post(base_url, headers=headers, json=config['payload'], timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("results") and len(result["results"]) > 0:
                    content_data = result["results"][0]
                    
                    print(f"+ Success - Status: {content_data.get('status_code')}")
                    print(f"  Parse Status: {content_data.get('content', {}).get('parse_status_code', 'N/A')}")
                    print(f"  Job ID: {content_data.get('job_id')}")
                    
                    # Check if we got actual content
                    content = content_data.get('content', {})
                    if isinstance(content, str) and len(content) > 100:
                        print(f"  + Got content: {len(content)} characters")
                        # Show first 200 characters
                        print(f"  Preview: {content[:200]}...")
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
        
        # Wait between requests
        if i < len(source_configs):
            print("  Waiting 3 seconds...")
            time.sleep(3)
    
    print("\n" + "=" * 80)
    print("Testing Complete!")
    print("=" * 80)


def test_simple_website():
    """Test with a simple website to verify Oxylabs is working."""
    
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
    
    # Test with a simple website
    test_url = "https://httpbin.org/html"
    
    payload = {
        "source": "universal",
        "url": test_url,
        "render": "html",
        "geo_location": "us",
        "parse": False
    }
    
    print("\n" + "=" * 80)
    print("Testing Oxylabs with Simple Website (httpbin.org)")
    print("=" * 80)
    
    try:
        response = requests.post(base_url, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("results") and len(result["results"]) > 0:
                content_data = result["results"][0]
                
                print(f"+ Success - Status: {content_data.get('status_code')}")
                print(f"  Parse Status: {content_data.get('content', {}).get('parse_status_code', 'N/A')}")
                
                content = content_data.get('content', {})
                if isinstance(content, str) and len(content) > 100:
                    print(f"  + Got content: {len(content)} characters")
                    print(f"  Preview: {content[:300]}...")
                else:
                    print(f"  Content: {content}")
            else:
                print("- No results returned")
        else:
            print(f"- Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"- Exception: {e}")


if __name__ == "__main__":
    test_oxylabs_different_sources()
    test_simple_website()
