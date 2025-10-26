// University Contact Scraper - Frontend JavaScript

let isRunning = false;
let statusCheckInterval = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('University Contact Scraper initialized');
    
    // Setup form submission
    document.getElementById('scraperForm').addEventListener('submit', startScraping);
    
    // Setup stop button
    document.getElementById('stopBtn').addEventListener('click', stopScraping);
    
    // Check status on load
    checkStatus();
});

// Start scraping
async function startScraping(event) {
    event.preventDefault();
    console.log('Start scraping button clicked');
    
    if (isRunning) {
        showError('Scraping is already in progress');
        return;
    }
    
    // Get form values
    const url = document.getElementById('url').value.trim();
    const maxPages = parseInt(document.getElementById('maxPages').value);
    const workers = parseInt(document.getElementById('workers').value);
    const enableDeepCrawl = document.getElementById('enableDeepCrawl').checked;
    const deepCrawlRequests = parseInt(document.getElementById('deepCrawlRequests').value);
    const enableAiUrlFilter = document.getElementById('enableAiUrlFilter').checked;
    
    console.log('Form values:', { url, maxPages, workers, enableDeepCrawl, deepCrawlRequests });
    
    // Validate URL
    if (!url) {
        showError('Please enter a valid URL');
        return;
    }
    
    // Prepare data
    const data = {
        url: url,
        max_pages: maxPages,
        workers: workers,
        enable_deep_crawl: enableDeepCrawl,
        deep_crawl_requests: deepCrawlRequests,
        enable_ai_url_filter: enableAiUrlFilter
    };
    
    try {
        // Send request to start scraping
        const response = await fetch('/api/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            // Success - update UI
            isRunning = true;
            updateUIForRunning();
            clearError();
            clearResults();
            
            // Start status polling
            startStatusPolling();
            
            console.log('Scraping started successfully');
        } else {
            showError(result.error || 'Failed to start scraping');
        }
    } catch (error) {
        showError('Network error: ' + error.message);
        console.error('Error starting scraper:', error);
    }
}

// Stop scraping
async function stopScraping() {
    try {
        const response = await fetch('/api/stop', {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            updateStatus('Stopping...', 0);
        } else {
            showError(result.error || 'Failed to stop scraping');
        }
    } catch (error) {
        showError('Network error: ' + error.message);
        console.error('Error stopping scraper:', error);
    }
}

// Start polling for status updates
function startStatusPolling() {
    if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
    }
    
    statusCheckInterval = setInterval(checkStatus, 1000);
}

// Stop polling for status updates
function stopStatusPolling() {
    if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
        statusCheckInterval = null;
    }
}

// Check current status
async function checkStatus() {
    try {
        const response = await fetch('/api/status');
        const status = await response.json();
        
        // Update UI with status
        updateProgress(status.progress);
        updateStatus(status.status, status.progress);
        updateQuickStats(status);
        updateDetailedStats(status);
        
        if (status.current_url) {
            updateCurrentUrl(status.current_url);
        }
        
        if (status.activity_log && status.activity_log.length > 0) {
            updateActivityFeed(status.activity_log);
        }
        
        // Update AI stats if available
        if (status.ai_stats && status.ai_stats.enabled) {
            updateAIStats(status.ai_stats);
        }
        
        if (status.error) {
            showError(status.error);
        }
        
        // Check if scraping completed
        if (status.running) {
            if (!isRunning) {
                isRunning = true;
                updateUIForRunning();
                startStatusPolling();
            }
        } else {
            if (isRunning) {
                isRunning = false;
                updateUIForStopped();
                stopStatusPolling();
                
                // Load results if available
                if (status.progress === 100 && !status.error) {
                    loadResults();
                }
            }
        }
    } catch (error) {
        console.error('Error checking status:', error);
    }
}

// Load and display results
async function loadResults() {
    try {
        const response = await fetch('/api/results');
        
        if (!response.ok) {
            console.log('No results available yet');
            return;
        }
        
        const data = await response.json();
        
        if (data.contacts && data.contacts.length > 0) {
            displayResults(data.contacts);
            showDownloadButtons();
        } else {
            showNoResults();
        }
    } catch (error) {
        console.error('Error loading results:', error);
    }
}

// Display results in table
function displayResults(contacts) {
    const tableBody = document.getElementById('resultsTableBody');
    tableBody.innerHTML = '';
    
    contacts.forEach((contact, index) => {
        const row = document.createElement('tr');
        row.classList.add('fade-in');
        
        const sourceUrl = contact.source_url || '';
        
        row.innerHTML = `
            <td>${index + 1}</td>
            <td>${escapeHtml(contact.name || '-')}</td>
            <td>${escapeHtml(contact.designation || '-')}</td>
            <td>${contact.email ? `<a href="mailto:${escapeHtml(contact.email)}" class="text-decoration-none">${escapeHtml(contact.email)}</a>` : '-'}</td>
            <td>${escapeHtml(contact.phone || '-')}</td>
            <td>${escapeHtml(contact.university || '-')}</td>
            <td class="text-center">
                ${sourceUrl ? `<a href="${escapeHtml(sourceUrl)}" target="_blank" rel="noopener noreferrer" class="btn btn-sm btn-outline-primary" title="View Source Page">
                    <i class="bi bi-box-arrow-up-right"></i>
                </a>` : '-'}
            </td>
        `;
        
        tableBody.appendChild(row);
    });
    
    // Show results container
    document.getElementById('resultsPlaceholder').style.display = 'none';
    document.getElementById('resultsContainer').style.display = 'block';
}

