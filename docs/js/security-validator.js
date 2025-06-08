// Security Validator for Solar AI Platform
class SecurityValidator {
    constructor() {
        this.securityChecks = [];
        this.init();
    }

    init() {
        // Run security validation on page load
        this.validateEnvironment();
        this.validateSecureContext();
        this.validateCSP();
        this.validateLocalStorage();
        this.setupSecurityMonitoring();
    }

    validateEnvironment() {
        // Check for development vs production environment
        const isDevelopment = window.location.hostname === 'localhost' || 
                             window.location.hostname === '127.0.0.1';
        const isProduction = window.location.protocol === 'https:' && 
                           window.location.hostname.includes('github.io');

        if (!isDevelopment && !isProduction) {
            this.logSecurityWarning('Unknown deployment environment detected');
        }

        // Ensure HTTPS in production
        if (!isDevelopment && window.location.protocol !== 'https:') {
            this.logSecurityError('Insecure HTTP connection detected in production');
        }

        this.logSecurityInfo(`Environment: ${isDevelopment ? 'Development' : 'Production'}`);
    }

    validateSecureContext() {
        // Check if running in secure context
        if (!window.isSecureContext) {
            this.logSecurityWarning('Not running in secure context (HTTPS required for full functionality)');
        }

        // Check for mixed content
        if (window.location.protocol === 'https:' && document.querySelector('script[src^="http:"]')) {
            this.logSecurityError('Mixed content detected: HTTP resources on HTTPS page');
        }
    }

    validateCSP() {
        // Check if Content Security Policy is implemented
        const metaCSP = document.querySelector('meta[http-equiv="Content-Security-Policy"]');
        if (!metaCSP) {
            this.logSecurityWarning('Content Security Policy not found in meta tags');
        } else {
            this.logSecurityInfo('Content Security Policy detected');
        }

        // Check for inline scripts (potential XSS risk)
        const inlineScripts = document.querySelectorAll('script:not([src])');
        if (inlineScripts.length > 0) {
            this.logSecurityWarning(`${inlineScripts.length} inline scripts detected`);
        }
    }

