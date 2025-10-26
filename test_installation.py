#!/usr/bin/env python
"""
Test script to verify the scraper installation is working correctly.
"""

import sys
import os

def test_imports():
    """Test if all required packages can be imported."""
    print("Testing package imports...")
    
    try:
        import scrapy
        print("+ Scrapy imported successfully")
    except ImportError as e:
        print(f"- Failed to import Scrapy: {e}")
        return False
    
    try:
        import pandas
        print("+ Pandas imported successfully")
    except ImportError as e:
        print(f"- Failed to import Pandas: {e}")
        return False
    
    try:
        import openpyxl
        print("+ OpenPyXL imported successfully")
    except ImportError as e:
        print(f"- Failed to import OpenPyXL: {e}")
        return False
    
    try:
        import scrapy_user_agents
        print("+ Scrapy User Agents imported successfully")
    except ImportError as e:
        print(f"- Failed to import Scrapy User Agents: {e}")
        return False
    
    return True

def test_project_structure():
    """Test if the project structure is correct."""
    print("\nTesting project structure...")
    
    required_files = [
        'scrapy.cfg',
        'run.py',
        'requirements.txt',
        'uni_scraper/__init__.py',
        'uni_scraper/items.py',
        'uni_scraper/settings.py',
        'uni_scraper/pipelines.py',
        'uni_scraper/spiders/__init__.py',
        'uni_scraper/spiders/contact_spider.py'
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"+ {file_path}")
        else:
            print(f"- {file_path} - MISSING")
            all_exist = False
    
    return all_exist

def test_scrapy_config():
    """Test if Scrapy can load the project configuration."""
    print("\nTesting Scrapy configuration...")
    
    try:
        from scrapy.utils.project import get_project_settings
        settings = get_project_settings()
        print("+ Scrapy settings loaded successfully")
        print(f"  - Bot name: {settings.get('BOT_NAME')}")
        print(f"  - Concurrent requests: {settings.get('CONCURRENT_REQUESTS')}")
        print(f"  - Download delay: {settings.get('DOWNLOAD_DELAY')}")
        return True
    except Exception as e:
        print(f"- Failed to load Scrapy settings: {e}")
        return False

def test_spider_import():
    """Test if the spider can be imported."""
    print("\nTesting spider import...")
    
    try:
        from uni_scraper.spiders.contact_spider import ContactSpider
        print("+ Contact spider imported successfully")
        return True
    except Exception as e:
        print(f"- Failed to import contact spider: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("University Contact Scraper - Installation Test")
    print("=" * 60)
    
    tests = [
        ("Package Imports", test_imports),
        ("Project Structure", test_project_structure),
        ("Scrapy Configuration", test_scrapy_config),
        ("Spider Import", test_spider_import)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"  - {test_name} failed")
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("SUCCESS! All tests passed! Your scraper is ready to use.")
        print("\nNext steps:")
        print("1. Run: python run.py --help")
        print("2. Test with: python run.py https://example.com --max-pages 5")
        print("3. Check the output/ directory for results")
    else:
        print("ERROR! Some tests failed. Please check the errors above.")
        print("\nTroubleshooting:")
        print("1. Make sure you're in the correct directory")
        print("2. Run: pip install -r requirements.txt")
        print("3. Check that all files are present")
    
    print("=" * 60)
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
