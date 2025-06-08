#!/usr/bin/env python3
"""
Quick launcher for Solar AI Platform
"""

import subprocess
import sys
import webbrowser
import time
import os

def main():
    print("🌞 Starting Solar AI Platform...")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists('app_modern.py'):
        print("❌ Error: app_modern.py not found!")
        print("Please run this script from the SolarAiHelper directory")
        return
    
    print("🚀 Launching Streamlit server...")
    print("📱 The app will open in your browser automatically")
    print("🔗 URL: http://localhost:8503")
    print("\n⏳ Starting server (this may take a few seconds)...")

    process = None
    try:
        # Start the Streamlit server (config.toml will handle port settings)
        process = subprocess.Popen([
            sys.executable, '-m', 'streamlit', 'run', 'app_modern.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Wait a moment for server to start
        time.sleep(3)

        # Open browser
        print("🌐 Opening browser...")
        webbrowser.open('http://localhost:8503')

        print("\n✅ Solar AI Platform is running!")
        print("📋 Test images are available in the 'test_images' folder")
        print("📖 See TESTING_GUIDE.md for detailed instructions")
        print("\n🛑 Press Ctrl+C to stop the server")

        # Wait for the process
        process.wait()

    except KeyboardInterrupt:
        print("\n👋 Shutting down Solar AI Platform...")
        if process:
            process.terminate()
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        if process:
            process.terminate()

if __name__ == "__main__":
    main()
