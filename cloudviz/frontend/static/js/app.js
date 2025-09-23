/**
 * CloudViz Frontend Application - Vanilla JS Implementation
 * Handles all frontend interactions with the CloudViz API
 */

class CloudVizApp {
    constructor() {
        this.apiBaseUrl = window.location.origin;
        this.credentials = {
            azure: null,
            aws: null,
            gcp: null
        };
        this.currentDiagram = null;
        this.init();
    }

    async init() {
        this.setupEventListeners();
        this.checkApiConnection();
        this.loadSavedCredentials();
        this.setupTabs();
    }

    setupEventListeners() {
        // Provider card clicks
        document.querySelectorAll('.provider-card').forEach(card => {
            card.addEventListener('click', (e) => {
                const provider = e.currentTarget.dataset.provider;
                this.showProviderForm(provider);
            });
        });

        // Scan buttons
        document.getElementById('scan-all').addEventListener('click', () => this.scanAllProviders());
        document.getElementById('scan-azure').addEventListener('click', () => this.scanProvider('azure'));
        document.getElementById('scan-aws').addEventListener('click', () => this.scanProvider('aws'));
        document.getElementById('scan-gcp').addEventListener('click', () => this.scanProvider('gcp'));

        // Export buttons
        document.getElementById('download-diagram').addEventListener('click', () => this.downloadDiagram());
        document.getElementById('share-link').addEventListener('click', () => this.shareLink());

        // Theme selector
        document.getElementById('theme-selector').addEventListener('change', (e) => {
            this.updateDiagramTheme(e.target.value);
        });

        // Zoom controls
        document.getElementById('zoom-in').addEventListener('click', () => this.zoomDiagram(1.2));
        document.getElementById('zoom-out').addEventListener('click', () => this.zoomDiagram(0.8));
        document.getElementById('reset-zoom').addEventListener('click', () => this.resetZoom());

        // Credential forms
        document.getElementById('azure-credentials').addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveCredentials('azure', new FormData(e.target));
        });

        document.getElementById('aws-credentials').addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveCredentials('aws', new FormData(e.target));
        });

        document.getElementById('gcp-credentials').addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveCredentials('gcp', new FormData(e.target));
        });
    }

    setupTabs() {
        // Simple tab implementation without Bootstrap
        document.querySelectorAll('.nav-link').forEach(tab => {
            tab.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = e.target.getAttribute('href');
                if (targetId) {
                    this.showTab(e.target.id);
                }
            });
        });
    }

    showTab(tabId) {
        // Remove active from all tabs and panes
        document.querySelectorAll('.nav-link').forEach(tab => {
            tab.classList.remove('active');
        });
        
        document.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.remove('active', 'show');
        });

        // Add active to clicked tab
        document.getElementById(tabId).classList.add('active');

        // Show corresponding pane
        const paneId = tabId.replace('-tab', '-pane');
        const pane = document.getElementById(paneId);
        if (pane) {
            pane.classList.add('active', 'show');
        }
    }

    async checkApiConnection() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api`);
            const data = await response.json();
            
            if (response.ok) {
                document.getElementById('connection-status').textContent = 'Connected';
                this.updateConnectionStatus(true);
            } else {
                throw new Error('API not responding');
            }
        } catch (error) {
            document.getElementById('connection-status').textContent = 'Disconnected';
            this.updateConnectionStatus(false);
            this.showNotification('Failed to connect to CloudViz API', 'error');
        }
    }

    updateConnectionStatus(connected) {
        const statusElement = document.querySelector('.navbar-text span');
        if (connected) {
            statusElement.className = 'bi-circle-fill text-success me-1';
        } else {
            statusElement.className = 'bi-circle-fill text-danger me-1';
        }
    }

    loadSavedCredentials() {
        // Load credentials from localStorage
        const saved = localStorage.getItem('cloudviz-credentials');
        if (saved) {
            try {
                this.credentials = JSON.parse(saved);
                this.updateProviderStatus();
            } catch (error) {
                console.error('Failed to load saved credentials:', error);
            }
        }
    }

    saveCredentials(provider, formData) {
        const credentials = {};
        for (let [key, value] of formData.entries()) {
            credentials[key] = value.trim();
        }

        this.credentials[provider] = credentials;
        localStorage.setItem('cloudviz-credentials', JSON.stringify(this.credentials));
        
        this.updateProviderStatus();
        this.showNotification(`${provider.toUpperCase()} credentials saved successfully`, 'success');
    }

    updateProviderStatus() {
        ['azure', 'aws', 'gcp'].forEach(provider => {
            const statusEl = document.getElementById(`${provider}-status`);
            if (this.credentials[provider] && Object.keys(this.credentials[provider]).length > 0) {
                statusEl.textContent = 'Configured';
                statusEl.className = 'badge status-badge bg-success';
            } else {
                statusEl.textContent = 'Not Configured';
                statusEl.className = 'badge status-badge bg-secondary';
            }
        });
    }

    showProviderForm(provider) {
        // Hide all forms
        document.querySelectorAll('.credential-form').forEach(form => {
            form.classList.remove('active');
        });

        // Show selected form
        document.getElementById(`${provider}-form`).classList.add('active');
        
        // Switch to settings tab
        this.showTab('settings-tab');
    }

    async testConnection(provider) {
        if (!this.credentials[provider]) {
            this.showNotification(`Please configure ${provider.toUpperCase()} credentials first`, 'warning');
            return;
        }

        try {
            // Note: This would need to be implemented in the backend
            this.showNotification(`Testing ${provider.toUpperCase()} connection...`, 'info');
            
            // Simulate API call for now
            setTimeout(() => {
                this.showNotification(`${provider.toUpperCase()} connection test completed`, 'success');
            }, 2000);
            
        } catch (error) {
            this.showNotification(`${provider.toUpperCase()} connection failed: ${error.message}`, 'error');
        }
    }

    async scanProvider(provider) {
        if (!this.credentials[provider]) {
            this.showNotification(`Please configure ${provider.toUpperCase()} credentials first`, 'warning');
            this.showProviderForm(provider);
            return;
        }

        this.showProgress(true, `Scanning ${provider.toUpperCase()} resources...`);

        try {
            // Note: This would connect to actual API endpoints
            this.showNotification(`Starting ${provider.toUpperCase()} scan...`, 'info');
            
            // Simulate scanning process
            let progress = 0;
            const progressInterval = setInterval(() => {
                progress += Math.random() * 15;
                this.updateProgress(Math.min(progress, 90));
                
                if (progress >= 90) {
                    clearInterval(progressInterval);
                    setTimeout(() => {
                        this.showProgress(false);
                        this.loadMockVisualization();
                        this.showNotification(`${provider.toUpperCase()} scan completed successfully`, 'success');
                    }, 1000);
                }
            }, 500);

        } catch (error) {
            this.showProgress(false);
            this.showNotification(`Failed to scan ${provider.toUpperCase()}: ${error.message}`, 'error');
        }
    }

    async scanAllProviders() {
        const configuredProviders = ['azure', 'aws', 'gcp'].filter(p => 
            this.credentials[p] && Object.keys(this.credentials[p]).length > 0
        );
        
        if (configuredProviders.length === 0) {
            this.showNotification('Please configure at least one cloud provider', 'warning');
            this.showTab('settings-tab');
            return;
        }

        this.showProgress(true, 'Scanning all configured providers...');
        this.showNotification(`Scanning ${configuredProviders.join(', ').toUpperCase()}...`, 'info');

        // Simulate scanning all providers
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress += Math.random() * 10;
            this.updateProgress(Math.min(progress, 90));
            
            if (progress >= 90) {
                clearInterval(progressInterval);
                setTimeout(() => {
                    this.showProgress(false);
                    this.loadMockVisualization();
                    this.showNotification('All scans completed successfully', 'success');
                }, 1000);
            }
        }, 800);
    }

    loadMockVisualization() {
        // Create a simple mock visualization
        const diagramContainer = document.getElementById('diagram-display');
        
        const mockDiagram = `
            <div class="text-center py-4">
                <h5 class="text-primary mb-3">Infrastructure Overview</h5>
                <div class="row">
                    <div class="col-md-4 mb-3">
                        <div class="card border-primary">
                            <div class="card-body text-center">
                                <div class="bi-microsoft text-primary" style="font-size: 2rem;"></div>
                                <h6 class="mt-2">Azure Resources</h6>
                                <p class="mb-0">3 VMs, 2 Storage Accounts</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4 mb-3">
                        <div class="card border-warning">
                            <div class="card-body text-center">
                                <div class="bi-amazon text-warning" style="font-size: 2rem;"></div>
                                <h6 class="mt-2">AWS Resources</h6>
                                <p class="mb-0">5 EC2, 1 RDS, 2 S3</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4 mb-3">
                        <div class="card border-danger">
                            <div class="card-body text-center">
                                <div class="bi-google text-danger" style="font-size: 2rem;"></div>
                                <h6 class="mt-2">GCP Resources</h6>
                                <p class="mb-0">2 Compute, 1 Cloud SQL</p>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="mt-3">
                    <small class="text-muted">Mock visualization - Real diagrams will be generated from actual cloud data</small>
                </div>
            </div>
        `;

        diagramContainer.innerHTML = mockDiagram;
        this.currentDiagram = 'mock-diagram';
        
        this.updateResourceSummary();
        this.generateRecommendations();
        
        // Switch to diagram tab
        this.showTab('diagram-tab');
    }

    updateDiagramTheme(theme) {
        if (this.currentDiagram) {
            this.showNotification(`Theme changed to: ${theme}`, 'info');
            // Theme change logic would go here for real diagrams
        }
    }

    updateResourceSummary() {
        // Mock data - replace with actual API data
        document.getElementById('total-resources').textContent = '13';
        document.getElementById('total-cost').textContent = '$2,847';
        document.getElementById('total-regions').textContent = '5';
        document.getElementById('last-scan').textContent = new Date().toLocaleTimeString();
    }

    generateRecommendations() {
        const recommendations = [
            {
                title: 'Underutilized Virtual Machines',
                description: 'Found 2 VMs with < 15% CPU utilization over the last 30 days',
                savings: '$287/month',
                priority: 'high'
            },
            {
                title: 'Unattached Storage Volumes',
                description: '1 storage volume is not attached to any instances',
                savings: '$45/month',
                priority: 'medium'
            },
            {
                title: 'Reserved Instance Opportunities',
                description: 'Consider reserved instances for consistent workloads',
                savings: '$412/month',
                priority: 'low'
            }
        ];

        const container = document.getElementById('recommendations-list');
        container.innerHTML = recommendations.map(rec => `
            <div class="alert alert-${rec.priority === 'high' ? 'warning' : rec.priority === 'medium' ? 'info' : 'secondary'} d-flex justify-content-between align-items-start">
                <div>
                    <h6 class="alert-heading">${rec.title}</h6>
                    <p class="mb-0">${rec.description}</p>
                </div>
                <div class="text-end">
                    <strong class="text-success">${rec.savings}</strong>
                    <br>
                    <small class="text-muted">${rec.priority} priority</small>
                </div>
            </div>
        `).join('');
    }

    async downloadDiagram() {
        if (!this.currentDiagram) {
            this.showNotification('No diagram to download', 'warning');
            return;
        }

        const format = document.getElementById('export-format').value;
        this.showNotification(`Preparing ${format.toUpperCase()} download...`, 'info');
        
        // Simulate download
        setTimeout(() => {
            this.showNotification(`${format.toUpperCase()} download completed`, 'success');
        }, 1500);
    }

    shareLink() {
        const shareUrl = `${window.location.origin}?shared=true`;
        
        if (navigator.clipboard) {
            navigator.clipboard.writeText(shareUrl).then(() => {
                this.showNotification('Share link copied to clipboard', 'success');
            }).catch(() => {
                this.fallbackShareLink(shareUrl);
            });
        } else {
            this.fallbackShareLink(shareUrl);
        }
    }

    fallbackShareLink(url) {
        const textArea = document.createElement('textarea');
        textArea.value = url;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        this.showNotification('Share link copied to clipboard', 'success');
    }

    zoomDiagram(factor) {
        if (this.currentDiagram) {
            this.showNotification(`Zoom ${factor > 1 ? 'in' : 'out'}`, 'info');
            // Zoom logic would go here for real diagrams
        }
    }

    resetZoom() {
        if (this.currentDiagram) {
            this.showNotification('Zoom reset', 'info');
            // Reset zoom logic would go here
        }
    }

    showProgress(show, message = '') {
        const container = document.querySelector('.progress-container');
        const text = document.getElementById('progress-text');
        
        if (show) {
            container.style.display = 'block';
            text.textContent = message;
            this.updateProgress(0);
        } else {
            container.style.display = 'none';
        }
    }

    updateProgress(percentage) {
        const progressBar = document.querySelector('.progress-bar');
        progressBar.style.width = `${percentage}%`;
        progressBar.setAttribute('aria-valuenow', percentage);
    }

    showNotification(message, type = 'info') {
        // Create toast notification
        const toastContainer = document.getElementById('toast-container') || this.createToastContainer();
        
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        // Auto-remove toast after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 5000);
    }

    createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        document.body.appendChild(container);
        return container;
    }
}

// Global function for testing connections (called from HTML)
window.testConnection = function(provider) {
    if (window.cloudVizApp) {
        window.cloudVizApp.testConnection(provider);
    }
};

// Global function for showing tabs (called from HTML)
window.showTab = function(tabId) {
    if (window.cloudVizApp) {
        window.cloudVizApp.showTab(tabId);
    }
};

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.cloudVizApp = new CloudVizApp();
});