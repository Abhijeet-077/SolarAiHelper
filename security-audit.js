#!/usr/bin/env node

/**
 * Security Audit Script for Solar AI Platform
 * 
 * This script performs a comprehensive security audit to ensure
 * no API keys or sensitive information are present in the codebase.
 * 
 * Usage: node security-audit.js
 */

const fs = require('fs');
const path = require('path');

class SecurityAuditor {
    constructor() {
        this.findings = [];
        this.scannedFiles = 0;
        this.suspiciousPatterns = [
            // Google API Keys
            /AIza[0-9A-Za-z_-]{35}/g,
            
            // Generic API key patterns
            /api[_-]?key[_-]?[:=]\s*['""][^'""]+['"]/gi,
            /secret[_-]?key[_-]?[:=]\s*['""][^'""]+['"]/gi,
            /access[_-]?token[_-]?[:=]\s*['""][^'""]+['"]/gi,
            
            // Environment variable patterns
            /process\.env\.[A-Z_]+[_-]?(KEY|SECRET|TOKEN|PASSWORD)/gi,
            
            // Common secret patterns
            /password[_-]?[:=]\s*['""][^'""]+['"]/gi,
            /token[_-]?[:=]\s*['""][^'""]+['"]/gi,
            
            // Hardcoded credentials
            /['""]AIza[0-9A-Za-z_-]{35}['"]/g,
            /['""]sk-[a-zA-Z0-9]{48}['"]/g, // OpenAI keys
            /['""]xoxb-[0-9]+-[0-9]+-[0-9]+-[a-fA-F0-9]{32}['"]/g, // Slack tokens
        ];
        
        this.allowedPatterns = [
            // These are safe patterns that might match but are not actual secrets
            'your_api_key_here',
            'your_google_api_key',
            'api_key_placeholder',
            'demo_key',
            'test_key',
            'example_key',
            'AIzaSyDemoKey',
            'AIzaSyExample',
            'AIzaSyC4K8B9X2M5N7P1Q3R6S8T0U2V4W6X8Y0Z' // Common documentation example
        ];

        this.excludeFiles = [
            'package-lock.json',
            'yarn.lock',
            '.DS_Store',
            'security-audit.js', // This file itself
            'SECURITY_GUIDE.md', // Documentation with examples
            'API_KEY_SECURITY.md', // Security documentation
            'USER_GUIDE.md', // User documentation
            'DEPLOYMENT_GUIDE.md' // Deployment documentation
        ];
        
        this.excludeDirectories = [
            'node_modules',
            '.git',
            'dist',
            'build',
            '.next',
            'coverage',
            '.nyc_output'
        ];
        

    }

    async audit(directory = '.') {
        console.log('🔍 Starting security audit...\n');
        
        await this.scanDirectory(directory);
        
        console.log(`\n📊 Audit Results:`);
        console.log(`Files scanned: ${this.scannedFiles}`);
        console.log(`Security findings: ${this.findings.length}\n`);
        
        if (this.findings.length === 0) {
            console.log('✅ No security issues found! Your codebase is clean.');
            return true;
        } else {
            console.log('🚨 Security issues found:\n');
            this.findings.forEach((finding, index) => {
                console.log(`${index + 1}. ${finding.severity.toUpperCase()}: ${finding.file}`);
                console.log(`   Line ${finding.line}: ${finding.description}`);
                console.log(`   Content: ${finding.content.substring(0, 100)}...`);
                console.log('');
            });
            return false;
        }
    }

    async scanDirectory(dir) {
        const items = fs.readdirSync(dir);
        
        for (const item of items) {
            const fullPath = path.join(dir, item);
            const stat = fs.statSync(fullPath);
            
            if (stat.isDirectory()) {
                if (!this.excludeDirectories.includes(item)) {
                    await this.scanDirectory(fullPath);
                }
            } else if (stat.isFile()) {
                if (!this.excludeFiles.includes(item)) {
                    await this.scanFile(fullPath);
                }
            }
        }
    }

    async scanFile(filePath) {
        try {
            const content = fs.readFileSync(filePath, 'utf8');
            this.scannedFiles++;
            
            // Skip binary files
            if (this.isBinaryFile(content)) {
                return;
            }
            
            const lines = content.split('\n');
            
            lines.forEach((line, lineNumber) => {
                this.suspiciousPatterns.forEach(pattern => {
                    const matches = line.match(pattern);
                    if (matches) {
                        matches.forEach(match => {
                            if (!this.isAllowedPattern(match)) {
                                this.findings.push({
                                    file: filePath,
                                    line: lineNumber + 1,
                                    content: line.trim(),
                                    match: match,
                                    description: this.getPatternDescription(pattern),
                                    severity: this.getSeverity(pattern, match)
                                });
                            }
                        });
                    }
                });
            });
            
        } catch (error) {
            console.warn(`Warning: Could not read file ${filePath}: ${error.message}`);
        }
    }

    isBinaryFile(content) {
        // Simple binary file detection
        const nonTextChars = content.match(/[\x00-\x08\x0E-\x1F\x7F-\xFF]/g);
        return nonTextChars && nonTextChars.length > content.length * 0.1;
    }

    isAllowedPattern(match) {
        return this.allowedPatterns.some(allowed => 
            match.toLowerCase().includes(allowed.toLowerCase())
        );
    }

    getPatternDescription(pattern) {
        const descriptions = {
            '/AIza[0-9A-Za-z_-]{35}/g': 'Google API Key detected',
            '/api[_-]?key[_-]?[:=]\\s*[\'"][^\'"]+[\']/gi': 'API key assignment detected',
            '/secret[_-]?key[_-]?[:=]\\s*[\'"][^\'"]+[\']/gi': 'Secret key assignment detected',
            '/access[_-]?token[_-]?[:=]\\s*[\'"][^\'"]+[\']/gi': 'Access token assignment detected',
            '/process\\.env\\.[A-Z_]+[_-]?(KEY|SECRET|TOKEN|PASSWORD)/gi': 'Environment variable reference',
            '/password[_-]?[:=]\\s*[\'"][^\'"]+[\']/gi': 'Password assignment detected',
            '/token[_-]?[:=]\\s*[\'"][^\'"]+[\']/gi': 'Token assignment detected'
        };
        
        return descriptions[pattern.toString()] || 'Suspicious pattern detected';
    }

    getSeverity(pattern, match) {
        // Google API keys are critical
        if (pattern.toString().includes('AIza')) {
            return 'critical';
        }
        
        // Environment variables are usually medium risk
        if (pattern.toString().includes('process.env')) {
            return 'medium';
        }
        
        // Other patterns are high risk
        return 'high';
    }

    generateReport() {
        const report = {
            timestamp: new Date().toISOString(),
            filesScanned: this.scannedFiles,
            totalFindings: this.findings.length,
            criticalFindings: this.findings.filter(f => f.severity === 'critical').length,
            highFindings: this.findings.filter(f => f.severity === 'high').length,
            mediumFindings: this.findings.filter(f => f.severity === 'medium').length,
            findings: this.findings
        };
        
        fs.writeFileSync('security-audit-report.json', JSON.stringify(report, null, 2));
        console.log('📄 Detailed report saved to security-audit-report.json');
        
        return report;
    }
}

// Run audit if called directly
if (require.main === module) {
    const auditor = new SecurityAuditor();
    
    auditor.audit(process.argv[2] || '.')
        .then(isClean => {
            if (!isClean) {
                auditor.generateReport();
                process.exit(1);
            } else {
                console.log('\n🎉 Security audit passed! No sensitive data found.');
                process.exit(0);
            }
        })
        .catch(error => {
            console.error('❌ Audit failed:', error);
            process.exit(1);
        });
}

module.exports = SecurityAuditor;
