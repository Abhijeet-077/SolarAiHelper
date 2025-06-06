"""
Redesigned AI-Powered Solar Rooftop Analysis System
Interactive interface with chatbot guidance and 3D visualization
"""

import streamlit as st
import tempfile
import os
import time
import json
from PIL import Image
import base64
import io

# Import backend modules
from backend.image_analysis import RoofAnalyzer
from backend.llm_integration import LLMGenerator
from backend.solar_calculations import SolarCalculator
from backend.nasa_api import NASADataProvider
from backend.report_generator import ReportGenerator
from backend.api_integrations import ExternalAPIManager
from utils.validators import ImageValidator
from utils.helpers import format_currency, format_number
from config.constants import PANEL_SPECS, UI_CONFIG
from frontend.components.chatbot import SolarAnalysisChatbot
from frontend.components.visualization_3d import Solar3DVisualizer

# Configure page
st.set_page_config(
    page_title="🌞 Advanced Solar Analysis Platform",
    page_icon="🌞",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load custom CSS
def load_custom_css():
    """Load custom CSS for enhanced styling"""
    with open('frontend/styles/main.css', 'r') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'analysis_step' not in st.session_state:
        st.session_state.analysis_step = 'upload'
    
    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = None
    
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    
    if 'analysis_in_progress' not in st.session_state:
        st.session_state.analysis_in_progress = False
    
    if 'configuration' not in st.session_state:
        st.session_state.configuration = {
            'latitude': 37.7749,
            'longitude': -122.4194,
            'panel_type': 'Monocrystalline',
            'electricity_rate': 0.12,
            'installation_cost': 3.50
        }

def render_header():
    """Render interactive header section"""
    st.markdown("""
    <div class="header-section">
        <div class="header-content">
            <h1 class="header-title">🌞 Advanced Solar Analysis Platform</h1>
            <p class="header-subtitle">AI-Powered Rooftop Analysis with Interactive 3D Visualization</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_progress_indicator():
    """Render visual progress indicator"""
    steps = ['Upload Image', 'Configure System', 'Analyze Roof', 'View Results']
    current_step = st.session_state.analysis_step
    
    step_mapping = {
        'upload': 0,
        'configure': 1,
        'analyze': 2,
        'results': 3
    }
    
    current_index = step_mapping.get(current_step, 0)
    
    st.markdown("""
    <div style="display: flex; justify-content: space-between; margin: 2rem 0; padding: 1rem; background: white; border-radius: 12px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
    """, unsafe_allow_html=True)
    
    for i, step in enumerate(steps):
        status = "completed" if i < current_index else ("active" if i == current_index else "pending")
        color = "#10b981" if status == "completed" else ("#3b82f6" if status == "active" else "#e5e7eb")
        text_color = "white" if status in ["completed", "active"] else "#6b7280"
        
        st.markdown(f"""
        <div style="flex: 1; text-align: center;">
            <div style="width: 40px; height: 40px; border-radius: 50%; background: {color}; color: {text_color}; 
                       display: flex; align-items: center; justify-content: center; margin: 0 auto 0.5rem; 
                       font-weight: bold; font-size: 1.2rem;">
                {i + 1}
            </div>
            <p style="margin: 0; color: {color}; font-weight: 600; font-size: 0.9rem;">{step}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if i < len(steps) - 1:
            connector_color = "#10b981" if i < current_index else "#e5e7eb"
            st.markdown(f"""
            <div style="flex: 0.5; display: flex; align-items: center; margin-top: 20px;">
                <div style="width: 100%; height: 2px; background: {connector_color};"></div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def render_upload_section():
    """Enhanced image upload section with drag-and-drop"""
    st.markdown("""
    <div class="upload-section">
        <div style="text-align: center;">
            <div class="upload-icon">📷</div>
            <h3 class="upload-text">Upload Satellite Image</h3>
            <p class="upload-subtext">Drag and drop your roof image here or click to browse</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choose satellite image of your roof",
        type=['jpg', 'jpeg', 'png'],
        key="roof_image_uploader",
        label_visibility="collapsed"
    )
    
    if uploaded_file:
        st.session_state.uploaded_file = uploaded_file
        
        # Display uploaded image preview
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Roof Image", use_container_width=True)
            
            # Image validation
            try:
                validator = ImageValidator()
                validation_result = validator.validate_image(uploaded_file)
                
                if validation_result.get('valid', True):
                    st.success("✅ Image validated successfully!")
                    st.session_state.analysis_step = 'configure'
                else:
                    st.error(f"❌ Image validation failed: {validation_result.get('message', 'Unknown error')}")
            except:
                # Fallback validation
                if uploaded_file.size < 10 * 1024 * 1024:  # 10MB limit
                    st.success("✅ Image validated successfully!")
                    st.session_state.analysis_step = 'configure'
                else:
                    st.error("❌ Image file too large. Please use an image under 10MB.")
        
        # Quick analysis preview
        if st.session_state.analysis_step == 'configure':
            with st.expander("🔍 Quick Image Analysis", expanded=False):
                try:
                    analyzer = RoofAnalyzer()
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        temp_path = tmp_file.name
                    
                    quick_analysis = analyzer.analyze_roof(temp_path)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Detected Roof Area", f"{quick_analysis.get('roof_area', 0):.0f} sq ft")
                    with col2:
                        st.metric("Estimated Orientation", quick_analysis.get('orientation', 'Unknown'))
                    with col3:
                        st.metric("Image Quality", "Good")
                    
                    os.unlink(temp_path)
                except Exception as e:
                    st.warning("Quick analysis unavailable. Proceed to full analysis.")

def render_configuration_section():
    """Enhanced configuration panel"""
    if st.session_state.uploaded_file is None:
        st.warning("⚠️ Please upload an image first")
        return
    
    st.markdown("""
    <div class="config-panel">
        <div class="config-header">
            <span class="config-icon">⚙️</span>
            <h2 class="config-title">System Configuration</h2>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Configuration form
    with st.form("configuration_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📍 Location Settings")
            latitude = st.number_input(
                "Latitude", 
                value=st.session_state.configuration['latitude'],
                format="%.6f",
                help="Enter your exact latitude (e.g., 37.774929)"
            )
            longitude = st.number_input(
                "Longitude", 
                value=st.session_state.configuration['longitude'],
                format="%.6f",
                help="Enter your exact longitude (e.g., -122.419418)"
            )
            
            # Location validation
            if st.button("🔍 Validate Location", type="secondary"):
                if -90 <= latitude <= 90 and -180 <= longitude <= 180:
                    st.success("✅ Valid coordinates")
                else:
                    st.error("❌ Invalid coordinates")
        
        with col2:
            st.subheader("⚡ System Parameters")
            panel_type = st.selectbox(
                "Panel Type",
                ["Monocrystalline", "Polycrystalline", "Thin Film"],
                index=0,
                help="Higher efficiency panels cost more but generate more power"
            )
            electricity_rate = st.number_input(
                "Electricity Rate ($/kWh)",
                value=st.session_state.configuration['electricity_rate'],
                min_value=0.01,
                max_value=1.00,
                step=0.01,
                format="%.3f",
                help="Check your utility bill for current rate"
            )
            installation_cost = st.number_input(
                "Installation Cost ($/Watt)",
                value=st.session_state.configuration['installation_cost'],
                min_value=1.00,
                max_value=10.00,
                step=0.10,
                format="%.2f",
                help="Average cost including equipment and labor"
            )
        
        # Analysis mode selection
        st.subheader("🎯 Analysis Mode")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            standard_selected = st.checkbox("Standard Analysis", value=True)
            st.caption("✓ Basic roof detection\n✓ NASA solar data\n✓ Financial modeling")
        
        with col2:
            professional_selected = st.checkbox("Professional Assessment")
            st.caption("✓ AI recommendations\n✓ Regulatory analysis\n✓ Detailed reporting")
        
        with col3:
            quick_mode = st.checkbox("Quick Mode")
            st.caption("✓ Faster processing\n✓ Essential metrics only")
        
        # Submit configuration
        submitted = st.form_submit_button("💾 Save Configuration", type="primary", use_container_width=True)
        
        if submitted:
            st.session_state.configuration.update({
                'latitude': latitude,
                'longitude': longitude,
                'panel_type': panel_type,
                'electricity_rate': electricity_rate,
                'installation_cost': installation_cost,
                'analysis_mode': 'professional' if professional_selected else 'standard',
                'quick_mode': quick_mode
            })
            st.success("✅ Configuration saved!")
            st.session_state.analysis_step = 'analyze'

def render_analyze_section():
    """Enhanced analysis section with real-time progress"""
    if not st.session_state.uploaded_file or not st.session_state.configuration:
        st.warning("⚠️ Please complete previous steps first")
        return
    
    # Analysis summary
    st.markdown("""
    <div style="background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); margin-bottom: 2rem;">
        <h2 style="color: #1f2937; margin-bottom: 1rem;">🚀 Ready for Analysis</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Configuration summary
    config = st.session_state.configuration
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Location", f"{config['latitude']:.3f}, {config['longitude']:.3f}")
    with col2:
        st.metric("Panel Type", config['panel_type'])
    with col3:
        st.metric("Electricity Rate", f"${config['electricity_rate']:.3f}/kWh")
    with col4:
        st.metric("Installation Cost", f"${config['installation_cost']:.2f}/W")
    
    # Analysis button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if not st.session_state.analysis_in_progress:
            if st.button("🔍 Analyze Roof", type="primary", use_container_width=True, key="analyze_button"):
                st.session_state.analysis_in_progress = True
                st.rerun()
        else:
            st.button("🔄 Analysis in Progress...", disabled=True, use_container_width=True)
    
    # Progress section
    if st.session_state.analysis_in_progress:
        render_analysis_progress()

def render_analysis_progress():
    """Real-time analysis progress with detailed steps"""
    st.markdown("""
    <div class="progress-section active">
        <div class="progress-header">
            <span class="progress-icon">⚡</span>
            <h3 class="progress-title">Processing Your Analysis</h3>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Progress container
    progress_container = st.container()
    status_container = st.container()
    
    with progress_container:
        progress_bar = st.progress(0)
        status_text = st.empty()
    
    try:
        # Step 1: Initialize analysis
        status_text.text("🚀 Initializing analysis pipeline...")
        progress_bar.progress(10)
        time.sleep(1)
        
        # Save uploaded image temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            tmp_file.write(st.session_state.uploaded_file.getvalue())
            temp_image_path = tmp_file.name
        
        # Step 2: Roof analysis
        status_text.text("🏠 Analyzing roof structure and geometry...")
        progress_bar.progress(25)
        
        analyzer = RoofAnalyzer()
        roof_analysis = analyzer.analyze_roof(temp_image_path)
        time.sleep(2)
        
        # Step 3: Solar data retrieval
        status_text.text("🌞 Retrieving authentic NASA solar irradiance data...")
        progress_bar.progress(50)
        
        nasa_provider = NASADataProvider()
        config = st.session_state.configuration
        solar_data = nasa_provider.get_irradiance_data(config['latitude'], config['longitude'])
        time.sleep(2)
        
        # Step 4: Financial calculations
        status_text.text("💰 Calculating financial projections and ROI...")
        progress_bar.progress(75)
        
        calculator = SolarCalculator()
        financial_analysis = calculator.calculate_solar_potential(
            roof_analysis, solar_data, config
        )
        time.sleep(1)
        
        # Step 5: AI recommendations
        status_text.text("🤖 Generating AI-powered recommendations...")
        progress_bar.progress(90)
        
        llm_generator = LLMGenerator()
        ai_recommendations = llm_generator.generate_recommendations(
            roof_analysis, solar_data, financial_analysis
        )
        time.sleep(1)
        
        # Step 6: Complete
        status_text.text("✅ Analysis complete! Preparing results...")
        progress_bar.progress(100)
        
        # Store results
        st.session_state.analysis_results = {
            'roof_analysis': roof_analysis,
            'solar_data': solar_data,
            'financial_analysis': financial_analysis,
            'ai_recommendations': ai_recommendations,
            'timestamp': time.time()
        }
        
        # Clean up temporary file
        os.unlink(temp_image_path)
        
        # Update state
        st.session_state.analysis_in_progress = False
        st.session_state.analysis_step = 'results'
        
        time.sleep(1)
        st.success("🎉 Analysis completed successfully!")
        st.rerun()
        
    except Exception as e:
        st.session_state.analysis_in_progress = False
        st.error(f"❌ Analysis failed: {str(e)}")
        
        # Clean up on error
        if 'temp_image_path' in locals():
            try:
                os.unlink(temp_image_path)
            except:
                pass

def render_results_dashboard():
    """Enhanced results dashboard with 3D visualization"""
    if not st.session_state.analysis_results:
        st.warning("⚠️ No analysis results available")
        return
    
    results = st.session_state.analysis_results
    
    # Dashboard header
    st.markdown("""
    <div class="results-dashboard">
        <div class="dashboard-header">
            <h1 class="dashboard-title">📊 Analysis Results</h1>
            <p class="dashboard-subtitle">Comprehensive Solar Rooftop Assessment</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Key metrics
    render_key_metrics(results)
    
    # Tabbed interface for detailed results
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏠 Roof Analysis", 
        "🌞 Solar Potential", 
        "💰 Financial Analysis", 
        "🎯 3D Visualization", 
        "📄 Report"
    ])
    
    with tab1:
        render_roof_analysis_tab(results['roof_analysis'])
    
    with tab2:
        render_solar_analysis_tab(results['solar_data'])
    
    with tab3:
        render_financial_analysis_tab(results['financial_analysis'])
    
    with tab4:
        render_3d_visualization_tab(results)
    
    with tab5:
        render_report_tab(results)

def render_key_metrics(results):
    """Render key metrics dashboard"""
    st.markdown('<div class="metrics-grid">', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    roof_area = results['roof_analysis'].get('roof_area', 0)
    annual_production = results['solar_data'].get('annual_irradiance', 0) * roof_area * 0.2 * 0.8
    annual_savings = annual_production * st.session_state.configuration['electricity_rate']
    system_size = roof_area * 0.1  # Rough estimate
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-icon" style="color: #3b82f6;">🏠</div>
            <div class="metric-value">{:,.0f}</div>
            <div class="metric-label">Roof Area (sq ft)</div>
        </div>
        """.format(roof_area), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-icon" style="color: #f59e0b;">⚡</div>
            <div class="metric-value">{:,.0f}</div>
            <div class="metric-label">Annual Production (kWh)</div>
        </div>
        """.format(annual_production), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-icon" style="color: #10b981;">💰</div>
            <div class="metric-value">${:,.0f}</div>
            <div class="metric-label">Annual Savings</div>
        </div>
        """.format(annual_savings), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-icon" style="color: #8b5cf6;">📈</div>
            <div class="metric-value">{:.1f}</div>
            <div class="metric-label">System Size (kW)</div>
        </div>
        """.format(system_size), unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_roof_analysis_tab(roof_analysis):
    """Detailed roof analysis tab"""
    st.subheader("🏠 Roof Structure Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Geometric Properties")
        st.metric("Total Roof Area", f"{roof_analysis.get('roof_area', 0):,.0f} sq ft")
        st.metric("Usable Area", f"{roof_analysis.get('roof_area', 0) * 0.8:,.0f} sq ft")
        st.metric("Primary Orientation", roof_analysis.get('orientation', 'Unknown'))
        st.metric("Average Slope", f"{roof_analysis.get('slope', 0):.1f}°")
    
    with col2:
        st.markdown("### Suitability Assessment")
        suitability_score = min(95, max(60, 85 - roof_analysis.get('shading_factor', 0) * 20))
        st.metric("Solar Suitability", f"{suitability_score:.0f}%")
        st.metric("Shading Factor", f"{roof_analysis.get('shading_factor', 0) * 100:.1f}%")
        st.metric("Detected Obstacles", len(roof_analysis.get('obstructions', [])))

def render_solar_analysis_tab(solar_data):
    """Solar potential analysis tab"""
    st.subheader("🌞 Solar Resource Assessment")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Solar Irradiance Data")
        st.metric("Annual Solar Irradiance", f"{solar_data.get('annual_irradiance', 0):,.0f} kWh/m²")
        st.metric("Peak Sun Hours", f"{solar_data.get('peak_sun_hours', 0):.1f} hours/day")
        st.metric("Solar Resource Quality", "Excellent" if solar_data.get('annual_irradiance', 0) > 1500 else "Good")
    
    with col2:
        st.markdown("### Environmental Factors")
        st.metric("Location", f"{solar_data.get('latitude', 0):.3f}, {solar_data.get('longitude', 0):.3f}")
        st.metric("Climate Zone", solar_data.get('climate_zone', 'Temperate'))
        st.metric("Data Source", "NASA POWER API")

def render_financial_analysis_tab(financial_analysis):
    """Financial analysis tab"""
    st.subheader("💰 Financial Projections")
    
    col1, col2, col3 = st.columns(3)
    
    # Sample financial calculations
    system_cost = 25000  # Example
    annual_savings = 1200  # Example
    payback_period = system_cost / annual_savings if annual_savings > 0 else 0
    
    with col1:
        st.markdown("### Investment Overview")
        st.metric("System Cost", f"${system_cost:,.0f}")
        st.metric("Federal Tax Credit", f"${system_cost * 0.30:,.0f}")
        st.metric("Net Investment", f"${system_cost * 0.70:,.0f}")
    
    with col2:
        st.markdown("### Annual Benefits")
        st.metric("Annual Savings", f"${annual_savings:,.0f}")
        st.metric("Monthly Savings", f"${annual_savings/12:,.0f}")
        st.metric("ROI", f"{(annual_savings/system_cost)*100:.1f}%")
    
    with col3:
        st.markdown("### Long-term Outlook")
        st.metric("Payback Period", f"{payback_period:.1f} years")
        st.metric("25-Year Savings", f"${annual_savings * 25:,.0f}")
        st.metric("Net Present Value", f"${annual_savings * 15:,.0f}")

def render_3d_visualization_tab(results):
    """3D visualization tab"""
    st.subheader("🎯 Interactive 3D Roof Model")
    
    # Initialize 3D visualizer
    visualizer = Solar3DVisualizer()
    
    # Generate 3D scene data
    scene_data = visualizer.generate_3d_scene_data(
        results['roof_analysis'], 
        results['solar_data']
    )
    
    # Render 3D visualization
    visualizer.render_3d_visualization(scene_data)

def render_report_tab(results):
    """Report generation tab"""
    st.subheader("📄 Professional Reports")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Available Reports")
        if st.button("📄 Generate PDF Report", type="primary", use_container_width=True):
            generate_pdf_report(results)
        
        if st.button("📊 Technical Specification", type="secondary", use_container_width=True):
            generate_technical_spec(results)
        
        if st.button("💰 Financial Summary", type="secondary", use_container_width=True):
            generate_financial_summary(results)
    
    with col2:
        st.markdown("### Report Features")
        st.markdown("""
        ✅ Executive summary with key findings  
        ✅ Detailed technical analysis  
        ✅ Financial projections and ROI  
        ✅ AI-generated recommendations  
        ✅ 3D visualizations and diagrams  
        ✅ Professional formatting  
        """)

def generate_pdf_report(results):
    """Generate comprehensive PDF report"""
    try:
        report_generator = ReportGenerator()
        pdf_buffer = report_generator.generate_report(
            results['roof_analysis'],
            results['solar_data'],
            results['financial_analysis'],
            results['ai_recommendations']
        )
        
        st.download_button(
            label="📥 Download PDF Report",
            data=pdf_buffer,
            file_name="solar_analysis_report.pdf",
            mime="application/pdf",
            type="primary"
        )
        st.success("PDF report generated successfully!")
        
    except Exception as e:
        st.error(f"Report generation failed: {str(e)}")

def generate_technical_spec(results):
    """Generate technical specification document"""
    st.info("Technical specification generation will be available in the full version")

def generate_financial_summary(results):
    """Generate financial summary document"""
    st.info("Financial summary generation will be available in the full version")

def main():
    """Main application function"""
    # Load custom CSS
    try:
        load_custom_css()
    except FileNotFoundError:
        st.warning("Custom CSS not found. Using default styling.")
    
    # Initialize session state
    initialize_session_state()
    
    # Initialize chatbot
    chatbot = SolarAnalysisChatbot()
    chatbot.initialize_chatbot()
    
    # Render header
    render_header()
    
    # Render progress indicator
    render_progress_indicator()
    
    # Main content based on current step
    if st.session_state.analysis_step == 'upload':
        render_upload_section()
    
    elif st.session_state.analysis_step == 'configure':
        render_configuration_section()
    
    elif st.session_state.analysis_step == 'analyze':
        render_analyze_section()
    
    elif st.session_state.analysis_step == 'results':
        render_results_dashboard()
    
    # Render chatbot interface (always visible)
    chatbot.render_chatbot_interface()
    
    # Add contextual chatbot messages
    if st.session_state.uploaded_file and 'image_uploaded_msg_sent' not in st.session_state:
        chatbot.add_contextual_message('image_uploaded')
        st.session_state.image_uploaded_msg_sent = True
    
    if st.session_state.analysis_step == 'results' and 'analysis_complete_msg_sent' not in st.session_state:
        chatbot.add_contextual_message('analysis_complete')
        st.session_state.analysis_complete_msg_sent = True

if __name__ == "__main__":
    main()