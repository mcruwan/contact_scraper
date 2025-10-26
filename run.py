#!/usr/bin/env python
"""
Simple runner script for the Uni Scraper.

Usage:
    python run.py https://example.com/contacts
    python run.py https://example.com/staff --max-pages 50
"""

import sys
import os
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from uni_scraper.spiders.contact_spider import ContactSpider


def main():
    """Main entry point for the scraper."""
    
    # Check if URL is provided or help is requested
    if len(sys.argv) < 2 or '--help' in sys.argv or '-h' in sys.argv:
        print("=" * 70)
        print("University Contact Scraper")
        print("=" * 70)
        print("\nUsage:")
        print("  python run.py <URL> [OPTIONS]\n")
        print("Arguments:")
        print("  URL                  Starting URL to scrape (required)\n")
        print("Options:")
        print("  --max-pages N        Maximum number of pages to scrape (default: unlimited)")
        print("  --max-depth N        Maximum crawl depth (default: 5)")
        print("  --output FILE        Output filename (without extension)")
        print("  --domain DOMAIN      Restrict crawling to specific domain")
        print("  --help, -h           Show this help message\n")
        print("Examples:")
        print("  python run.py https://example.com/contacts")
        print("  python run.py https://example.com/staff --max-pages 50")
        print("  python run.py https://example.com/directory --output staff_contacts")
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
    
    # Create output directory if it doesn't exist
    os.makedirs('output', exist_ok=True)
    
    # Get project settings
    settings = get_project_settings()
    
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
    
    print("\n" + "=" * 70)
    print("Starting University Contact Scraper")
    print("=" * 70)
    print(f"Start URL: {start_url}")
    print(f"Max Pages: {max_pages if max_pages else 'Unlimited'}")
    print(f"Max Depth: {max_depth}")
    if allowed_domain:
        print(f"Allowed Domain: {allowed_domain}")
    print(f"Output Directory: output/")
    print("=" * 70 + "\n")
    
    # Create and configure the crawler process
    process = CrawlerProcess(settings)
    
    # Start the spider
    process.crawl(
        ContactSpider,
        start_url=start_url,
        allowed_domain=allowed_domain
    )
    
    # Start crawling
    process.start()
    
    print("\n" + "=" * 70)
    print("Scraping completed!")
    print("=" * 70)
    print("Check the 'output/' directory for results (CSV and JSON files)")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()