// Show no results message
function showNoResults() {
    document.getElementById('resultsPlaceholder').innerHTML = `
        <i class="bi bi-inbox fs-1 text-warning"></i>
        <p class="text-muted mt-3">Scraping completed but no contacts were found.</p>
    `;
}

// Clear results
function clearResults() {
    document.getElementById('resultsTableBody').innerHTML = '';
    document.getElementById('resultsContainer').style.display = 'none';
    document.getElementById('resultsPlaceholder').style.display = 'block';
    document.getElementById('resultsPlaceholder').innerHTML = `
        <i class="bi bi-inbox fs-1 text-muted"></i>
        <p class="text-muted mt-3">No results yet. Start scraping to see contacts here.</p>
    `;
    document.getElementById('activityFeed').style.display = 'none';
    document.getElementById('activityList').innerHTML = '';
    document.getElementById('detailedStats').style.display = 'none';
    hideDownloadButtons();
}

// Update progress bar
function updateProgress(percent) {
    const progressBar = document.getElementById('progressBar');
    const progressPercent = document.getElementById('progressPercent');
    
    progressBar.style.width = percent + '%';
    progressBar.setAttribute('aria-valuenow', percent);
    progressPercent.textContent = percent + '%';
    
    // Change color based on progress
    if (percent === 100) {
        progressBar.classList.remove('bg-primary', 'bg-warning');
        progressBar.classList.add('bg-success');
    } else if (percent > 50) {
        progressBar.classList.remove('bg-primary', 'bg-success');
        progressBar.classList.add('bg-warning');
    } else {
        progressBar.classList.remove('bg-warning', 'bg-success');
        progressBar.classList.add('bg-primary');
    }
}

// Update status text
function updateStatus(text, progress) {
    const statusText = document.getElementById('statusText');
    statusText.textContent = text;
    
    // Add icon based on status
    if (progress === 100) {
        statusText.innerHTML = '<i class="bi bi-check-circle-fill text-success me-2"></i>' + text;
    } else if (text.toLowerCase().includes('error')) {
        statusText.innerHTML = '<i class="bi bi-exclamation-triangle-fill text-danger me-2"></i>' + text;
    } else if (text.toLowerCase().includes('discovering')) {
        statusText.innerHTML = '<i class="bi bi-search text-primary me-2"></i>' + text;
    } else if (text.toLowerCase().includes('scraping')) {
        statusText.innerHTML = '<i class="bi bi-gear-fill text-primary me-2 spin"></i>' + text;
    }
}

// Update current URL being processed
function updateCurrentUrl(url) {
    const currentUrlBox = document.getElementById('currentUrlBox');
    const currentUrl = document.getElementById('currentUrl');
    
    currentUrl.textContent = url;
    currentUrlBox.style.display = 'block';
}

// Update statistics
function updateQuickStats(status) {
    const urlsToScrape = status.urls_discovered || 0;
    const totalDiscovered = status.total_urls_discovered || 0;
    const contacts = status.contacts_found || 0;

    const statsUrls = document.getElementById('statsUrls');
    
    // Show "To Scrape / Discovered" format if we have both numbers
    if (totalDiscovered > 0 && totalDiscovered > urlsToScrape) {
        statsUrls.innerHTML = `${urlsToScrape.toLocaleString()} / <span class="text-muted small">${totalDiscovered.toLocaleString()}</span>`;
    } else {
        // Fallback to the simple number if they are the same or total is missing
        statsUrls.textContent = urlsToScrape.toLocaleString();
    }
    
    document.getElementById('statsContacts').textContent = contacts.toLocaleString();
}

