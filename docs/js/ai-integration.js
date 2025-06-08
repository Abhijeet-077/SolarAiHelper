// AI Integration Module for Solar AI Platform
class AIIntegration {
    constructor() {
        this.apiKey = null;
        this.isConfigured = false;
        this.fallbackRecommendations = this.getFallbackRecommendations();
    }

    setApiKey(apiKey) {
        // Security: Comprehensive API key validation
        if (apiKey && !this.isApiKeyValid(apiKey)) {
            throw new Error('Invalid API key format. Google API keys should be 20+ characters.');
        }

        // Security: Check for potentially compromised keys
        if (apiKey && this.isKeyPotentiallyCompromised(apiKey)) {
            throw new Error('This API key appears to be from a public example or documentation. Please use your own private key.');
        }

        this.apiKey = apiKey;
        this.isConfigured = !!apiKey;

        // Store in localStorage for persistence (client-side only)
        if (apiKey) {
            // Security: Encrypt key before storing (basic obfuscation)
            const obfuscatedKey = this.obfuscateKey(apiKey);
            localStorage.setItem('solar_ai_google_key', obfuscatedKey);
            console.log('🔑 API key configured (stored locally in browser with obfuscation)');

            // Security: Log key usage for monitoring
            this.logKeyUsage('configured');
        } else {
            localStorage.removeItem('solar_ai_google_key');
            console.log('🔑 API key cleared');
            this.logKeyUsage('cleared');
        }
    }

    loadApiKey() {
        const storedKey = localStorage.getItem('solar_ai_google_key');
        if (storedKey) {
            try {
                // Security: Deobfuscate key before use
                const deobfuscatedKey = this.deobfuscateKey(storedKey);
                this.apiKey = deobfuscatedKey;
                this.isConfigured = true;
                this.logKeyUsage('loaded');
            } catch (error) {
                console.warn('🔑 Stored API key appears corrupted, clearing...');
                localStorage.removeItem('solar_ai_google_key');
                this.apiKey = null;
                this.isConfigured = false;
            }
        }
    }

    async generateRecommendations(roofAnalysis, solarResults, config) {
        if (this.isConfigured) {
            try {
                return await this.generateAIRecommendations(roofAnalysis, solarResults, config);
            } catch (error) {
                console.error('AI recommendation failed:', error);
                return this.generateFallbackRecommendations(roofAnalysis, solarResults, config);
            }
        } else {
            return this.generateFallbackRecommendations(roofAnalysis, solarResults, config);
        }
    }

