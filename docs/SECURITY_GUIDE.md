# 🔐 Security Guide - Solar AI Platform

## 🛡️ **Security Architecture Overview**

The Solar AI Platform implements a **client-side security model** where sensitive information never touches the server or repository. This guide explains our security practices and how to maintain them.

---

## 🔑 **API Key Security**

### **Current Implementation (Secure by Design)**

#### ✅ **No Hard-coded Keys**
```javascript
// ❌ NEVER do this (hard-coded key)
const API_KEY = "MY API key ";

// ✅ Our implementation (user-provided)
class AIIntegration {
    constructor() {
        this.apiKey = null; // No default key
        this.loadApiKey(); // Load from localStorage only
    }
    
    setApiKey(apiKey) {
        // Store in browser localStorage only
        localStorage.setItem('solar_ai_google_key', apiKey);
    }
}
```

#### ✅ **Client-Side Storage Only**
- **Browser localStorage**: Keys stored locally, never transmitted to our servers
- **No server component**: Static deployment means no server to compromise
- **User control**: Users manage their own keys, can clear anytime

#### ✅ **Secure Transmission**
```javascript
// Direct HTTPS calls to Google API
const response = await fetch('https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=' + this.apiKey, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    // Key sent directly to Google, never to our servers
});
```

---

## 🚫 **What NOT to Do**

### **❌ Never Commit These Files**
```bash
# These files should NEVER be in your repository
.env
.env.local
.env.production
config/api_keys.js
secrets.json
credentials.json
any_file_with_api_keys.txt
```

### **❌ Never Hard-code Keys**
```javascript
// ❌ NEVER do this
const GOOGLE_API_KEY = "AIzaSyC4K8B9X2M5N7P1Q3R6S8T0U2V4W6X8Y0Z";
const NASA_API_KEY = "your_nasa_key_here";

// ❌ NEVER do this in HTML
<script>
    const API_KEY = "AIzaSyC4K8B9X2M5N7P1Q3R6S8T0U2V4W6X8Y0Z";
</script>
```

### **❌ Never Log Sensitive Data**
```javascript
// ❌ NEVER do this
console.log('API Key:', apiKey);
console.error('Failed with key:', apiKey);

// ✅ Do this instead
console.log('API Key:', apiKey ? 'Set' : 'Not set');
console.error('API call failed');
```

---

## ✅ **Security Best Practices**

### **1. Repository Security**

#### **Enhanced .gitignore**
Our `.gitignore` includes comprehensive patterns:
```gitignore
# Environment variables (SECURITY CRITICAL)
.env
.env.local
.env.development
.env.test
.env.production

# API Keys and Secrets (CRITICAL SECURITY)
*api_key*
*secret*
*token*
*password*
*credentials*
config/secrets.py
config/keys.py
config/api_keys.js
secrets.json
credentials.json

# Backup files that might contain secrets
*.backup
*.bak
*.orig
```

#### **Pre-commit Hooks (Recommended)**
```bash
# Install git-secrets to prevent accidental commits
git clone https://github.com/awslabs/git-secrets.git
cd git-secrets
make install

# Configure for your repo
git secrets --register-aws
git secrets --install
git secrets --scan
```

### **2. Development Environment**

#### **Local Development Setup**
```bash
# Create local environment file (NOT committed)
echo "GOOGLE_API_KEY=your_key_here" > .env.local

# Add to .gitignore if not already there
echo ".env.local" >> .gitignore
```

#### **Environment Variable Loading**
```javascript
// For local development (if using Node.js build process)
if (process.env.NODE_ENV === 'development') {
    require('dotenv').config({ path: '.env.local' });
}

// Never expose in production build
const apiKey = process.env.NODE_ENV === 'development' 
    ? process.env.GOOGLE_API_KEY 
    : null; // User must provide in production
```

### **3. GitHub Actions Security**

#### **Using GitHub Secrets**
```yaml
# .github/workflows/deploy.yml
name: Deploy to GitHub Pages
on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          
      - name: Build (without embedding secrets)
        run: |
          npm install
          npm run build
        env:
          # These are NOT embedded in the build
          GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
          
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs
```

#### **Setting GitHub Secrets**
1. Go to repository **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add secrets:
   - `GOOGLE_API_KEY`: Your Google Gemini API key
   - Any other sensitive configuration

### **4. Production Deployment**

#### **Static Site Security**
```javascript
// Production configuration (no secrets embedded)
const config = {
    // Public configuration only
    nasaApiBase: 'https://power.larc.nasa.gov/api',
    corsProxy: 'https://api.allorigins.win/get?url=',
    
    // No API keys - users provide their own
    requiresUserApiKey: true,
    
    // Security headers
    csp: "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com"
};
```