    validateLocalStorage() {
        try {
            // Check localStorage availability
            localStorage.setItem('security_test', 'test');
            localStorage.removeItem('security_test');
            this.logSecurityInfo('localStorage available and functional');

            // Check for sensitive data patterns in localStorage
            const sensitivePatterns = ['password', 'secret', 'private_key', 'token'];
            let foundSensitive = false;

            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                const value = localStorage.getItem(key);
                
                sensitivePatterns.forEach(pattern => {
                    if (key.toLowerCase().includes(pattern) || 
                        (value && value.toLowerCase().includes(pattern))) {
                        this.logSecurityWarning(`Potentially sensitive data in localStorage: ${key}`);
                        foundSensitive = true;
                    }
                });
            }

            if (!foundSensitive) {
                this.logSecurityInfo('No obvious sensitive data patterns in localStorage');
            }

        } catch (error) {
            this.logSecurityError('localStorage not available or blocked');
        }
    }

    setupSecurityMonitoring() {
        // Monitor for potential security issues
        this.setupErrorMonitoring();
        this.setupNetworkMonitoring();
        this.setupDOMMonitoring();
    }

    setupErrorMonitoring() {
        // Global error handler for security-related errors
        window.addEventListener('error', (event) => {
            const error = event.error;
            if (error && error.message) {
                // Check for security-related errors
                const securityKeywords = ['cors', 'csp', 'mixed content', 'insecure', 'blocked'];
                if (securityKeywords.some(keyword => 
                    error.message.toLowerCase().includes(keyword))) {
                    this.logSecurityError(`Security-related error: ${error.message}`);
                }
            }
        });

        // Unhandled promise rejection handler
        window.addEventListener('unhandledrejection', (event) => {
            if (event.reason && event.reason.message) {
                const securityKeywords = ['cors', 'network', 'fetch', 'api'];
                if (securityKeywords.some(keyword => 
                    event.reason.message.toLowerCase().includes(keyword))) {
                    this.logSecurityWarning(`Network/API error: ${event.reason.message}`);
                }
            }
        });
    }

    setupNetworkMonitoring() {
        // Monitor fetch requests for security issues
        const originalFetch = window.fetch;
        window.fetch = async (...args) => {
            const url = args[0];
            
            // Check for insecure HTTP requests
            if (typeof url === 'string' && url.startsWith('http://') && 
                window.location.protocol === 'https:') {
                this.logSecurityWarning(`Insecure HTTP request attempted: ${url}`);
            }

            // Check for suspicious domains
            if (typeof url === 'string') {
                const suspiciousDomains = ['bit.ly', 'tinyurl.com', 'goo.gl'];
                if (suspiciousDomains.some(domain => url.includes(domain))) {
                    this.logSecurityWarning(`Request to potentially suspicious domain: ${url}`);
                }
            }

            return originalFetch.apply(this, args);
        };
    }

    setupDOMMonitoring() {
        // Monitor for dynamic script injection
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        if (node.tagName === 'SCRIPT') {
                            this.logSecurityWarning('Dynamic script element added to DOM');
                        }
                        
                        // Check for suspicious attributes
                        if (node.hasAttribute && node.hasAttribute('onclick')) {
                            this.logSecurityWarning('Element with onclick handler added to DOM');
                        }
                    }
                });
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    // API Key Security Validation
    validateApiKey(apiKey, provider = 'google') {
        const validationRules = {
            google: {
                minLength: 20,
                maxLength: 50,
                pattern: /^[A-Za-z0-9_-]+$/,
                forbiddenPatterns: ['test', 'demo', 'example', 'your_api_key']
            }
        };

        const rules = validationRules[provider];
        if (!rules) {
            this.logSecurityWarning(`Unknown API provider: ${provider}`);
            return false;
        }

        // Length check
        if (apiKey.length < rules.minLength || apiKey.length > rules.maxLength) {
            this.logSecurityError(`API key length invalid for ${provider}`);
            return false;
        }

        // Pattern check
        if (!rules.pattern.test(apiKey)) {
            this.logSecurityError(`API key format invalid for ${provider}`);
            return false;
        }

        // Forbidden patterns check
        const lowerKey = apiKey.toLowerCase();
        if (rules.forbiddenPatterns.some(pattern => lowerKey.includes(pattern))) {
            this.logSecurityError(`API key contains forbidden pattern for ${provider}`);
            return false;
        }

        this.logSecurityInfo(`API key validation passed for ${provider}`);
        return true;
    }

    // Rate limiting validation
    validateRateLimit(endpoint, maxRequests = 10, windowMs = 60000) {
        const key = `rate_limit_${endpoint}`;
        const now = Date.now();
        
        let requests = JSON.parse(localStorage.getItem(key) || '[]');
        requests = requests.filter(time => now - time < windowMs);

        if (requests.length >= maxRequests) {
            this.logSecurityWarning(`Rate limit exceeded for ${endpoint}`);
            return false;
        }

        requests.push(now);
        localStorage.setItem(key, JSON.stringify(requests));
        return true;
    }

    // Logging methods
    logSecurityInfo(message) {
        console.log(`🔒 [SECURITY INFO] ${message}`);
        this.securityChecks.push({ level: 'info', message, timestamp: new Date() });
    }

    logSecurityWarning(message) {
        console.warn(`⚠️ [SECURITY WARNING] ${message}`);
        this.securityChecks.push({ level: 'warning', message, timestamp: new Date() });
    }

    logSecurityError(message) {
        console.error(`🚨 [SECURITY ERROR] ${message}`);
        this.securityChecks.push({ level: 'error', message, timestamp: new Date() });
    }

    // Get security report
    getSecurityReport() {
        const report = {
            timestamp: new Date(),
            environment: {
                hostname: window.location.hostname,
                protocol: window.location.protocol,
                isSecureContext: window.isSecureContext
            },
            checks: this.securityChecks,
            summary: {
                total: this.securityChecks.length,
                errors: this.securityChecks.filter(c => c.level === 'error').length,
                warnings: this.securityChecks.filter(c => c.level === 'warning').length,
                info: this.securityChecks.filter(c => c.level === 'info').length
            }
        };

        return report;
    }

    // Clear sensitive data
    clearSensitiveData() {
        const sensitiveKeys = ['solar_ai_google_key', 'api_key', 'token', 'secret'];
        
        sensitiveKeys.forEach(key => {
            if (localStorage.getItem(key)) {
                localStorage.removeItem(key);
                this.logSecurityInfo(`Cleared sensitive data: ${key}`);
            }
        });

        // Clear rate limiting data
        for (let i = localStorage.length - 1; i >= 0; i--) {
            const key = localStorage.key(i);
            if (key && key.startsWith('rate_limit_')) {
                localStorage.removeItem(key);
            }
        }

        this.logSecurityInfo('Sensitive data cleanup completed');
    }
}

// Initialize security validator
window.addEventListener('DOMContentLoaded', () => {
    window.securityValidator = new SecurityValidator();
});

// Export for manual use
window.SecurityValidator = SecurityValidator;
