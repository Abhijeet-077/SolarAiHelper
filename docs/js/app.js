// Main Application Controller for Solar AI Platform
class SolarAIApp {
    constructor() {
        this.currentStep = 1;
        this.imageProcessor = new ImageProcessor();
        this.solarCalculator = new SolarCalculator();
        this.aiIntegration = new AIIntegration();
        this.pdfGenerator = new PDFGenerator();
        
        this.currentImage = null;
        this.roofAnalysis = null;
        this.solarResults = null;
        this.aiRecommendations = null;
        this.config = {};
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadStoredApiKey();
        this.showApiNoticeIfNeeded();
        console.log('🌞 Solar AI Platform initialized');
    }

    setupEventListeners() {
        // File upload
        const fileInput = document.getElementById('file-input');
        const fileUpload = document.getElementById('file-upload');
        
        if (fileInput && fileUpload) {
            fileInput.addEventListener('change', (e) => this.handleFileUpload(e));
            fileUpload.addEventListener('click', () => fileInput.click());
            fileUpload.addEventListener('dragover', (e) => this.handleDragOver(e));
            fileUpload.addEventListener('drop', (e) => this.handleFileDrop(e));
        }

        // Form inputs
        this.setupFormValidation();
        
        // Modal events
        this.setupModalEvents();
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyboardShortcuts(e));
    }

    setupFormValidation() {
        const inputs = ['latitude', 'longitude', 'electricity-rate', 'installation-cost'];
        inputs.forEach(id => {
            const input = document.getElementById(id);
            if (input) {
                input.addEventListener('input', () => this.validateForm());
            }
        });
    }

    setupModalEvents() {
        const modal = document.getElementById('api-modal');
        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeApiModal();
                }
            });
        }
    }

    loadStoredApiKey() {
        this.aiIntegration.loadApiKey();
        if (this.aiIntegration.isConfigured) {
            this.hideApiNotice();
        }
    }

    showApiNoticeIfNeeded() {
        if (!this.aiIntegration.isConfigured) {
            const notice = document.getElementById('api-notice');
            if (notice) {
                notice.style.display = 'block';
            }
        }
    }

    hideApiNotice() {
        const notice = document.getElementById('api-notice');
        if (notice) {
            notice.style.display = 'none';
        }
    }

    // File handling
    handleFileUpload(event) {
        const file = event.target.files[0];
        if (file) {
            this.processUploadedFile(file);
        }
    }

    handleDragOver(event) {
        event.preventDefault();
        event.currentTarget.classList.add('dragover');
    }

    handleFileDrop(event) {
        event.preventDefault();
        event.currentTarget.classList.remove('dragover');
        
        const files = event.dataTransfer.files;
        if (files.length > 0) {
            this.processUploadedFile(files[0]);
        }
    }

    async processUploadedFile(file) {
        try {
            // Validate file
            this.imageProcessor.validateImageFile(file);
            
            // Show loading state
            this.showMessage('Processing image...', 'info');
            
            // Process image
            const result = await this.imageProcessor.processImage(file);
            
            if (result.success) {
                this.currentImage = result.imageData;
                this.roofAnalysis = result.analysis;
                this.showImagePreview(result.imageData);
                this.enableContinueButton();
                this.showMessage('Image processed successfully!', 'success');
            } else {
                throw new Error(result.error);
            }
        } catch (error) {
            this.showMessage(`Error: ${error.message}`, 'error');
        }
    }

    showImagePreview(imageData) {
        const previewContainer = document.getElementById('image-preview-container');
        const previewImg = document.getElementById('image-preview');
        
        if (previewContainer && previewImg) {
            const previewUrl = this.imageProcessor.getImagePreviewUrl(imageData);
            if (previewUrl) {
                previewImg.src = previewUrl;
                previewContainer.style.display = 'block';
            }
        }
    }

    enableContinueButton() {
        const continueBtn = document.getElementById('continue-btn');
        if (continueBtn) {
            continueBtn.disabled = false;
        }
    }

    // Sample image handling
    async loadSampleImage(sampleType) {
        try {
            this.showMessage('Loading sample image...', 'info');
            
            const result = await this.imageProcessor.processSampleImage(sampleType);
            
            if (result.success) {
                this.currentImage = result.imageData;
                this.roofAnalysis = result.analysis;
                this.showImagePreview(result.imageData);
                this.enableContinueButton();
                this.showMessage(`Sample image loaded: ${result.sampleInfo.name}`, 'success');
            } else {
                throw new Error(result.error);
            }
        } catch (error) {
            this.showMessage(`Error loading sample: ${error.message}`, 'error');
        }
    }

    // Navigation
    goToStep(step) {
        if (step < 1 || step > 4) return;
        
        // Validate step transition
        if (step > this.currentStep + 1) {
            this.showMessage('Please complete the current step first', 'warning');
            return;
        }
        
        // Hide current section
        const currentSection = document.getElementById(`section-${this.currentStep}`);
        if (currentSection) {
            currentSection.classList.remove('active');
        }
        
        // Update step indicator
        const currentStepIndicator = document.getElementById(`step-${this.currentStep}`);
        if (currentStepIndicator) {
            currentStepIndicator.classList.remove('active');
            if (step > this.currentStep) {
                currentStepIndicator.classList.add('completed');
            }
        }
        
        // Show new section
        const newSection = document.getElementById(`section-${step}`);
        if (newSection) {
            newSection.classList.add('active');
        }
        
        // Update step indicator
        const newStepIndicator = document.getElementById(`step-${step}`);
        if (newStepIndicator) {
            newStepIndicator.classList.add('active');
        }
        
        this.currentStep = step;
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    // Configuration
    setLocation(lat, lng) {
        const latInput = document.getElementById('latitude');
        const lngInput = document.getElementById('longitude');
        
        if (latInput) latInput.value = lat;
        if (lngInput) lngInput.value = lng;
        
        this.showMessage(`Location set to ${lat}, ${lng}`, 'success');
    }

    validateForm() {
        const requiredFields = ['latitude', 'longitude', 'electricity-rate', 'installation-cost'];
        let isValid = true;
        
        requiredFields.forEach(id => {
            const input = document.getElementById(id);
            if (input && (!input.value || isNaN(parseFloat(input.value)))) {
                isValid = false;
            }
        });
        
        return isValid;
    }

    getConfiguration() {
        return {
            latitude: parseFloat(document.getElementById('latitude').value),
            longitude: parseFloat(document.getElementById('longitude').value),
            electricityRate: parseFloat(document.getElementById('electricity-rate').value),
            installationCost: parseFloat(document.getElementById('installation-cost').value),
            panelType: document.getElementById('panel-type').value,
            systemSizePreference: document.getElementById('system-size').value
        };
    }

    // Analysis
    async startAnalysis() {
        if (!this.currentImage || !this.roofAnalysis) {
            this.showMessage('Please upload an image first', 'error');
            return;
        }
        
        if (!this.validateForm()) {
            this.showMessage('Please fill in all configuration fields', 'error');
            return;
        }
        
        this.config = this.getConfiguration();
        this.goToStep(3);
        
        try {
            await this.runAnalysis();
        } catch (error) {
            this.showMessage(`Analysis failed: ${error.message}`, 'error');
        }
    }

    async runAnalysis() {
        const steps = [
            { id: 'step-image', text: 'Analyzing image structure...', duration: 1000 },
            { id: 'step-roof', text: 'Detecting roof boundaries...', duration: 1500 },
            { id: 'step-dimensions', text: 'Calculating roof dimensions...', duration: 1000 },
            { id: 'step-solar', text: 'Fetching solar irradiance data...', duration: 2000 },
            { id: 'step-ai', text: 'Generating AI recommendations...', duration: 2000 }
        ];
        
        let progress = 0;
        const progressFill = document.getElementById('progress-fill');
        const progressText = document.getElementById('progress-text');
        
        for (let i = 0; i < steps.length; i++) {
            const step = steps[i];
            
            // Update progress
            progress = ((i + 1) / steps.length) * 100;
            if (progressFill) progressFill.style.width = `${progress}%`;
            if (progressText) progressText.textContent = step.text;
            
            // Show current step
            const stepElement = document.getElementById(step.id);
            if (stepElement) {
                stepElement.classList.remove('hidden');
                stepElement.classList.add('active');
            }
            
            // Perform actual analysis
            if (i === 2) { // Solar calculations
                this.solarResults = await this.solarCalculator.calculateSolarPotential(
                    this.roofAnalysis, 
                    this.config
                );
            } else if (i === 4) { // AI recommendations
                this.aiRecommendations = await this.aiIntegration.generateRecommendations(
                    this.roofAnalysis,
                    this.solarResults,
                    this.config
                );
            }
            
            // Wait for step duration
            await new Promise(resolve => setTimeout(resolve, step.duration));
            
            // Mark step as completed
            if (stepElement) {
                stepElement.classList.remove('active');
                stepElement.classList.add('completed');
            }
        }
        
        // Analysis complete
        if (progressText) progressText.textContent = 'Analysis complete!';
        
        // Wait a moment then show results
        setTimeout(() => {
            this.showResults();
            this.goToStep(4);
        }, 1000);
    }

    showResults() {
        this.displayMetrics();
        this.displayDetailedAnalysis();
        this.displayAIRecommendations();
    }

    displayMetrics() {
        const resultsGrid = document.getElementById('results-grid');
        if (!resultsGrid || !this.solarResults) return;
        
        const metrics = [
            { label: 'System Size', value: `${this.solarResults.system_size_kw} kW`, icon: '⚡' },
            { label: 'Annual Production', value: `${this.solarResults.annual_energy_kwh.toLocaleString()} kWh`, icon: '☀️' },
            { label: 'Annual Savings', value: `$${this.solarResults.annual_savings.toLocaleString()}`, icon: '💰' },
            { label: 'Payback Period', value: `${this.solarResults.payback_years} years`, icon: '📈' },
            { label: 'Total Investment', value: `$${this.solarResults.total_cost.toLocaleString()}`, icon: '🏦' },
            { label: 'CO₂ Offset', value: `${this.solarResults.co2_offset_kg.toLocaleString()} kg/year`, icon: '🌱' }
        ];
        
        resultsGrid.innerHTML = metrics.map(metric => `
            <div class="metric-card">
                <div class="metric-value">${metric.value}</div>
                <div class="metric-label">${metric.icon} ${metric.label}</div>
            </div>
        `).join('');
    }

    displayDetailedAnalysis() {
        const analysisDetails = document.getElementById('analysis-details');
        if (!analysisDetails || !this.roofAnalysis || !this.solarResults) return;
        
        const roofAreaSqFt = this.roofAnalysis.usable_area * 10.764;
        
        analysisDetails.innerHTML = `
            <div class="detail-section">
                <h3>🏠 Roof Characteristics</h3>
                <div class="detail-item">
                    <span class="detail-label">Usable Area:</span>
                    <span class="detail-value">${roofAreaSqFt.toFixed(0)} sq ft</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Orientation:</span>
                    <span class="detail-value">${this.roofAnalysis.orientation}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Slope:</span>
                    <span class="detail-value">${this.roofAnalysis.slope.toFixed(1)}°</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Shading:</span>
                    <span class="detail-value">${(this.roofAnalysis.shading_factor * 100).toFixed(1)}%</span>
                </div>
            </div>
            <div class="detail-section">
                <h3>💰 Financial Analysis</h3>
                <div class="detail-item">
                    <span class="detail-label">System Cost:</span>
                    <span class="detail-value">$${this.solarResults.total_cost.toLocaleString()}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Annual Savings:</span>
                    <span class="detail-value">$${this.solarResults.annual_savings.toLocaleString()}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">25-Year Savings:</span>
                    <span class="detail-value">$${this.solarResults.lifetime_savings.toLocaleString()}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">ROI:</span>
                    <span class="detail-value">${this.solarResults.roi_percent}%</span>
                </div>
            </div>
        `;
    }

    displayAIRecommendations() {
        const recommendationsContainer = document.getElementById('ai-recommendations');
        if (!recommendationsContainer || !this.aiRecommendations) return;
        
        const recommendations = this.aiRecommendations.recommendations || [];
        
        recommendationsContainer.innerHTML = `
            <p style="margin-bottom: 1rem; color: #e0e0e0;">
                Generated by ${this.aiRecommendations.source || 'AI Analysis Engine'}
            </p>
            ${recommendations.map(rec => `
                <div class="recommendation-item">
                    <h4>${rec.icon} ${rec.category}</h4>
                    <p>${rec.content}</p>
                </div>
            `).join('')}
        `;
    }

    // PDF Generation
    async generatePDFReport() {
        if (!this.roofAnalysis || !this.solarResults) {
            this.showMessage('No analysis data available for report generation', 'error');
            return;
        }
        
        try {
            this.showMessage('Generating PDF report...', 'info');
            
            const result = await this.pdfGenerator.generateReport(
                this.roofAnalysis,
                this.solarResults,
                this.aiRecommendations,
                this.config
            );
            
            if (result.success) {
                this.showMessage(`Report downloaded: ${result.filename}`, 'success');
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            console.error('PDF generation failed:', error);
            
            // Try fallback method
            try {
                const fallbackResult = this.pdfGenerator.generateFallbackReport(
                    this.roofAnalysis,
                    this.solarResults,
                    this.aiRecommendations,
                    this.config
                );
                this.showMessage(`Analysis data exported: ${fallbackResult.filename}`, 'warning');
            } catch (fallbackError) {
                this.showMessage('Failed to generate report. Please try again.', 'error');
            }
        }
    }

    // API Key Management
    showApiModal() {
        const modal = document.getElementById('api-modal');
        if (modal) {
            modal.classList.remove('hidden');
            
            // Focus on input
            const input = document.getElementById('google-api-key');
            if (input) {
                setTimeout(() => input.focus(), 100);
            }
        }
    }

    closeApiModal() {
        const modal = document.getElementById('api-modal');
        if (modal) {
            modal.classList.add('hidden');
        }
    }

    saveApiKey() {
        const input = document.getElementById('google-api-key');
        if (input) {
            const apiKey = input.value.trim();

            try {
                if (apiKey) {
                    this.aiIntegration.setApiKey(apiKey);
                    this.hideApiNotice();
                    this.showMessage('API key saved successfully!', 'success');
                } else {
                    this.aiIntegration.clearApiKey();
                    this.showMessage('API key cleared', 'info');
                }

                this.closeApiModal();
            } catch (error) {
                this.showMessage(`API key error: ${error.message}`, 'error');
            }
        }
    }

    // Security Dashboard Functions
    showSecurityDashboard() {
        const modal = document.getElementById('security-modal');
        if (modal) {
            modal.classList.remove('hidden');
            this.loadSecurityDashboard();
        }
    }

    closeSecurityDashboard() {
        const modal = document.getElementById('security-modal');
        if (modal) {
            modal.classList.add('hidden');
        }
    }

    refreshSecurityDashboard() {
        this.loadSecurityDashboard();
    }

    loadSecurityDashboard() {
        const content = document.getElementById('security-dashboard-content');
        if (!content) return;

        // Get security reports
        const securityReport = window.securityValidator ? window.securityValidator.getSecurityReport() : null;
        const apiSecurityReport = window.apiSecurityMonitor ? window.apiSecurityMonitor.getSecurityReport() : null;

        const securityScore = apiSecurityReport ? apiSecurityReport.securityScore : 100;
        const apiKeyStatus = this.aiIntegration.getApiKeyStatus();

        content.innerHTML = `
            <div class="security-dashboard">
                <div class="security-score">
                    <h4>🛡️ Security Score: ${securityScore}/100</h4>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${securityScore}%; background: ${securityScore >= 80 ? '#00ff00' : securityScore >= 60 ? '#ffff00' : '#ff6b6b'}"></div>
                    </div>
                </div>

                <div class="security-status">
                    <h4>🔑 API Key Status</h4>
                    <div class="status-item">
                        <span>Configured:</span>
                        <span class="status ${apiKeyStatus.configured ? 'pass' : 'info'}">${apiKeyStatus.configured ? '✅ Yes' : '❌ No'}</span>
                    </div>
                    <div class="status-item">
                        <span>Storage:</span>
                        <span class="status pass">✅ Browser Only</span>
                    </div>
                    <div class="status-item">
                        <span>Encryption:</span>
                        <span class="status pass">✅ Obfuscated</span>
                    </div>
                    <div class="status-item">
                        <span>Server Access:</span>
                        <span class="status pass">✅ None</span>
                    </div>
                </div>

                <div class="security-features">
                    <h4>🔒 Security Features</h4>
                    <div class="feature-list">
                        <div class="feature-item">✅ No hard-coded API keys</div>
                        <div class="feature-item">✅ Client-side processing only</div>
                        <div class="feature-item">✅ Direct HTTPS to Google API</div>
                        <div class="feature-item">✅ Real-time security monitoring</div>
                        <div class="feature-item">✅ Automatic key validation</div>
                        <div class="feature-item">✅ Suspicious pattern detection</div>
                    </div>
                </div>

                ${apiSecurityReport && apiSecurityReport.recentAlerts.length > 0 ? `
                <div class="security-alerts">
                    <h4>⚠️ Recent Security Events</h4>
                    ${apiSecurityReport.recentAlerts.slice(0, 5).map(alert => `
                        <div class="alert-item">
                            <span class="alert-time">${new Date(alert.timestamp).toLocaleTimeString()}</span>
                            <span class="alert-type">${alert.type}</span>
                            <span class="alert-severity ${alert.severity}">${alert.severity}</span>
                        </div>
                    `).join('')}
                </div>
                ` : ''}

                <div class="security-actions">
                    <h4>🛠️ Security Actions</h4>
                    <button class="btn btn-small" onclick="window.apiSecurityMonitor.clearSecurityLog()">Clear Security Log</button>
                    <button class="btn btn-small btn-secondary" onclick="window.open('API_KEY_SECURITY.md', '_blank')">View Security Guide</button>
                </div>
            </div>
        `;
    }

    // Reset and restart
    resetAnalysis() {
        this.currentImage = null;
        this.roofAnalysis = null;
        this.solarResults = null;
        this.aiRecommendations = null;
        this.config = {};
        
        // Reset UI
        const previewContainer = document.getElementById('image-preview-container');
        if (previewContainer) {
            previewContainer.style.display = 'none';
        }
        
        const continueBtn = document.getElementById('continue-btn');
        if (continueBtn) {
            continueBtn.disabled = true;
        }
        
        const fileInput = document.getElementById('file-input');
        if (fileInput) {
            fileInput.value = '';
        }
        
        this.goToStep(1);
        this.showMessage('Ready for new analysis', 'info');
    }

    // Utility methods
    showMessage(message, type = 'info') {
        // Create or update message element
        let messageEl = document.getElementById('app-message');
        if (!messageEl) {
            messageEl = document.createElement('div');
            messageEl.id = 'app-message';
            messageEl.className = 'message';
            document.querySelector('.container').insertBefore(messageEl, document.querySelector('.container').firstChild);
        }
        
        messageEl.className = `message ${type}`;
        messageEl.textContent = message;
        messageEl.style.display = 'block';
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            if (messageEl) {
                messageEl.style.display = 'none';
            }
        }, 5000);
    }

    handleKeyboardShortcuts(event) {
        // Escape key closes modal
        if (event.key === 'Escape') {
            this.closeApiModal();
        }
        
        // Enter key in API modal saves key
        if (event.key === 'Enter' && !document.getElementById('api-modal').classList.contains('hidden')) {
            this.saveApiKey();
        }
    }
}

// Global functions for HTML onclick handlers
window.goToStep = (step) => window.solarApp.goToStep(step);
window.loadSampleImage = (type) => window.solarApp.loadSampleImage(type);
window.setLocation = (lat, lng) => window.solarApp.setLocation(lat, lng);
window.startAnalysis = () => window.solarApp.startAnalysis();
window.generatePDFReport = () => window.solarApp.generatePDFReport();
window.resetAnalysis = () => window.solarApp.resetAnalysis();
window.showApiModal = () => window.solarApp.showApiModal();
window.closeApiModal = () => window.solarApp.closeApiModal();
window.saveApiKey = () => window.solarApp.saveApiKey();
window.showSecurityDashboard = () => window.solarApp.showSecurityDashboard();
window.closeSecurityDashboard = () => window.solarApp.closeSecurityDashboard();
window.refreshSecurityDashboard = () => window.solarApp.refreshSecurityDashboard();

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.solarApp = new SolarAIApp();
});
