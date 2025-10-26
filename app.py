"""
University Contact Scraper - Web Interface
Flask server for running the scraper with a user-friendly web interface
"""

from flask import Flask, render_template, request, jsonify, send_file, Response
import json
import os
import threading
import time
from datetime import datetime
from queue import Queue
import sys

# Import the scraper
from oxylabs_integration import OxylabsScraper

app = Flask(__name__)

# Global state for tracking scraping progress
scraping_state = {
    'running': False,
    'progress': 0,
    'status': 'Idle',
    'urls_discovered': 0,
    'contacts_found': 0,
    'current_url': '',
    'error': None,
    'output_file': None,
    'raw_output_file': None,
    'pages_scraped': 0,
    'total_pages': 0,
    'emails_found': 0,
    'start_time': None,
    'elapsed_time': 0,
    'avg_speed': 0,
    'activity_log': []
}

# Queue for progress updates
progress_queue = Queue()


class ProgressTracker:
    """Custom progress tracker that updates the global state"""
    
    def __init__(self):
        self.total = 0
        self.current = 0
    
    def add_activity(self, message, icon='info'):
        """Add an activity log entry"""
        global scraping_state
        import time
        
        timestamp = time.strftime('%H:%M:%S')
        activity = {
            'time': timestamp,
            'message': message,
            'icon': icon
        }
        
        # Keep only last 50 activities
        scraping_state['activity_log'].append(activity)
        if len(scraping_state['activity_log']) > 50:
            scraping_state['activity_log'].pop(0)
    
    def update(self, message, urls_discovered=None, contacts_found=None, current_url=None):
        """Update progress with message and optional metrics"""
        global scraping_state
        
        if self.total > 0:
            scraping_state['progress'] = int((self.current / self.total) * 100)
            scraping_state['pages_scraped'] = self.current
            scraping_state['total_pages'] = self.total
            
            # Calculate speed
            if scraping_state['start_time']:
                elapsed = time.time() - scraping_state['start_time']
                scraping_state['elapsed_time'] = int(elapsed)
                if elapsed > 0:
                    scraping_state['avg_speed'] = round(self.current / elapsed, 2)
        
        scraping_state['status'] = message
        
        if urls_discovered is not None:
            scraping_state['urls_discovered'] = urls_discovered
        if contacts_found is not None:
            scraping_state['contacts_found'] = contacts_found
            scraping_state['emails_found'] = contacts_found
        if current_url is not None:
            scraping_state['current_url'] = current_url
        
        # Add to activity log
        self.add_activity(message)
        
        # Add to queue for SSE
        progress_queue.put({
            'progress': scraping_state['progress'],
            'status': message,
            'urls_discovered': scraping_state['urls_discovered'],
            'contacts_found': scraping_state['contacts_found'],
            'current_url': scraping_state['current_url'],
            'pages_scraped': scraping_state['pages_scraped'],
            'total_pages': scraping_state['total_pages'],
            'elapsed_time': scraping_state['elapsed_time'],
            'avg_speed': scraping_state['avg_speed']
        })
        
        self.current += 1


def run_scraper_thread(url, max_pages, workers, enable_deep_crawl, deep_crawl_requests):
    """Run the scraper in a background thread"""
    global scraping_state
    
    try:
        scraping_state['running'] = True
        scraping_state['progress'] = 0
        scraping_state['status'] = 'Initializing scraper...'
        scraping_state['urls_discovered'] = 0
        scraping_state['contacts_found'] = 0
        scraping_state['current_url'] = url
        scraping_state['error'] = None
        scraping_state['output_file'] = None
        scraping_state['raw_output_file'] = None
        scraping_state['pages_scraped'] = 0
        scraping_state['total_pages'] = 0
        scraping_state['emails_found'] = 0
        scraping_state['start_time'] = time.time()
        scraping_state['elapsed_time'] = 0
        scraping_state['avg_speed'] = 0
        scraping_state['activity_log'] = []
        
        # Initialize tracker
        tracker = ProgressTracker()
        
        # Update status - discovering URLs
        tracker.update('Discovering URLs...', urls_discovered=0, contacts_found=0)
        scraping_state['progress'] = 10
        
        # Import the discover_urls function and scraper class
        from oxylabs_integration import discover_urls, OxylabsScraper
        
        # Discover URLs
        discovered_urls = discover_urls(
            url, 
            max_pages=max_pages,
            enable_deep_crawl=enable_deep_crawl,
            deep_crawl_requests=deep_crawl_requests
        )
        
        tracker.update(f'Found {len(discovered_urls)} URLs to scrape', urls_discovered=len(discovered_urls))
        scraping_state['progress'] = 20
        
        # Initialize scraper with credentials
        scraper = OxylabsScraper("mcruwan_6Grof", "NewAdmin_123")
        
        # Update status - starting scraping
        tracker.update('Starting parallel scraping...', urls_discovered=len(discovered_urls))
        scraping_state['progress'] = 25
        
        # Scrape URLs using the scraper's method
        # Note: scrape_multiple_urls saves files internally and returns raw contacts
        results = scraper.scrape_multiple_urls(discovered_urls, max_workers=workers)
        
        scraping_state['progress'] = 90
        
        # Find the most recent output files
        import glob
        import os
        
        # Get the latest files from output directory
        json_files = glob.glob('output/raw_contacts_*.json')
        csv_files = glob.glob('output/contacts_*.csv')
        
        if json_files:
            scraping_state['raw_output_file'] = max(json_files, key=os.path.getctime)
        if csv_files:
            scraping_state['output_file'] = max(csv_files, key=os.path.getctime)
        
        # Count unique contacts from results
        from oxylabs_integration import clean_and_deduplicate_contacts
        unique_contacts = clean_and_deduplicate_contacts(results)
        contacts_found = len(unique_contacts)
        
        scraping_state['contacts_found'] = contacts_found
        
        # Complete
        tracker.update(f'✓ Complete! Found {contacts_found} contacts', 
                      urls_discovered=len(discovered_urls), 
                      contacts_found=contacts_found)
        scraping_state['progress'] = 100
        
    except Exception as e:
        scraping_state['error'] = str(e)
        scraping_state['status'] = f'Error: {str(e)}'
        scraping_state['progress'] = 0
        print(f"Error in scraper thread: {e}")
        import traceback
        traceback.print_exc()
    finally:
        scraping_state['running'] = False