#### **Content Security Policy**
```html
<!-- Add to index.html head -->
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; 
               script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://docs.opencv.org;
               connect-src 'self' https://generativelanguage.googleapis.com https://power.larc.nasa.gov;
               style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;">
```

---

## 🔍 **Security Auditing**

### **Regular Security Checks**

#### **1. Repository Scan**
```bash
# Scan for accidentally committed secrets
git log --all --full-history -- "*.env*"
git log --all --full-history -S "api_key" --source --all
git log --all --full-history -S "secret" --source --all

# Use automated tools
npm install -g detect-secrets
detect-secrets scan --all-files
```

#### **2. Code Review Checklist**
- [ ] No hard-coded API keys or secrets
- [ ] No sensitive data in console.log statements
- [ ] Environment files in .gitignore
- [ ] No credentials in configuration files
- [ ] Secure API call implementations

#### **3. Dependency Security**
```bash
# Check for vulnerable dependencies
npm audit
npm audit fix

# Use security-focused linting
npm install -g eslint-plugin-security
```

### **Incident Response**

#### **If API Key is Accidentally Committed**

1. **Immediate Actions**:
   ```bash
   # Remove from current code
   git rm config/api_keys.js
   git commit -m "Remove accidentally committed API keys"
   
   # Rotate the compromised key immediately
   # Generate new key from API provider
   ```

2. **Clean Git History**:
   ```bash
   # Use BFG Repo-Cleaner (recommended)
   java -jar bfg.jar --delete-files api_keys.js
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive
   
   # Force push (WARNING: destructive)
   git push --force-with-lease origin main
   ```

3. **Verify Cleanup**:
   ```bash
   # Scan entire history
   git log --all --full-history -S "your_old_api_key"
   ```

---

## 🛡️ **Advanced Security Measures**

### **1. API Key Rotation**
```javascript
// Implement automatic key validation
class APIKeyManager {
    async validateKey(apiKey) {
        try {
            const testResponse = await fetch(`https://generativelanguage.googleapis.com/v1beta/models?key=${apiKey}`);
            return testResponse.ok;
        } catch (error) {
            return false;
        }
    }
    
    async rotateKey(oldKey, newKey) {
        if (await this.validateKey(newKey)) {
            localStorage.setItem('solar_ai_google_key', newKey);
            localStorage.removeItem('solar_ai_google_key_old');
            return true;
        }
        return false;
    }
}
```

### **2. Rate Limiting Protection**
```javascript
// Implement client-side rate limiting
class RateLimiter {
    constructor(maxRequests = 10, windowMs = 60000) {
        this.requests = [];
        this.maxRequests = maxRequests;
        this.windowMs = windowMs;
    }
    
    canMakeRequest() {
        const now = Date.now();
        this.requests = this.requests.filter(time => now - time < this.windowMs);
        return this.requests.length < this.maxRequests;
    }
    
    recordRequest() {
        this.requests.push(Date.now());
    }
}
```

### **3. Secure Configuration**
```javascript
// Environment-aware configuration
const getConfig = () => {
    const isDevelopment = window.location.hostname === 'localhost';
    const isProduction = window.location.hostname.includes('github.io');
    
    return {
        development: {
            debug: true,
            apiTimeout: 30000,
            // No API keys - loaded from localStorage
        },
        production: {
            debug: false,
            apiTimeout: 10000,
            // No API keys - user provided only
        }
    }[isDevelopment ? 'development' : 'production'];
};
```

---

## 📋 **Security Checklist**

### **Before Deployment**
- [ ] No API keys in any committed files
- [ ] .gitignore includes all sensitive file patterns
- [ ] Environment variables properly configured
- [ ] GitHub secrets set up for CI/CD
- [ ] Content Security Policy implemented
- [ ] Dependencies scanned for vulnerabilities

### **Regular Maintenance**
- [ ] Rotate API keys quarterly
- [ ] Review access logs for unusual activity
- [ ] Update dependencies regularly
- [ ] Scan repository for accidentally committed secrets
- [ ] Review and update security policies

### **User Education**
- [ ] Clear instructions for API key setup
- [ ] Warnings about key security in documentation
- [ ] Guidance on recognizing phishing attempts
- [ ] Instructions for reporting security issues

---

## 🚨 **Reporting Security Issues**

If you discover a security vulnerability:

1. **DO NOT** create a public GitHub issue
2. **DO NOT** discuss in public forums
3. **DO** email security concerns privately
4. **DO** provide detailed reproduction steps
5. **DO** allow reasonable time for response

---

**🔐 Security is everyone's responsibility. Follow these practices to keep the Solar AI Platform secure for all users.**
