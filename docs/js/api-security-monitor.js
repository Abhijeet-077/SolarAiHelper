// API Security Monitor for Solar AI Platform
class APISecurityMonitor {
    constructor() {
        this.securityEvents = [];
        this.suspiciousPatterns = [
            'AIzaSyDemoKey',
            'AIzaSyExample',
            'your_api_key_here',
            'demo_key',
            'test_key',
            'sample_key'
        ];
        this.init();
    }

    init() {
        this.monitorNetworkRequests();
        this.monitorLocalStorage();
        this.monitorConsoleAccess();
        this.setupPeriodicScans();
        console.log('🔒 API Security Monitor initialized');
    }

    monitorNetworkRequests() {
        // Override fetch to monitor API calls
        const originalFetch = window.fetch;
        const self = this;
        
        window.fetch = async function(...args) {
            const url = args[0];
            const options = args[1] || {};
            
            // Check for API key exposure in URL
            if (typeof url === 'string') {
                self.checkUrlForApiKeys(url);
                
                // Monitor Google API calls
                if (url.includes('generativelanguage.googleapis.com')) {
                    self.logSecurityEvent('google_api_call', {
                        timestamp: new Date().toISOString(),
                        url: url.split('?')[0], // Remove query params for logging
                        hasKey: url.includes('key='),
                        origin: window.location.origin
                    });
                }
            }
            
            // Check headers for exposed keys
            if (options.headers) {
                self.checkHeadersForApiKeys(options.headers);
            }
            
            return originalFetch.apply(this, args);
        };
    }

    monitorLocalStorage() {
        // Override localStorage methods to monitor key storage
        const originalSetItem = localStorage.setItem;
        const originalGetItem = localStorage.getItem;
        const self = this;
        
        localStorage.setItem = function(key, value) {
            if (key.toLowerCase().includes('api') || key.toLowerCase().includes('key')) {
                self.logSecurityEvent('localStorage_api_key_set', {
                    key: key,
                    timestamp: new Date().toISOString(),
                    valueLength: value ? value.length : 0
                });
                
                // Check for suspicious values
                if (value && self.isSuspiciousApiKey(value)) {
                    self.logSecurityEvent('suspicious_api_key_detected', {
                        key: key,
                        timestamp: new Date().toISOString(),
                        reason: 'matches_known_example_pattern'
                    });
                    
                    console.warn('🚨 Suspicious API key detected! This appears to be an example key.');
                }
            }
            
            return originalSetItem.apply(this, arguments);
        };
        
        localStorage.getItem = function(key) {
            if (key.toLowerCase().includes('api') || key.toLowerCase().includes('key')) {
                self.logSecurityEvent('localStorage_api_key_get', {
                    key: key,
                    timestamp: new Date().toISOString()
                });
            }
            
            return originalGetItem.apply(this, arguments);
        };
    }

    monitorConsoleAccess() {
        // Monitor console access to API keys
        const originalLog = console.log;
        const originalWarn = console.warn;
        const originalError = console.error;
        const self = this;
        
        const wrapConsoleMethod = (originalMethod, level) => {
            return function(...args) {
                // Check if any arguments contain API keys
                args.forEach(arg => {
                    if (typeof arg === 'string' && self.containsApiKey(arg)) {
                        self.logSecurityEvent('api_key_console_exposure', {
                            level: level,
                            timestamp: new Date().toISOString(),
                            message: 'API key detected in console output'
                        });
                        
                        // Replace API key with masked version
                        arg = self.maskApiKey(arg);
                    }
                });
                
                return originalMethod.apply(this, args);
            };
        };
        
        console.log = wrapConsoleMethod(originalLog, 'log');
        console.warn = wrapConsoleMethod(originalWarn, 'warn');
        console.error = wrapConsoleMethod(originalError, 'error');
    }

    setupPeriodicScans() {
        // Scan for exposed API keys every 30 seconds
        setInterval(() => {
            this.scanForExposedKeys();
        }, 30000);
        
        // Full security audit every 5 minutes
        setInterval(() => {
            this.performSecurityAudit();
        }, 300000);
    }

    checkUrlForApiKeys(url) {
        if (this.containsApiKey(url)) {
            this.logSecurityEvent('api_key_in_url', {
                timestamp: new Date().toISOString(),
                url: this.maskApiKey(url),
                severity: 'high'
            });
            
            console.error('🚨 SECURITY ALERT: API key detected in URL! This is a security risk.');
        }
    }

    checkHeadersForApiKeys(headers) {
        Object.entries(headers).forEach(([key, value]) => {
            if (typeof value === 'string' && this.containsApiKey(value)) {
                this.logSecurityEvent('api_key_in_header', {
                    timestamp: new Date().toISOString(),
                    header: key,
                    severity: 'high'
                });
                
                console.error(`🚨 SECURITY ALERT: API key detected in header "${key}"!`);
            }
        });
    }