@app.route('/')
def index():
    """Render the main interface"""
    return render_template('index.html')


@app.route('/api/start', methods=['POST'])
def start_scraping():
    """Start a new scraping job"""
    global scraping_state
    
    if scraping_state['running']:
        return jsonify({'error': 'Scraping already in progress'}), 400
    
    data = request.get_json()
    
    # Validate input
    url = data.get('url', '').strip()
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    if not url.startswith('http'):
        url = 'https://' + url
    
    max_pages = int(data.get('max_pages', 20))
    workers = int(data.get('workers', 30))
    enable_deep_crawl = data.get('enable_deep_crawl', False)
    deep_crawl_requests = int(data.get('deep_crawl_requests', 50))
    
    # Validate ranges
    if max_pages < 1 or max_pages > 10000:
        return jsonify({'error': 'Max pages must be between 1 and 10000'}), 400
    if workers < 1 or workers > 100:
        return jsonify({'error': 'Workers must be between 1 and 100'}), 400
    if deep_crawl_requests < 1 or deep_crawl_requests > 200:
        return jsonify({'error': 'Deep crawl requests must be between 1 and 200'}), 400
    
    # Start scraping in background thread
    thread = threading.Thread(
        target=run_scraper_thread,
        args=(url, max_pages, workers, enable_deep_crawl, deep_crawl_requests)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({'success': True, 'message': 'Scraping started'})


@app.route('/api/status')
def get_status():
    """Get current scraping status"""
    return jsonify(scraping_state)


@app.route('/api/progress-stream')
def progress_stream():
    """Server-Sent Events stream for real-time progress updates"""
    def generate():
        while True:
            if not progress_queue.empty():
                data = progress_queue.get()
                yield f"data: {json.dumps(data)}\n\n"
            time.sleep(0.1)
    
    return Response(generate(), mimetype='text/event-stream')


@app.route('/api/results')
def get_results():
    """Get the latest results"""
    if not scraping_state['output_file']:
        return jsonify({'error': 'No results available'}), 404
    
    try:
        # Read CSV and convert to JSON for display
        import csv
        contacts = []
        
        with open(scraping_state['output_file'], 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                contacts.append(row)
        
        return jsonify({
            'contacts': contacts,
            'count': len(contacts),
            'csv_file': scraping_state['output_file'],
            'json_file': scraping_state['raw_output_file']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/download/<file_type>')
def download_file(file_type):
    """Download the results file"""
    if file_type == 'csv':
        file_path = scraping_state['output_file']
    elif file_type == 'json':
        file_path = scraping_state['raw_output_file']
    else:
        return jsonify({'error': 'Invalid file type'}), 400
    
    if not file_path or not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(file_path, as_attachment=True)


@app.route('/api/stop', methods=['POST'])
def stop_scraping():
    """Stop the current scraping job (graceful)"""
    global scraping_state
    
    if not scraping_state['running']:
        return jsonify({'error': 'No scraping in progress'}), 400
    
    # Note: This is a graceful indicator, the thread will complete current work
    scraping_state['status'] = 'Stopping...'
    return jsonify({'success': True, 'message': 'Stop request sent'})


if __name__ == '__main__':
    print("\n" + "="*70)
    print("University Contact Scraper - Web Interface")
    print("="*70)
    print("\nServer starting...")
    print("Open your browser and go to: http://localhost:5000")
    print("\n" + "="*70 + "\n")
    
    app.run(debug=True, threaded=True, port=5000)

