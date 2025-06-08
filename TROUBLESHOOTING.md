# 🔧 Solar AI Platform Troubleshooting Guide

## 🚨 **Server Not Running / Localhost Not Working**

### Quick Fix Steps:

#### 1. **Check Server Status**
```bash
python check_status.py
```

#### 2. **Restart the Server**
```bash
# Method 1: Use the launcher
python start_solar_ai.py

# Method 2: Direct command
streamlit run app_modern.py

# Method 3: Force specific port
streamlit run app_modern.py --server.port 8503
```

#### 3. **Check the Correct URL**
- **Correct URL**: http://localhost:8503
- **Alternative**: http://127.0.0.1:8503
- **Check terminal output** for the actual URL

#### 4. **Clear Browser Cache**
- Press `Ctrl + F5` (Windows) or `Cmd + Shift + R` (Mac)
- Try incognito/private browsing mode
- Try a different browser

---

## 🐛 **Common Issues and Solutions**

### Issue 1: "Port Already in Use"
```bash
# Kill existing processes
taskkill /f /im streamlit.exe  # Windows
pkill -f streamlit             # Mac/Linux

# Or use a different port
streamlit run app_modern.py --server.port 8504
```

### Issue 2: "Module Not Found" Errors
```bash
# Install missing dependencies
pip install streamlit opencv-python pillow numpy requests reportlab

# Or install from requirements
pip install -r requirements.txt
```

### Issue 3: "Permission Denied" Errors
```bash
# Run as administrator (Windows)
# Or check file permissions (Mac/Linux)
chmod +x start_solar_ai.py
```

### Issue 4: "3D Background Not Loading"
- **Check Browser**: Ensure WebGL support
- **Update Graphics Drivers**: For better performance
- **Fallback**: 2D version loads automatically

### Issue 5: "PDF Generation Fails"
```bash
# Install reportlab
pip install reportlab

# Check write permissions
mkdir reports  # Create reports directory
```

---

## 🌐 **Browser Compatibility**

### ✅ **Supported Browsers**
- **Chrome**: Full support (recommended)
- **Firefox**: Full support
- **Safari**: Full support (Mac)
- **Edge**: Full support (Windows)

### ❌ **Unsupported Browsers**
- Internet Explorer
- Very old browser versions

---

## 🔍 **Diagnostic Commands**

### Check Python Environment
```bash
python --version          # Should be 3.11+
pip list | grep streamlit  # Check Streamlit version
```

### Check Network
```bash
# Test if port is accessible
curl http://localhost:8503
netstat -an | grep 8503    # Check if port is listening
```

### Check Files
```bash
# Verify all files exist
ls -la app_modern.py
ls -la .streamlit/config.toml
ls -la static/js/neural_3d.js
```

---

## 🚀 **Performance Issues**

### Slow Loading
1. **Check Internet Connection**: NASA API requires internet
2. **Reduce 3D Quality**: Edit `.streamlit/config.toml`
3. **Close Other Applications**: Free up system resources

### High Memory Usage
1. **Restart Browser**: Clear memory leaks
2. **Disable 3D Background**: Set `ENABLE_3D_NEURAL=false` in `.env`
3. **Use Smaller Images**: Resize test images if needed

---

## 📱 **Mobile Issues**

### Touch Not Working
- **Enable Touch**: Ensure touch events are enabled
- **Zoom Issues**: Use pinch-to-zoom for better interaction
- **Orientation**: Rotate device for better layout

### Performance on Mobile
- **Reduce Quality**: 3D background automatically adapts
- **Close Apps**: Free up mobile device memory
- **Use WiFi**: Better connection for API calls

---

## 🔐 **Security Issues**

### API Key Problems
```bash
# Check environment variables
python -c "import os; print('Google API:', 'Set' if os.getenv('GOOGLE_API_KEY') else 'Not set')"

# Validate environment
python setup_environment.py --validate-only
```

### CORS Errors
- **Check Config**: Verify `.streamlit/config.toml` settings
- **Browser Security**: Try incognito mode
- **Firewall**: Check if firewall is blocking localhost

---

## 🛠️ **Advanced Troubleshooting**

### Debug Mode
```bash
# Enable debug logging
export DEBUG_MODE=true
streamlit run app_modern.py --logger.level debug
```

### Check Logs
```bash
# View Streamlit logs
tail -f ~/.streamlit/logs/streamlit.log

# Check application logs
python -c "import logging; logging.basicConfig(level=logging.DEBUG)"
```

### Reset Configuration
```bash
# Reset Streamlit config
rm -rf ~/.streamlit/
streamlit config show

# Reset application config
rm .env
cp .env.example .env
```

---

## 📞 **Getting Help**

### Before Asking for Help:
1. ✅ Run `python check_status.py`
2. ✅ Check this troubleshooting guide
3. ✅ Try restarting the server
4. ✅ Clear browser cache
5. ✅ Check browser console for errors

### Information to Include:
- **Operating System**: Windows/Mac/Linux version
- **Python Version**: `python --version`
- **Browser**: Chrome/Firefox/Safari/Edge version
- **Error Messages**: Copy exact error text
- **Steps to Reproduce**: What you were doing when it failed

### Quick Diagnostic Report:
```bash
# Run this and share the output
python check_status.py > diagnostic_report.txt
echo "Python Version: $(python --version)" >> diagnostic_report.txt
echo "Operating System: $(uname -a)" >> diagnostic_report.txt
```

---

## 🎯 **Quick Solutions Summary**

| Problem | Quick Fix |
|---------|-----------|
| Server won't start | `python start_solar_ai.py` |
| Wrong port | Check terminal output for actual URL |
| Page won't load | Clear browser cache, try incognito |
| 3D not working | Update graphics drivers, try different browser |
| PDF fails | `pip install reportlab` |
| Slow performance | Close other apps, check internet |
| API errors | Check `.env` file, validate API keys |

---

## ✅ **Success Indicators**

When everything is working correctly, you should see:
- ✅ Server running at http://localhost:8503
- ✅ Dark neural network background with animations
- ✅ Upload area accepts images
- ✅ Configuration inputs work
- ✅ Processing completes successfully
- ✅ Results display with metrics
- ✅ PDF generation works

---

**🌞 If you're still having issues, the platform includes fallback modes to ensure basic functionality works even with limited features!**