// Update AI statistics
function updateAIStats(aiStats) {
    const aiStatsCard = document.getElementById('aiStatsCard');
    const urlAnalysisSection = document.getElementById('urlAnalysisSection');
    
    // Check if we should show AI stats (contact extraction or URL analysis)
    const hasContactStats = aiStats.enabled && aiStats.total_calls > 0;
    const hasUrlAnalysis = aiStats.url_analysis && aiStats.url_analysis.requests > 0;
    
    if (!hasContactStats && !hasUrlAnalysis) {
        aiStatsCard.style.display = 'none';
        return;
    }
    
    aiStatsCard.style.display = 'block';
    
    // Update model name
    const modelName = aiStats.model ? aiStats.model.split('/').pop() : '-';  // Get last part of model name
    document.getElementById('aiModel').textContent = modelName;
    
    // Update contact extraction stats
    document.getElementById('aiCalls').textContent = aiStats.total_calls || 0;
    
    const successRate = aiStats.total_calls > 0 
        ? ((aiStats.successful / aiStats.total_calls) * 100).toFixed(1)
        : 0;
    document.getElementById('aiSuccessRate').textContent = successRate + '%';
    
    // Update URL analysis stats (if available)
    if (hasUrlAnalysis) {
        urlAnalysisSection.style.display = 'block';
        document.getElementById('urlAnalysisCalls').textContent = aiStats.url_analysis.requests || 0;
        document.getElementById('urlAnalysisTokens').textContent = (aiStats.url_analysis.tokens || 0).toLocaleString();
    } else {
        urlAnalysisSection.style.display = 'none';
    }
    
    // Update total tokens and cost (includes both contact extraction and URL analysis)
    const totalTokens = aiStats.total_tokens || 0;
    document.getElementById('aiTokens').textContent = totalTokens.toLocaleString();
    
    const totalCost = aiStats.total_cost || 0;
    document.getElementById('aiCost').textContent = totalCost.toFixed(6);
}

// Update detailed statistics
function updateDetailedStats(status) {
    if (!status.running && status.progress === 0) {
        document.getElementById('detailedStats').style.display = 'none';
        return;
    }
    
    document.getElementById('detailedStats').style.display = 'block';
    
    // Pages scraped
    const pagesScraped = status.pages_scraped || 0;
    const totalPages = status.total_pages || 0;
    document.getElementById('pagesScraped').textContent = `${pagesScraped} / ${totalPages}`;
    
    // Emails found
    const emailsFound = status.emails_found || status.contacts_found || 0;
    document.getElementById('emailsFound').textContent = emailsFound;
    
    // Elapsed time
    const elapsed = status.elapsed_time || 0;
    const minutes = Math.floor(elapsed / 60);
    const seconds = elapsed % 60;
    document.getElementById('elapsedTime').textContent = 
        `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    
    // Average speed
    const avgSpeed = status.avg_speed || 0;
    document.getElementById('avgSpeed').textContent = `${avgSpeed}/s`;
}

// Update activity feed
function updateActivityFeed(activities) {
    if (!activities || activities.length === 0) {
        document.getElementById('activityFeed').style.display = 'none';
        return;
    }
    
    document.getElementById('activityFeed').style.display = 'block';
    
    const activityList = document.getElementById('activityList');
    
    // Only update if activity count changed
    if (activityList.children.length !== activities.length) {
        activityList.innerHTML = '';
        
        // Show activities in reverse order (newest first)
        activities.slice().reverse().forEach(activity => {
            const li = document.createElement('li');
            li.className = 'list-group-item py-2 px-3 fade-in';
            
            let icon = 'bi-info-circle';
            let iconColor = 'text-primary';
            
            if (activity.message.includes('✓') || activity.message.includes('Complete')) {
                icon = 'bi-check-circle-fill';
                iconColor = 'text-success';
            } else if (activity.message.includes('Error')) {
                icon = 'bi-exclamation-triangle-fill';
                iconColor = 'text-danger';
            } else if (activity.message.includes('Scraping')) {
                icon = 'bi-arrow-repeat';
                iconColor = 'text-info';
            }
            
            li.innerHTML = `
                <div class="d-flex align-items-start">
                    <i class="bi ${icon} ${iconColor} me-2 mt-1"></i>
                    <div class="flex-grow-1">
                        <small class="d-block">${escapeHtml(activity.message)}</small>
                        <small class="text-muted">${activity.time}</small>
                    </div>
                </div>
            `;
            
            activityList.appendChild(li);
        });
    }
}

// Update UI for running state
function updateUIForRunning() {
    document.getElementById('startBtn').style.display = 'none';
    document.getElementById('stopBtn').style.display = 'block';
    document.getElementById('scraperForm').querySelectorAll('input').forEach(input => {
        input.disabled = true;
    });
}

// Update UI for stopped state
function updateUIForStopped() {
    document.getElementById('startBtn').style.display = 'block';
    document.getElementById('stopBtn').style.display = 'none';
    document.getElementById('scraperForm').querySelectorAll('input').forEach(input => {
        input.disabled = false;
    });
    document.getElementById('currentUrlBox').style.display = 'none';
}

// Show error message
function showError(message) {
    const errorBox = document.getElementById('errorBox');
    const errorText = document.getElementById('errorText');
    
    errorText.textContent = message;
    errorBox.style.display = 'block';
}

// Clear error message
function clearError() {
    document.getElementById('errorBox').style.display = 'none';
}

// Show download buttons
function showDownloadButtons() {
    document.getElementById('downloadButtons').style.display = 'block';
}

// Hide download buttons
function hideDownloadButtons() {
    document.getElementById('downloadButtons').style.display = 'none';
}

// Download file
function downloadFile(fileType) {
    window.location.href = `/api/download/${fileType}`;
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Add spinning animation for loading icons
const style = document.createElement('style');
style.textContent = `
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    .spin {
        animation: spin 2s linear infinite;
        display: inline-block;
    }
`;
document.head.appendChild(style);

