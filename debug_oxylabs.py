#!/usr/bin/env python
"""
Debug Oxylabs response to understand the content structure
"""

import requests
import base64
import json


def debug_oxylabs_response():
    """Debug what we're actually getting from Oxylabs."""
    
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
    
    payload = {
        "source": "universal",
        "url": test_url,
        "render": "html",
        "geo_location": "my",
        "parse": False
    }
    
    print("=" * 80)
    print("Debugging Oxylabs Response")
    print("=" * 80)
    print(f"URL: {test_url}")
    print("=" * 80)
    
    try:
        response = requests.post(base_url, headers=headers, json=payload, timeout=60)
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("results") and len(result["results"]) > 0:
                content_data = result["results"][0]
                
                print(f"Job ID: {content_data.get('job_id')}")
                print(f"Status Code: {content_data.get('status_code')}")
                print(f"Parse Status: {content_data.get('content', {}).get('parse_status_code', 'N/A')}")
                print(f"URL: {content_data.get('url')}")
                
                # Check the content structure
                content = content_data.get('content', {})
                print(f"\nContent type: {type(content)}")
                print(f"Content keys: {list(content.keys()) if isinstance(content, dict) else 'Not a dict'}")
                
                if isinstance(content, dict):
                    for key, value in content.items():
                        if isinstance(value, str):
                            print(f"  {key}: {len(value)} characters")
                            if len(value) > 100:
                                print(f"    Preview: {value[:200]}...")
                        else:
                            print(f"  {key}: {type(value)} - {value}")
                elif isinstance(content, str):
                    print(f"Content (string): {len(content)} characters")
                    print(f"Preview: {content[:500]}...")
                else:
                    print(f"Content: {content}")
                
                # Save full response for inspection
                with open('oxylabs_debug_response.json', 'w') as f:
                    json.dump(content_data, f, indent=2)
                print(f"\nFull response saved to: oxylabs_debug_response.json")
                
            else:
                print("No results in response")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_oxylabs_response()

