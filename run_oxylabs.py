#!/usr/bin/env python
"""
Oxylabs-Enhanced Runner Script for University Contact Scraper

This script uses Oxylabs Web Scraper API to bypass anti-bot protection
and scrape protected websites like UCSI University.

Usage:
    python run_oxylabs.py https://ucsiuniversity.edu.my
    python run_oxylabs.py https://ucsiuniversity.edu.my --max-pages 10
"""

import sys
import os
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from uni_scraper.spiders.oxylabs_spider import OxylabsContactSpider


def main():
    """Main entry point for the Oxylabs-enhanced scraper."""
    
    # Check if URL is provided
    if len(sys.argv) < 2 or '--help' in sys.argv or '-h' in sys.argv:
        print("=" * 70)
        print("Oxylabs-Enhanced University Contact Scraper")
        print("=" * 70)
        print("\nUsage:")
        print("  python run_oxylabs.py <URL> [OPTIONS]\n")
        print("Arguments:")
        print("  URL                  Starting URL to scrape (required)\n")
        print("Options:")
        print("  --max-pages N        Maximum number of pages to scrape (default: unlimited)")
        print("  --max-depth N        Maximum crawl depth (default: 5)")
        print("  --output FILE        Output filename (without extension)")
        print("  --domain DOMAIN      Restrict crawling to specific domain")
        print("  --help, -h           Show this help message\n")
        print("Examples:")
        print("  python run_oxylabs.py https://ucsiuniversity.edu.my")
        print("  python run_oxylabs.py https://ucsiuniversity.edu.my --max-pages 10")
        print("  python run_oxylabs.py https://ucsiuniversity.edu.my --output ucsi_contacts")
        print("\nNote: This scraper uses Oxylabs API to bypass anti-bot protection.")
        print("Make sure you have valid Oxylabs credentials configured.")
        print("=" * 70)
        sys.exit(0)
    
    # Parse arguments
    start_url = sys.argv[1]
    max_pages = None
    max_depth = 5
    output_name = None
    allowed_domain = None
    
    # Parse optional arguments
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--max-pages' and i + 1 < len(sys.argv):
            max_pages = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '--max-depth' and i + 1 < len(sys.argv):
            max_depth = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '--output' and i + 1 < len(sys.argv):
            output_name = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--domain' and i + 1 < len(sys.argv):
            allowed_domain = sys.argv[i + 1]
            i += 2
        else:
            i += 1
    
    # Oxylabs credentials (you can also set these as environment variables)
    username = os.getenv('OXYLABS_USERNAME', 'mcruwan_6Grof')
    password = os.getenv('OXYLABS_PASSWORD', 'NewAdmin_123')
    
    # Create output directory if it doesn't exist
    os.makedirs('output', exist_ok=True)
    
    # Get project settings
    settings = get_project_settings()
    
    # Override settings for Oxylabs
    settings.set('ROBOTSTXT_OBEY', False)  # Disable robots.txt for protected sites
    settings.set('DOWNLOAD_DELAY', 2)  # Add delay between Oxylabs API calls
    settings.set('CONCURRENT_REQUESTS', 1)  # Process one at a time
    settings.set('CONCURRENT_REQUESTS_PER_DOMAIN', 1)
    settings.set('CONCURRENT_REQUESTS_PER_IP', 1)
    
    # Override settings if specified
    if max_pages:
        settings.set('CLOSESPIDER_PAGECOUNT', max_pages)
    
    settings.set('DEPTH_LIMIT', max_depth)
    
    # Configure output files if custom name is provided
    if output_name:
        settings.set('FEEDS', {
            f'output/{output_name}.csv': {
                'format': 'csv',
                'encoding': 'utf-8',
                'store_empty': False,
                'fields': ['name', 'email', 'phone', 'designation', 'university', 'department', 'source_url', 'scraped_date'],
            },
            f'output/{output_name}.json': {
                'format': 'json',
                'encoding': 'utf-8',
                'indent': 4,
            },
        })
    else:
        # Default output with Oxylabs prefix
        settings.set('FEEDS', {
            'output/oxylabs_contacts_%(time)s.csv': {
                'format': 'csv',
                'encoding': 'utf-8',
                'store_empty': False,
                'fields': ['name', 'email', 'phone', 'designation', 'university', 'department', 'source_url', 'scraped_date'],
            },
            'output/oxylabs_contacts_%(time)s.json': {
                'format': 'json',
                'encoding': 'utf-8',
                'indent': 4,
            },
        })
    
    print("\n" + "=" * 70)
    print("Oxylabs-Enhanced University Contact Scraper")
    print("=" * 70)
    print(f"Start URL: {start_url}")
    print(f"Max Pages: {max_pages if max_pages else 'Unlimited'}")
    print(f"Max Depth: {max_depth}")
    if allowed_domain:
        print(f"Allowed Domain: {allowed_domain}")
    print(f"Oxylabs Username: {username}")
    print(f"Output Directory: output/")
    print("=" * 70 + "\n")
    
    # Create and configure the crawler process
    process = CrawlerProcess(settings)
    
    # Start the Oxylabs spider
    process.crawl(
        OxylabsContactSpider,
        start_url=start_url,
        allowed_domain=allowed_domain,
        username=username,
        password=password
    )
    
    # Start crawling
    process.start()
    
    print("\n" + "=" * 70)
    print("Oxylabs Scraping completed!")
    print("=" * 70)
    print("Check the 'output/' directory for results (CSV and JSON files)")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()

