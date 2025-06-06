import streamlit as st
import os
import tempfile
import time
import json
from PIL import Image
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Import backend modules
from backend.image_analysis import RoofAnalyzer
from backend.llm_integration import LLMGenerator
from backend.solar_calculations import SolarCalculator
from backend.nasa_api import NASADataProvider
from backend.report_generator import ReportGenerator
from utils.validators import ImageValidator
from utils.helpers import format_currency, format_number
from config.constants import PANEL_SPECS

# Configure page
st.set_page_config(
    page_title="🌞 AI Solar Analysis Platform",
    page_icon="🌞",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern design with neural network background
def load_custom_css():
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
        background: transparent;
        min-height: 100vh;
        position: relative;
        z-index: 1;
        color: #ffffff;
    }

    /* Dark theme base */
    .stApp {
        background: #000000;
        color: #ffffff;
    }

    /* Ensure content is above neural background */
    .main .block-container {
        position: relative;
        z-index: 10;
        background: transparent;
        color: #ffffff;
    }

    /* WCAG 2.1 AA Compliant Text Colors */
    .stApp, .stApp * {
        color: #ffffff !important;
    }

    /* Streamlit component overrides for visibility */
    .stSelectbox label, .stNumberInput label, .stFileUploader label {
        color: #ffffff !important;
        font-weight: 500 !important;
        font-size: 1rem !important;
    }

    .stSelectbox div[data-baseweb="select"] {
        background-color: rgba(0, 0, 0, 0.8) !important;
        border: 2px solid rgba(0, 255, 255, 0.3) !important;
        color: #ffffff !important;
    }

    .stNumberInput input {
        background-color: rgba(0, 0, 0, 0.8) !important;
        border: 2px solid rgba(0, 255, 255, 0.3) !important;
        color: #ffffff !important;
    }

    .stFileUploader section {
        background-color: rgba(0, 0, 0, 0.8) !important;
        border: 2px dashed rgba(0, 255, 255, 0.5) !important;
        color: #ffffff !important;
    }

    .stFileUploader section small {
        color: #e0e0e0 !important;
    }

    /* Progress and Status Messages */
    .stProgress .stProgress-bar {
        background-color: #00ffff !important;
    }

    .stProgress .stProgress-text {
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    /* Success and Error Messages */
    .stSuccess {
        background-color: rgba(0, 255, 0, 0.1) !important;
        border: 1px solid #00ff00 !important;
        color: #ffffff !important;
    }

    .stError {
        background-color: rgba(255, 107, 107, 0.1) !important;
        border: 1px solid #ff6b6b !important;
        color: #ffffff !important;
    }

    .stWarning {
        background-color: rgba(255, 255, 0, 0.1) !important;
        border: 1px solid #ffff00 !important;
        color: #ffffff !important;
    }

    .stInfo {
        background-color: rgba(0, 255, 255, 0.1) !important;
        border: 1px solid #00ffff !important;
        color: #ffffff !important;
    }

    /* Markdown text in cards */
    .analysis-card h1, .analysis-card h2, .analysis-card h3,
    .analysis-card h4, .analysis-card h5, .analysis-card h6 {
        color: #00ffff !important;
        text-shadow: 0 0 10px rgba(0, 255, 255, 0.3);
    }

    .analysis-card p, .analysis-card li, .analysis-card span {
        color: #ffffff !important;
        line-height: 1.6;
    }

    .analysis-card strong {
        color: #00ffff !important;
        font-weight: 700;
    }

    /* Step indicator text */
    .step-indicator {
        color: #ffffff !important;
    }
    
    /* Header Styles */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: rgba(0, 0, 0, 0.8);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        margin: 1rem 0 2rem 0;
        border: 2px solid rgba(0, 255, 255, 0.3);
        box-shadow:
            0 0 30px rgba(0, 255, 255, 0.2),
            inset 0 0 30px rgba(0, 255, 255, 0.1);
    }

    .main-title {
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(45deg, #00ffff, #00ff00, #ff00ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        text-shadow: 0 0 20px rgba(0, 255, 255, 0.5);
        animation: titleGlow 3s ease-in-out infinite alternate;
    }

    @keyframes titleGlow {
        0% { filter: brightness(1) drop-shadow(0 0 10px rgba(0, 255, 255, 0.5)); }
        100% { filter: brightness(1.2) drop-shadow(0 0 20px rgba(0, 255, 255, 0.8)); }
    }

    .main-subtitle {
        font-size: 1.2rem;
        color: rgba(255, 255, 255, 0.9);
        font-weight: 400;
        margin-bottom: 1rem;
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
    }
    
    /* Card Styles */
    .analysis-card {
        background: rgba(0, 0, 0, 0.85);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow:
            0 8px 32px rgba(0, 255, 255, 0.2),
            inset 0 0 20px rgba(0, 255, 255, 0.05);
        border: 2px solid rgba(0, 255, 255, 0.3);
        transition: all 0.3s ease;
        color: #ffffff;
    }

    .analysis-card:hover {
        transform: translateY(-5px);
        box-shadow:
            0 12px 40px rgba(0, 255, 255, 0.3),
            inset 0 0 30px rgba(0, 255, 255, 0.1);
        border-color: rgba(0, 255, 255, 0.5);
    }
    
    /* Button Styles */
    .stButton > button {
        background: linear-gradient(45deg, #00ffff, #00ff00);
        color: #000000;
        border: 2px solid rgba(0, 255, 255, 0.5);
        border-radius: 50px;
        padding: 0.75rem 2rem;
        font-weight: 700;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow:
            0 4px 15px rgba(0, 255, 255, 0.4),
            0 0 20px rgba(0, 255, 255, 0.2);
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow:
            0 6px 20px rgba(0, 255, 255, 0.6),
            0 0 30px rgba(0, 255, 255, 0.4);
        background: linear-gradient(45deg, #00ff00, #ff00ff);
        border-color: rgba(0, 255, 0, 0.7);
    }
    
    .process-button {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        color: white;
        border: none;
        border-radius: 50px;
        padding: 1rem 3rem;
        font-weight: 700;
        font-size: 1.2rem;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4);
        margin: 1rem auto;
        display: block;
    }
    
    .process-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(255, 107, 107, 0.6);
    }
    
    /* Progress Bar */
    .progress-container {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 50px;
        padding: 0.5rem;
        margin: 1rem 0;
    }
    
    .progress-bar {
        background: linear-gradient(45deg, #FFD700, #FFA500);
        height: 20px;
        border-radius: 50px;
        transition: width 0.5s ease;
        position: relative;
        overflow: hidden;
    }
    
    .progress-bar::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        bottom: 0;
        right: 0;
        background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.5) 50%, transparent 70%);
        animation: shimmer 2s infinite;
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    /* Upload Area */
    .upload-area {
        border: 3px dashed rgba(255, 255, 255, 0.5);
        border-radius: 20px;
        padding: 3rem;
        text-align: center;
        background: rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
        margin: 2rem 0;
    }
    
    .upload-area:hover {
        border-color: rgba(255, 255, 255, 0.8);
        background: rgba(255, 255, 255, 0.2);
    }
    
    /* Metrics Cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(0,0,0,0.9), rgba(0,20,20,0.8));
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        margin: 0.5rem;
        box-shadow:
            0 4px 15px rgba(0,255,255,0.3),
            inset 0 0 20px rgba(0,255,255,0.1);
        border: 2px solid rgba(0,255,255,0.3);
        transition: all 0.3s ease;
        color: #ffffff;
    }

    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow:
            0 6px 20px rgba(0,255,255,0.5),
            inset 0 0 30px rgba(0,255,255,0.2);
        border-color: rgba(0,255,255,0.6);
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #00ffff !important;
        margin-bottom: 0.5rem;
        text-shadow: 0 0 10px rgba(0,255,255,0.5);
        filter: brightness(1.2);
    }

    .metric-label {
        font-size: 1rem;
        color: #ffffff !important;
        font-weight: 600;
        text-shadow: 0 0 5px rgba(255,255,255,0.3);
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Sidebar styling */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    
    /* Step indicator */
    .step-indicator {
        display: flex;
        justify-content: center;
        margin: 2rem 0;
    }
    
    .step {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .step.active {
        background: linear-gradient(45deg, #FFD700, #FFA500);
        color: white;
        transform: scale(1.2);
    }
    
    .step.completed {
        background: linear-gradient(45deg, #4ECDC4, #44A08D);
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

    # Load and inject neural network CSS and JS
    load_neural_network_assets()

def load_neural_network_assets():
    """Load 3D neural network CSS and JavaScript assets"""
    try:
        # Load 3D Neural Network CSS
        css_path = "static/css/neural_background.css"
        if os.path.exists(css_path):
            with open(css_path, 'r') as f:
                css_content = f.read()
            st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

        # Load 3D Neural Network JavaScript
        js_3d_path = "static/js/neural_3d.js"
        if os.path.exists(js_3d_path):
            with open(js_3d_path, 'r') as f:
                js_3d_content = f.read()
            st.markdown(f"<script>{js_3d_content}</script>", unsafe_allow_html=True)

        # Load 2D fallback
        js_2d_path = "static/js/neural_network.js"
        if os.path.exists(js_2d_path):
            with open(js_2d_path, 'r') as f:
                js_2d_content = f.read()
            st.markdown(f"<script>{js_2d_content}</script>", unsafe_allow_html=True)

    except Exception as e:
        # Fallback: create basic neural background with CSS only
        st.markdown("""
        <style>
        .neural-background {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: radial-gradient(ellipse at center, #0a0a0a 0%, #000000 100%);
            z-index: -2;
        }
        </style>
        <div class="neural-background"></div>
        """, unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 1
    if 'uploaded_image' not in st.session_state:
        st.session_state.uploaded_image = None
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'location_data' not in st.session_state:
        st.session_state.location_data = {'latitude': 37.7749, 'longitude': -122.4194}

def render_header():
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">🌞 AI Solar Analysis Platform</h1>
        <p class="main-subtitle">Advanced AI-Powered Solar Rooftop Analysis with Real-time Processing</p>
    </div>
    """, unsafe_allow_html=True)

def render_step_indicator():
    steps = ["Upload", "Configure", "Process", "Results"]
    current = st.session_state.current_step
    
    step_html = '<div class="step-indicator">'
    for i, step in enumerate(steps, 1):
        if i < current:
            step_class = "step completed"
        elif i == current:
            step_class = "step active"
        else:
            step_class = "step"
        step_html += f'<div class="{step_class}">{i}</div>'
    step_html += '</div>'
    
    st.markdown(step_html, unsafe_allow_html=True)

def render_upload_step():
    st.markdown('<div class="analysis-card">', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("### 📸 Upload Satellite Image")
        st.markdown("Upload a high-resolution satellite image of your rooftop for AI analysis")

        uploaded_file = st.file_uploader(
            "Choose an image file",
            type=['png', 'jpg', 'jpeg'],
            help="Upload a clear satellite image of your rooftop (PNG, JPG, JPEG)"
        )

        if uploaded_file is not None:
            # Validate image
            validator = ImageValidator()
            is_valid, message = validator.validate_image(uploaded_file)

            if is_valid:
                st.session_state.uploaded_image = uploaded_file

                # Display image preview
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Image Preview", use_column_width=True)

                st.success("✅ Image uploaded successfully!")

                # Next button
                if st.button("🚀 Continue to Configuration", key="next_to_config"):
                    st.session_state.current_step = 2
                    st.rerun()
            else:
                st.error(f"❌ {message}")

    st.markdown('</div>', unsafe_allow_html=True)

def render_configure_step():
    st.markdown('<div class="analysis-card">', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🌍 Location Settings")

        latitude = st.number_input(
            "Latitude",
            value=st.session_state.location_data['latitude'],
            min_value=-90.0,
            max_value=90.0,
            step=0.0001,
            format="%.4f"
        )

        longitude = st.number_input(
            "Longitude",
            value=st.session_state.location_data['longitude'],
            min_value=-180.0,
            max_value=180.0,
            step=0.0001,
            format="%.4f"
        )

        st.session_state.location_data = {'latitude': latitude, 'longitude': longitude}

    with col2:
        st.markdown("### ⚡ System Configuration")

        electricity_rate = st.number_input(
            "Electricity Rate ($/kWh)",
            value=0.12,
            min_value=0.01,
            max_value=1.0,
            step=0.01,
            format="%.3f"
        )

        installation_cost = st.number_input(
            "Installation Cost per Watt ($)",
            value=3.0,
            min_value=1.0,
            max_value=10.0,
            step=0.1,
            format="%.2f"
        )

        panel_type = st.selectbox(
            "Panel Type",
            options=list(PANEL_SPECS.keys()),
            index=0
        )

    # Navigation buttons
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("⬅️ Back to Upload", key="back_to_upload"):
            st.session_state.current_step = 1
            st.rerun()

    with col3:
        if st.button("🔄 Start Analysis", key="start_analysis"):
            st.session_state.current_step = 3
            st.session_state.processing = True
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

def render_process_step():
    st.markdown('<div class="analysis-card">', unsafe_allow_html=True)

    st.markdown("### 🤖 AI Processing in Progress")

    if st.session_state.processing:
        # Create progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Simulate processing steps
        steps = [
            ("🔍 Analyzing image structure...", 20),
            ("🏠 Detecting roof boundaries...", 40),
            ("📐 Calculating roof dimensions...", 60),
            ("☀️ Fetching solar data...", 80),
            ("🤖 Generating AI recommendations...", 100)
        ]

        for step_text, progress in steps:
            status_text.text(step_text)
            progress_bar.progress(progress)
            time.sleep(1)  # Simulate processing time

        # Perform actual analysis
        try:
            results = perform_analysis()
            st.session_state.analysis_results = results
            st.session_state.processing = False
            st.session_state.current_step = 4
            st.success("✅ Analysis completed successfully!")
            time.sleep(1)
            st.rerun()

        except Exception as e:
            st.error(f"❌ Analysis failed: {str(e)}")
            st.session_state.processing = False

            if st.button("🔄 Retry Analysis", key="retry_analysis"):
                st.session_state.processing = True
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

def perform_analysis():
    """Perform the actual AI analysis"""
    if st.session_state.uploaded_image is None:
        raise ValueError("No image uploaded")

    # Save uploaded image temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
        tmp_file.write(st.session_state.uploaded_image.getvalue())
        temp_image_path = tmp_file.name

    try:
        # Initialize analyzers
        roof_analyzer = RoofAnalyzer()
        solar_calculator = SolarCalculator()
        nasa_provider = NASADataProvider()
        llm_generator = LLMGenerator()

        # Perform roof analysis
        roof_analysis = roof_analyzer.analyze_roof(temp_image_path)

        # Get solar data
        location = st.session_state.location_data
        solar_data = nasa_provider.get_solar_data(
            location['latitude'],
            location['longitude']
        )

        # Calculate solar potential
        solar_results = solar_calculator.calculate_potential(
            roof_analysis,
            solar_data,
            panel_type='monocrystalline',
            electricity_rate=0.12,
            installation_cost_per_watt=3.0
        )

        # Generate AI recommendations
        ai_recommendations = llm_generator.generate_recommendations(
            roof_analysis,
            solar_results,
            location['latitude'],
            location['longitude']
        )

        return {
            'roof_analysis': roof_analysis,
            'solar_data': solar_data,
            'solar_results': solar_results,
            'ai_recommendations': ai_recommendations
        }

    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_image_path)
        except:
            pass

def render_results_step():
    if st.session_state.analysis_results is None:
        st.error("No analysis results available")
        return

    results = st.session_state.analysis_results

    # Display results in cards
    render_metrics_cards(results)
    render_detailed_analysis(results)
    render_ai_recommendations(results)

    # Navigation and actions
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("⬅️ Back to Configuration", key="back_to_config"):
            st.session_state.current_step = 2
            st.rerun()

    with col2:
        if st.button("🔄 New Analysis", key="new_analysis"):
            st.session_state.current_step = 1
            st.session_state.uploaded_image = None
            st.session_state.analysis_results = None
            st.rerun()

    with col3:
        if st.button("📄 Generate Report", key="generate_report"):
            generate_pdf_report(results)

def render_metrics_cards(results):
    st.markdown("### 📊 Key Metrics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        area = results['roof_analysis'].get('usable_area', 0) * 10.764  # Convert m² to sq ft
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{area:.0f}</div>
            <div class="metric-label">Roof Area (sq ft)</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{results['solar_results']['system_size_kw']:.1f}</div>
            <div class="metric-label">System Size (kW)</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{results['solar_results']['annual_energy_kwh']:.0f}</div>
            <div class="metric-label">Annual Production (kWh)</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{results['solar_results']['payback_years']:.1f}</div>
            <div class="metric-label">Payback Period (years)</div>
        </div>
        """, unsafe_allow_html=True)

def render_detailed_analysis(results):
    st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
    st.markdown("### 🔍 Detailed Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🏠 Roof Characteristics")
        area_sqft = results['roof_analysis'].get('usable_area', 0) * 10.764
        st.markdown(f"""
        <div style="color: #ffffff; line-height: 1.8; font-size: 1.1rem;">
            <p><strong style="color: #00ffff;">Area:</strong> <span style="color: #ffffff;">{area_sqft:.0f} sq ft</span></p>
            <p><strong style="color: #00ffff;">Orientation:</strong> <span style="color: #ffffff;">{results['roof_analysis'].get('orientation', 'Unknown')}</span></p>
            <p><strong style="color: #00ffff;">Slope:</strong> <span style="color: #ffffff;">{results['roof_analysis'].get('slope', 0):.1f}°</span></p>
            <p><strong style="color: #00ffff;">Shading:</strong> <span style="color: #ffffff;">{results['roof_analysis'].get('shading_factor', 0):.1%}</span></p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("#### 💰 Financial Analysis")
        st.markdown(f"""
        <div style="color: #ffffff; line-height: 1.8; font-size: 1.1rem;">
            <p><strong style="color: #00ffff;">System Cost:</strong> <span style="color: #ffffff;">${results['solar_results'].get('total_cost', 0):,.0f}</span></p>
            <p><strong style="color: #00ffff;">Annual Savings:</strong> <span style="color: #ffffff;">${results['solar_results'].get('annual_savings', 0):,.0f}</span></p>
            <p><strong style="color: #00ffff;">25-Year Savings:</strong> <span style="color: #ffffff;">${results['solar_results'].get('lifetime_savings', 0):,.0f}</span></p>
            <p><strong style="color: #00ffff;">ROI:</strong> <span style="color: #ffffff;">{results['solar_results'].get('roi_percent', 0):.1f}%</span></p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

def render_ai_recommendations(results):
    st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
    st.markdown("### 🤖 AI Recommendations")

    recommendations = results['ai_recommendations']

    if isinstance(recommendations, dict):
        # Display structured recommendations
        if 'installation_plan' in recommendations:
            st.markdown("#### 🔧 Installation Plan")
            st.markdown(recommendations['installation_plan'])

        if 'optimization_tips' in recommendations:
            st.markdown("#### ⚡ Optimization Tips")
            st.markdown(recommendations['optimization_tips'])

        if 'compliance_info' in recommendations:
            st.markdown("#### 📋 Compliance Information")
            st.markdown(recommendations['compliance_info'])

        if 'maintenance_plan' in recommendations:
            st.markdown("#### 🔧 Maintenance Plan")
            st.markdown(recommendations['maintenance_plan'])
    else:
        # Display as plain text
        st.markdown(str(recommendations))

    st.markdown('</div>', unsafe_allow_html=True)

def generate_pdf_report(results):
    """Generate and download PDF report"""
    try:
        # Create a simple PDF report with current data structure
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import inch
        import io

        # Create buffer
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Title
        story.append(Paragraph("🌞 Solar Analysis Report", styles['Title']))
        story.append(Spacer(1, 0.5*inch))

        # Report date
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))

        # Roof Analysis
        roof_analysis = results.get('roof_analysis', {})
        area_sqft = roof_analysis.get('usable_area', 0) * 10.764

        story.append(Paragraph("Roof Characteristics", styles['Heading1']))
        story.append(Paragraph(f"• Usable Area: {area_sqft:.0f} sq ft", styles['Normal']))
        story.append(Paragraph(f"• Orientation: {roof_analysis.get('orientation', 'Unknown')}", styles['Normal']))
        story.append(Paragraph(f"• Slope: {roof_analysis.get('slope', 0):.1f}°", styles['Normal']))
        story.append(Paragraph(f"• Shading Factor: {roof_analysis.get('shading_factor', 0):.1%}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))

        # Solar Results
        solar_results = results.get('solar_results', {})

        story.append(Paragraph("Solar System Analysis", styles['Heading1']))
        story.append(Paragraph(f"• System Size: {solar_results.get('system_size_kw', 0):.1f} kW", styles['Normal']))
        story.append(Paragraph(f"• Annual Production: {solar_results.get('annual_energy_kwh', 0):,.0f} kWh", styles['Normal']))
        story.append(Paragraph(f"• Annual Savings: ${solar_results.get('annual_savings', 0):,.0f}", styles['Normal']))
        story.append(Paragraph(f"• Payback Period: {solar_results.get('payback_years', 0):.1f} years", styles['Normal']))
        story.append(Paragraph(f"• Total System Cost: ${solar_results.get('total_cost', 0):,.0f}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))

        # AI Recommendations
        ai_recommendations = results.get('ai_recommendations', 'No recommendations available')
        story.append(Paragraph("AI Recommendations", styles['Heading1']))

        if isinstance(ai_recommendations, dict):
            for key, value in ai_recommendations.items():
                story.append(Paragraph(f"• {key.replace('_', ' ').title()}: {value}", styles['Normal']))
        else:
            story.append(Paragraph(str(ai_recommendations), styles['Normal']))

        story.append(Spacer(1, 0.3*inch))

        # Disclaimer
        story.append(Paragraph("Disclaimer", styles['Heading2']))
        story.append(Paragraph(
            "This analysis is based on satellite imagery and modeled data. "
            "Actual results may vary based on site-specific conditions, local regulations, "
            "utility policies, and installation quality. A professional site assessment "
            "is recommended before proceeding with installation.",
            styles['Normal']
        ))

        # Build PDF
        doc.build(story)
        buffer.seek(0)

        st.download_button(
            label="📄 Download PDF Report",
            data=buffer,
            file_name=f"solar_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf"
        )

        st.success("✅ Report generated successfully!")

    except Exception as e:
        st.error(f"❌ Failed to generate report: {str(e)}")
        st.error("Please try again or contact support if the problem persists.")

def main():
    # Load custom CSS
    load_custom_css()

    # Initialize session state
    initialize_session_state()

    # Render header
    render_header()

    # Render step indicator
    render_step_indicator()

    # Main content based on current step
    if st.session_state.current_step == 1:
        render_upload_step()
    elif st.session_state.current_step == 2:
        render_configure_step()
    elif st.session_state.current_step == 3:
        render_process_step()
    elif st.session_state.current_step == 4:
        render_results_step()

if __name__ == "__main__":
    main()