    scanForExposedKeys() {
        // Scan DOM for exposed API keys
        const textContent = document.body.textContent || '';
        if (this.containsApiKey(textContent)) {
            this.logSecurityEvent('api_key_in_dom', {
                timestamp: new Date().toISOString(),
                severity: 'critical'
            });
            
            console.error('🚨 CRITICAL: API key found in DOM content!');
        }
        
        // Scan localStorage for unencrypted keys
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            const value = localStorage.getItem(key);
            
            if (value && this.containsApiKey(value) && !key.startsWith('sk_')) {
                this.logSecurityEvent('unencrypted_api_key_storage', {
                    timestamp: new Date().toISOString(),
                    storageKey: key,
                    severity: 'medium'
                });
            }
        }
    }

    performSecurityAudit() {
        const audit = {
            timestamp: new Date().toISOString(),
            totalEvents: this.securityEvents.length,
            recentEvents: this.securityEvents.filter(e => 
                new Date() - new Date(e.timestamp) < 300000 // Last 5 minutes
            ).length,
            suspiciousActivity: this.securityEvents.filter(e => 
                e.severity === 'high' || e.severity === 'critical'
            ).length,
            apiKeyStorageSecure: this.isApiKeyStorageSecure(),
            networkRequestsSecure: this.areNetworkRequestsSecure()
        };
        
        this.logSecurityEvent('security_audit', audit);
        
        // Alert if suspicious activity detected
        if (audit.suspiciousActivity > 0) {
            console.warn(`🔒 Security Audit: ${audit.suspiciousActivity} suspicious events detected`);
        }
    }

    containsApiKey(text) {
        if (!text || typeof text !== 'string') return false;
        
        // Google API key pattern
        const googleApiPattern = /AIza[0-9A-Za-z_-]{35}/g;
        return googleApiPattern.test(text);
    }

    isSuspiciousApiKey(key) {
        if (!key || typeof key !== 'string') return false;
        
        return this.suspiciousPatterns.some(pattern => 
            key.toLowerCase().includes(pattern.toLowerCase())
        );
    }

    maskApiKey(text) {
        if (!text || typeof text !== 'string') return text;
        
        // Replace API keys with masked version
        return text.replace(/AIza[0-9A-Za-z_-]{35}/g, 'AIza****MASKED****');
    }

    isApiKeyStorageSecure() {
        // Check if API keys are properly obfuscated
        const apiKeyItem = localStorage.getItem('solar_ai_google_key');
        if (!apiKeyItem) return true; // No key stored
        
        // Should be obfuscated (start with sk_)
        return apiKeyItem.startsWith('sk_');
    }

    areNetworkRequestsSecure() {
        // Check recent network events for security issues
        const recentNetworkEvents = this.securityEvents.filter(e => 
            e.type === 'google_api_call' && 
            new Date() - new Date(e.timestamp) < 300000
        );
        
        // All should be HTTPS
        return recentNetworkEvents.every(e => 
            e.data && e.data.url && e.data.url.startsWith('https://')
        );
    }

    logSecurityEvent(type, data) {
        const event = {
            type,
            timestamp: new Date().toISOString(),
            data,
            severity: data.severity || 'info'
        };
        
        this.securityEvents.push(event);
        
        // Keep only last 1000 events
        if (this.securityEvents.length > 1000) {
            this.securityEvents.splice(0, this.securityEvents.length - 1000);
        }
        
        // Store in localStorage for persistence
        try {
            localStorage.setItem('solar_ai_security_events', 
                JSON.stringify(this.securityEvents.slice(-100)) // Keep last 100
            );
        } catch (error) {
            console.warn('Failed to store security events:', error);
        }
    }

    getSecurityReport() {
        return {
            timestamp: new Date().toISOString(),
            totalEvents: this.securityEvents.length,
            eventsByType: this.groupEventsByType(),
            recentAlerts: this.securityEvents
                .filter(e => e.severity === 'high' || e.severity === 'critical')
                .slice(-10),
            securityScore: this.calculateSecurityScore(),
            recommendations: this.getSecurityRecommendations()
        };
    }

    groupEventsByType() {
        const grouped = {};
        this.securityEvents.forEach(event => {
            grouped[event.type] = (grouped[event.type] || 0) + 1;
        });
        return grouped;
    }

    calculateSecurityScore() {
        const criticalEvents = this.securityEvents.filter(e => e.severity === 'critical').length;
        const highEvents = this.securityEvents.filter(e => e.severity === 'high').length;
        const mediumEvents = this.securityEvents.filter(e => e.severity === 'medium').length;
        
        let score = 100;
        score -= criticalEvents * 20;
        score -= highEvents * 10;
        score -= mediumEvents * 5;
        
        return Math.max(0, score);
    }

    getSecurityRecommendations() {
        const recommendations = [];
        
        if (!this.isApiKeyStorageSecure()) {
            recommendations.push('API key storage should be obfuscated');
        }
        
        if (!this.areNetworkRequestsSecure()) {
            recommendations.push('All network requests should use HTTPS');
        }
        
        const recentCritical = this.securityEvents.filter(e => 
            e.severity === 'critical' && 
            new Date() - new Date(e.timestamp) < 3600000 // Last hour
        );
        
        if (recentCritical.length > 0) {
            recommendations.push('Critical security events detected in the last hour');
        }
        
        return recommendations;
    }

    clearSecurityLog() {
        this.securityEvents = [];
        localStorage.removeItem('solar_ai_security_events');
        console.log('🔒 Security log cleared');
    }
}

// Initialize security monitor
window.addEventListener('DOMContentLoaded', () => {
    window.apiSecurityMonitor = new APISecurityMonitor();
});

// Export for manual use
window.APISecurityMonitor = APISecurityMonitor;