    async generateAIRecommendations(roofAnalysis, solarResults, config) {
        const prompt = this.buildPrompt(roofAnalysis, solarResults, config);
        
        try {
            const response = await fetch('https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=' + this.apiKey, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    contents: [{
                        parts: [{
                            text: prompt
                        }]
                    }],
                    generationConfig: {
                        temperature: 0.7,
                        topK: 40,
                        topP: 0.95,
                        maxOutputTokens: 1024,
                    }
                })
            });

            if (!response.ok) {
                throw new Error(`API request failed: ${response.status}`);
            }

            const data = await response.json();
            
            if (data.candidates && data.candidates[0] && data.candidates[0].content) {
                const aiText = data.candidates[0].content.parts[0].text;
                return this.parseAIResponse(aiText);
            } else {
                throw new Error('Invalid API response format');
            }
        } catch (error) {
            console.error('Google AI API error:', error);
            throw error;
        }
    }

    buildPrompt(roofAnalysis, solarResults, config) {
        return `As a solar energy expert, analyze this rooftop solar installation and provide detailed recommendations:

ROOF ANALYSIS:
- Usable Area: ${roofAnalysis.usable_area} m²
- Orientation: ${roofAnalysis.orientation}
- Slope: ${roofAnalysis.slope}°
- Shading Factor: ${(roofAnalysis.shading_factor * 100).toFixed(1)}%

SYSTEM SPECIFICATIONS:
- System Size: ${solarResults.system_size_kw} kW
- Panel Count: ${solarResults.panel_count}
- Panel Type: ${config.panelType}
- Annual Energy: ${solarResults.annual_energy_kwh} kWh

FINANCIAL METRICS:
- Total Cost: $${solarResults.total_cost.toLocaleString()}
- Annual Savings: $${solarResults.annual_savings.toLocaleString()}
- Payback Period: ${solarResults.payback_years} years
- ROI: ${solarResults.roi_percent}%

LOCATION:
- Latitude: ${config.latitude}
- Longitude: ${config.longitude}
- Electricity Rate: $${config.electricityRate}/kWh

Please provide recommendations in the following categories:
1. INSTALLATION OPTIMIZATION
2. FINANCIAL CONSIDERATIONS
3. MAINTENANCE PLANNING
4. PERFORMANCE MAXIMIZATION
5. REGULATORY COMPLIANCE

Format your response as structured recommendations with clear headings and actionable advice. Keep each section concise but informative.`;
    }

    parseAIResponse(aiText) {
        // Parse the AI response into structured recommendations
        const sections = aiText.split(/\d+\.\s+([A-Z\s]+)/);
        const recommendations = [];

        for (let i = 1; i < sections.length; i += 2) {
            if (sections[i] && sections[i + 1]) {
                const title = sections[i].trim();
                const content = sections[i + 1].trim();
                
                recommendations.push({
                    category: title,
                    content: content,
                    priority: this.determinePriority(title),
                    icon: this.getIconForCategory(title)
                });
            }
        }

        // If parsing failed, create a single recommendation with the full text
        if (recommendations.length === 0) {
            recommendations.push({
                category: 'AI Analysis',
                content: aiText,
                priority: 'medium',
                icon: '🤖'
            });
        }

        return {
            recommendations: recommendations,
            source: 'Google Gemini AI',
            timestamp: new Date().toISOString()
        };
    }

    generateFallbackRecommendations(roofAnalysis, solarResults, config) {
        const recommendations = [];

        // Installation optimization
        if (roofAnalysis.orientation !== 'South') {
            recommendations.push({
                category: 'Installation Optimization',
                content: `Your roof faces ${roofAnalysis.orientation}, which may reduce energy production by 5-15% compared to south-facing installations. Consider micro-inverters or power optimizers to maximize energy harvest from each panel.`,
                priority: 'medium',
                icon: '🔧'
            });
        }

        if (roofAnalysis.slope < 15 || roofAnalysis.slope > 40) {
            recommendations.push({
                category: 'Installation Optimization',
                content: `Your roof slope of ${roofAnalysis.slope}° is outside the optimal range (15-40°). Consider tilt racks to optimize panel angle for maximum solar exposure.`,
                priority: 'medium',
                icon: '📐'
            });
        }

        // Financial considerations
        if (solarResults.payback_years > 10) {
            recommendations.push({
                category: 'Financial Considerations',
                content: `With a payback period of ${solarResults.payback_years} years, consider exploring federal and state incentives, net metering programs, or financing options to improve the financial return.`,
                priority: 'high',
                icon: '💰'
            });
        } else {
            recommendations.push({
                category: 'Financial Considerations',
                content: `Excellent financial outlook with a ${solarResults.payback_years}-year payback period! This system will generate significant long-term savings. Consider maximizing the system size if budget allows.`,
                priority: 'low',
                icon: '💰'
            });
        }

        // Shading considerations
        if (roofAnalysis.shading_factor > 0.15) {
            recommendations.push({
                category: 'Performance Maximization',
                content: `Your roof has ${(roofAnalysis.shading_factor * 100).toFixed(1)}% shading. Consider tree trimming, power optimizers, or microinverters to minimize shading impact. Each 1% reduction in shading can increase annual production by 1-2%.`,
                priority: 'high',
                icon: '🌳'
            });
        }

        // System size recommendations
        if (solarResults.system_size_kw < 5) {
            recommendations.push({
                category: 'System Sizing',
                content: `Your ${solarResults.system_size_kw} kW system is relatively small. Consider maximizing the available roof space to take advantage of economies of scale and better cost per watt.`,
                priority: 'medium',
                icon: '📏'
            });
        }

        // Maintenance planning
        recommendations.push({
            category: 'Maintenance Planning',
            content: `Plan for annual system inspections and cleaning. Monitor energy production monthly to identify any performance issues early. Most systems require minimal maintenance but benefit from professional inspection every 2-3 years.`,
            priority: 'low',
            icon: '🔧'
        });

        // Panel type optimization
        if (config.panelType === 'thin-film') {
            recommendations.push({
                category: 'Technology Optimization',
                content: `Thin-film panels have lower efficiency but work better in high temperatures and partial shading. Consider monocrystalline panels if roof space is limited and you want maximum power density.`,
                priority: 'medium',
                icon: '⚡'
            });
        }

        return {
            recommendations: recommendations,
            source: 'Built-in Analysis Engine',
            timestamp: new Date().toISOString()
        };
    }

    determinePriority(category) {
        const highPriorityKeywords = ['financial', 'cost', 'savings', 'shading', 'performance'];
        const lowPriorityKeywords = ['maintenance', 'compliance', 'monitoring'];
        
        const categoryLower = category.toLowerCase();
        
        if (highPriorityKeywords.some(keyword => categoryLower.includes(keyword))) {
            return 'high';
        } else if (lowPriorityKeywords.some(keyword => categoryLower.includes(keyword))) {
            return 'low';
        } else {
            return 'medium';
        }
    }

    getIconForCategory(category) {
        const categoryLower = category.toLowerCase();
        
        if (categoryLower.includes('installation') || categoryLower.includes('optimization')) {
            return '🔧';
        } else if (categoryLower.includes('financial') || categoryLower.includes('cost')) {
            return '💰';
        } else if (categoryLower.includes('maintenance')) {
            return '🛠️';
        } else if (categoryLower.includes('performance')) {
            return '⚡';
        } else if (categoryLower.includes('regulatory') || categoryLower.includes('compliance')) {
            return '📋';
        } else {
            return '💡';
        }
    }

    getFallbackRecommendations() {
        return {
            general: [
                {
                    category: 'System Optimization',
                    content: 'Consider the orientation and tilt of your panels for maximum energy production. South-facing panels with a 30-35° tilt typically perform best.',
                    priority: 'high',
                    icon: '☀️'
                },
                {
                    category: 'Financial Planning',
                    content: 'Research available federal, state, and local incentives. The federal solar tax credit can significantly reduce your installation costs.',
                    priority: 'high',
                    icon: '💰'
                },
                {
                    category: 'Maintenance',
                    content: 'Plan for regular system monitoring and occasional cleaning. Most solar systems require minimal maintenance but benefit from annual inspections.',
                    priority: 'medium',
                    icon: '🔧'
                }
            ]
        };
    }

    // Utility methods
    isApiKeyValid(apiKey) {
        // Security: Comprehensive API key validation
        if (!apiKey || typeof apiKey !== 'string') {
            return false;
        }

        // Google API keys are typically 39 characters, alphanumeric with specific patterns
        if (apiKey.length < 20 || apiKey.length > 50) {
            return false;
        }

        // Check for placeholder values
        const placeholders = ['your_api_key', 'your_google_api_key', 'api_key_here', 'replace_me'];
        if (placeholders.some(placeholder => apiKey.toLowerCase().includes(placeholder))) {
            return false;
        }

        // Check for obvious test values
        const testPatterns = ['test', 'demo', 'example', '123456', 'abcdef'];
        if (testPatterns.some(pattern => apiKey.toLowerCase().includes(pattern))) {
            return false;
        }

        return true;
    }

    getApiKeyStatus() {
        return {
            configured: this.isConfigured,
            hasKey: !!this.apiKey,
            keyLength: this.apiKey ? this.apiKey.length : 0
        };
    }

    clearApiKey() {
        this.setApiKey(null);
    }

    // Security helper methods
    isKeyPotentiallyCompromised(apiKey) {
        // Check against known public/example keys
        const compromisedPatterns = [
            'AIzaSyDemoKey',
            'AIzaSyExample',
            'your_api_key_here',
            'replace_with_your_key',
            'demo_key',
            'test_key',
            'sample_key',
            'AIzaSyC4K8B9X2M5N7P1Q3R6S8T0U2V4W6X8Y0Z' // Common example key
        ];

        return compromisedPatterns.some(pattern =>
            apiKey.toLowerCase().includes(pattern.toLowerCase())
        );
    }

    obfuscateKey(key) {
        // Simple obfuscation (not encryption, just makes it less obvious)
        const prefix = 'sk_';
        const encoded = btoa(key).split('').reverse().join('');
        return prefix + encoded;
    }

    deobfuscateKey(obfuscatedKey) {
        if (!obfuscatedKey.startsWith('sk_')) {
            // Legacy key format, return as-is
            return obfuscatedKey;
        }

        const encoded = obfuscatedKey.substring(3);
        const decoded = atob(encoded.split('').reverse().join(''));
        return decoded;
    }

    logKeyUsage(action) {
        // Security logging (no sensitive data)
        const timestamp = new Date().toISOString();
        const logEntry = {
            timestamp,
            action,
            userAgent: navigator.userAgent.substring(0, 50),
            origin: window.location.origin
        };

        // Store in separate log storage
        const logs = JSON.parse(localStorage.getItem('solar_ai_security_log') || '[]');
        logs.push(logEntry);

        // Keep only last 50 entries
        if (logs.length > 50) {
            logs.splice(0, logs.length - 50);
        }

        localStorage.setItem('solar_ai_security_log', JSON.stringify(logs));
    }
}

// Export for use in other modules
window.AIIntegration = AIIntegration;
