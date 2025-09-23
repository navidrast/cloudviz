/**
 * CloudViz Frontend Application
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
        this.charts = {};
        this.init();
    }

    async init() {
        this.setupEventListeners();
        this.initializeCharts();
        this.checkApiConnection();
        this.loadSavedCredentials();
        await this.initializeMermaid();
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

    async initializeMermaid() {
        mermaid.initialize({
            startOnLoad: false,
            theme: 'default',
            securityLevel: 'loose',
            fontFamily: 'Arial, sans-serif'
        });
    }

    initializeCharts() {
        // Provider cost breakdown chart
        const providerCtx = document.getElementById('provider-cost-chart').getContext('2d');
        this.charts.providerCost = new Chart(providerCtx, {
            type: 'pie',
            data: {
                labels: ['Azure', 'AWS', 'GCP'],
                datasets: [{
                    data: [0, 0, 0],
                    backgroundColor: ['#0078d4', '#ff9900', '#4285f4'],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });

        // Spending trend chart
        const trendCtx = document.getElementById('spending-trend-chart').getContext('2d');
        this.charts.spendingTrend = new Chart(trendCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Monthly Spend',
                    data: [],
                    borderColor: '#0d6efd',
                    backgroundColor: 'rgba(13, 110, 253, 0.1)',
                    borderWidth: 2,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    }

    async checkApiConnection() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api`);
            const data = await response.json();
            
            if (response.ok) {
                document.getElementById('connection-status').textContent = 'Connected';
                document.querySelector('.navbar-text i').className = 'bi bi-circle-fill text-success me-1';
            } else {
                throw new Error('API not responding');
            }
        } catch (error) {
            document.getElementById('connection-status').textContent = 'Disconnected';
            document.querySelector('.navbar-text i').className = 'bi bi-circle-fill text-danger me-1';
            this.showNotification('Failed to connect to CloudViz API', 'error');
        }
    }

    loadSavedCredentials() {
        // Load credentials from localStorage
        const saved = localStorage.getItem('cloudviz-credentials');
        if (saved) {
            this.credentials = JSON.parse(saved);
            this.updateProviderStatus();
        }
    }

    saveCredentials(provider, formData) {
        const credentials = {};
        for (let [key, value] of formData.entries()) {
            credentials[key] = value;
        }

        this.credentials[provider] = credentials;
        localStorage.setItem('cloudviz-credentials', JSON.stringify(this.credentials));
        
        this.updateProviderStatus();
        this.showNotification(`${provider.toUpperCase()} credentials saved successfully`, 'success');
    }

    updateProviderStatus() {
        ['azure', 'aws', 'gcp'].forEach(provider => {
            const statusEl = document.getElementById(`${provider}-status`);
            if (this.credentials[provider]) {
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
        const settingsTab = new bootstrap.Tab(document.getElementById('settings-tab'));
        settingsTab.show();
    }

    async testConnection(provider) {
        if (!this.credentials[provider]) {
            this.showNotification(`Please configure ${provider.toUpperCase()} credentials first`, 'warning');
            return;
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/api/v1/${provider}/test`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(this.credentials[provider])
            });

            if (response.ok) {
                this.showNotification(`${provider.toUpperCase()} connection successful`, 'success');
            } else {
                throw new Error('Connection failed');
            }
        } catch (error) {
            this.showNotification(`${provider.toUpperCase()} connection failed`, 'error');
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
            const response = await fetch(`${this.apiBaseUrl}/api/v1/${provider}/extract`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(this.credentials[provider])
            });

            const data = await response.json();

            if (response.ok) {
                await this.pollJobStatus(data.job_id);
            } else {
                throw new Error(data.message || 'Scan failed');
            }
        } catch (error) {
            this.showProgress(false);
            this.showNotification(`Failed to scan ${provider.toUpperCase()}: ${error.message}`, 'error');
        }
    }

    async scanAllProviders() {
        const configuredProviders = ['azure', 'aws', 'gcp'].filter(p => this.credentials[p]);
        
        if (configuredProviders.length === 0) {
            this.showNotification('Please configure at least one cloud provider', 'warning');
            return;
        }

        this.showProgress(true, 'Scanning all configured providers...');

        try {
            const promises = configuredProviders.map(provider => this.scanProvider(provider));
            await Promise.all(promises);
            this.showNotification('All scans completed successfully', 'success');
        } catch (error) {
            this.showNotification('Some scans failed. Check individual provider status.', 'warning');
        } finally {
            this.showProgress(false);
        }
    }

    async pollJobStatus(jobId) {
        const pollInterval = 2000; // 2 seconds
        let attempts = 0;
        const maxAttempts = 150; // 5 minutes max

        const poll = async () => {
            try {
                const response = await fetch(`${this.apiBaseUrl}/api/v1/jobs/${jobId}`);
                const data = await response.json();

                if (data.status === 'completed') {
                    this.showProgress(false);
                    await this.loadVisualization(data.result_url || jobId);
                    return;
                } else if (data.status === 'failed') {
                    throw new Error(data.error || 'Job failed');
                } else if (attempts < maxAttempts) {
                    attempts++;
                    this.updateProgress(Math.min((attempts / maxAttempts) * 100, 90));
                    setTimeout(poll, pollInterval);
                } else {
                    throw new Error('Job timeout');
                }
            } catch (error) {
                this.showProgress(false);
                this.showNotification(`Job failed: ${error.message}`, 'error');
            }
        };

        poll();
    }

    async loadVisualization(resultUrl) {
        try {
            // This is a mock implementation - replace with actual API calls
            const mockDiagram = `
graph TB
    subgraph "Azure"
        VM1[Virtual Machine]
        DB1[SQL Database]
        SA1[Storage Account]
    end
    
    subgraph "AWS"
        EC2[EC2 Instance]
        RDS[RDS Database]
        S3[S3 Bucket]
    end
    
    subgraph "GCP"
        GCE[Compute Engine]
        SQL[Cloud SQL]
        GCS[Cloud Storage]
    end
    
    VM1 --> DB1
    EC2 --> RDS
    GCE --> SQL
`;

            await this.renderDiagram(mockDiagram);
            this.updateResourceSummary();
            this.updateCostCharts();
            this.generateRecommendations();

        } catch (error) {
            this.showNotification(`Failed to load visualization: ${error.message}`, 'error');
        }
    }

    async renderDiagram(diagramCode) {
        const diagramContainer = document.getElementById('diagram-display');
        
        try {
            // Clear previous diagram
            diagramContainer.innerHTML = '';
            
            // Create a new div for the diagram
            const diagramDiv = document.createElement('div');
            diagramDiv.id = 'mermaid-diagram';
            diagramContainer.appendChild(diagramDiv);

            // Render the mermaid diagram
            const { svg } = await mermaid.render('diagram-svg', diagramCode);
            diagramDiv.innerHTML = svg;
            
            this.currentDiagram = diagramCode;
            this.showNotification('Diagram loaded successfully', 'success');
            
        } catch (error) {
            diagramContainer.innerHTML = `
                <div class="text-center text-danger py-5">
                    <i class="bi bi-exclamation-triangle display-1"></i>
                    <h5 class="mt-3">Failed to render diagram</h5>
                    <p>${error.message}</p>
                </div>
            `;
        }
    }

    updateDiagramTheme(theme) {
        if (this.currentDiagram) {
            mermaid.initialize({ theme: theme });
            this.renderDiagram(this.currentDiagram);
        }
    }

    updateResourceSummary() {
        // Mock data - replace with actual API data
        document.getElementById('total-resources').textContent = '42';
        document.getElementById('total-cost').textContent = '$1,234';
        document.getElementById('total-regions').textContent = '8';
        document.getElementById('last-scan').textContent = new Date().toLocaleTimeString();
    }

    updateCostCharts() {
        // Mock data - replace with actual API data
        this.charts.providerCost.data.datasets[0].data = [450, 520, 264];
        this.charts.providerCost.update();

        const last6Months = [];
        const spending = [];
        for (let i = 5; i >= 0; i--) {
            const date = new Date();
            date.setMonth(date.getMonth() - i);
            last6Months.push(date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' }));
            spending.push(Math.floor(Math.random() * 500) + 800);
        }

        this.charts.spendingTrend.data.labels = last6Months;
        this.charts.spendingTrend.data.datasets[0].data = spending;
        this.charts.spendingTrend.update();
    }

    generateRecommendations() {
        const recommendations = [
            {
                title: 'Underutilized Virtual Machines',
                description: 'Found 3 VMs with < 10% CPU utilization over the last 30 days',
                savings: '$145/month',
                priority: 'high'
            },
            {
                title: 'Unattached Storage Volumes',
                description: '2 storage volumes are not attached to any instances',
                savings: '$67/month',
                priority: 'medium'
            },
            {
                title: 'Reserved Instance Opportunities',
                description: 'Purchase reserved instances for consistent workloads',
                savings: '$234/month',
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
        
        try {
            // For SVG, we can download directly from the current diagram
            if (format === 'svg') {
                const svg = document.querySelector('#mermaid-diagram svg');
                if (svg) {
                    const svgData = new XMLSerializer().serializeToString(svg);
                    const blob = new Blob([svgData], { type: 'image/svg+xml' });
                    this.downloadBlob(blob, `cloudviz-diagram.${format}`);
                    return;
                }
            }

            // For other formats, make API call
            const response = await fetch(`${this.apiBaseUrl}/api/v1/visualization/export`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    diagram: this.currentDiagram,
                    format: format
                })
            });

            if (response.ok) {
                const blob = await response.blob();
                this.downloadBlob(blob, `cloudviz-diagram.${format}`);
            } else {
                throw new Error('Export failed');
            }
        } catch (error) {
            this.showNotification(`Download failed: ${error.message}`, 'error');
        }
    }

    downloadBlob(blob, filename) {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.showNotification(`Downloaded ${filename}`, 'success');
    }

    shareLink() {
        const shareUrl = `${window.location.origin}?diagram=${encodeURIComponent(this.currentDiagram || '')}`;
        
        if (navigator.share) {
            navigator.share({
                title: 'CloudViz Infrastructure Diagram',
                url: shareUrl
            });
        } else if (navigator.clipboard) {
            navigator.clipboard.writeText(shareUrl);
            this.showNotification('Share link copied to clipboard', 'success');
        } else {
            // Fallback
            prompt('Copy this link to share:', shareUrl);
        }
    }

    zoomDiagram(factor) {
        const diagram = document.querySelector('#mermaid-diagram svg');
        if (diagram) {
            const currentScale = parseFloat(diagram.style.transform.replace(/scale\(([^)]+)\)/, '$1') || '1');
            const newScale = Math.max(0.1, Math.min(3, currentScale * factor));
            diagram.style.transform = `scale(${newScale})`;
            diagram.style.transformOrigin = 'center';
        }
    }

    resetZoom() {
        const diagram = document.querySelector('#mermaid-diagram svg');
        if (diagram) {
            diagram.style.transform = 'scale(1)';
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
        toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type === 'success' ? 'success' : type === 'warning' ? 'warning' : 'primary'} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remove toast after it's hidden
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }

    createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '1100';
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

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.cloudVizApp = new CloudVizApp();
});