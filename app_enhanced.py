import streamlit as st
import os
import tempfile
from PIL import Image
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
import json
import base64

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

# Try to import advanced CV module, fallback if not available
try:
    from backend.advanced_cv_analysis import AdvancedRoofAnalyzer
    ADVANCED_CV_AVAILABLE = True
except ImportError:
    ADVANCED_CV_AVAILABLE = False
    AdvancedRoofAnalyzer = None

# Configure page
st.set_page_config(
    page_title="Advanced Solar Rooftop Analysis",
    page_icon="🌞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced UI
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .analysis-mode {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        margin: 1rem 0;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #f1f3f4;
        border-radius: 8px 8px 0 0;
        padding: 0.5rem 1rem;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #667eea;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'analysis_mode' not in st.session_state:
    st.session_state.analysis_mode = "standard"

def main():
    """Enhanced main application function"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🌞 Advanced AI-Powered Solar Rooftop Analysis</h1>
        <p>Cutting-edge computer vision and 3D modeling for comprehensive solar potential assessment</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Analysis mode selection
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🎯 Analysis Mode")
        
        # Available modes based on system capabilities
        available_modes = ["Standard Analysis", "Professional Assessment"]
        if ADVANCED_CV_AVAILABLE:
            available_modes.insert(1, "Advanced CV Analysis")
        
        analysis_mode = st.selectbox(
            "Choose analysis depth:",
            available_modes,
            index=0,
            help="Professional Assessment includes comprehensive data integration and AI recommendations"
        )
        st.session_state.analysis_mode = analysis_mode.lower().replace(" ", "_")
    
    # Main layout
    col_left, col_right = st.columns([1.2, 0.8])
    
    with col_left:
        display_upload_section()
    
    with col_right:
        display_configuration_panel()
    
    # Results section
    if st.session_state.analysis_complete and st.session_state.analysis_results:
        st.markdown("---")
        display_enhanced_results()

def display_upload_section():
    """Enhanced image upload section with 3D preview"""
    
    st.markdown("### 📤 Satellite Image Upload")
    
    # File uploader with enhanced features
    uploaded_file = st.file_uploader(
        "Upload high-resolution satellite image",
        type=['jpg', 'jpeg', 'png'],
        help="For best results, use satellite images with resolution ≥ 1024x1024 pixels"
    )
    
    if uploaded_file is not None:
        # Image validation
        validator = ImageValidator()
        is_valid, message = validator.validate_image(uploaded_file)
        
        if not is_valid:
            st.error(f"❌ {message}")
            return
        
        # Display image with analysis overlay
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("**📸 Original Image**")
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Satellite Image", use_column_width=True)
            
            # Image metadata
            st.markdown("**📊 Image Information**")
            st.write(f"• Dimensions: {image.size[0]} x {image.size[1]} pixels")
            st.write(f"• Format: {image.format}")
            st.write(f"• Mode: {image.mode}")
        
        with col2:
            st.markdown("**🔍 Analysis Preview**")
            
            # Quick analysis preview
            if st.button("🚀 Quick Preview", type="secondary", use_container_width=True):
                with st.spinner("Generating preview..."):
                    preview_results = perform_quick_analysis(uploaded_file)
                    display_preview_results(preview_results)
            
            # 3D Visualization placeholder
            st.markdown("**🏠 3D Roof Model**")
            display_3d_placeholder()
        
        # Analysis button
        st.markdown("---")
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
        
        with col_btn1:
            if st.button("🔬 Analyze Solar Potential", type="primary", use_container_width=True):
                perform_comprehensive_analysis(uploaded_file)
        
        with col_btn2:
            if st.button("📋 Generate Report", use_container_width=True, disabled=not st.session_state.analysis_complete):
                generate_enhanced_report()
        
        with col_btn3:
            if st.button("🔄 Reset Analysis", use_container_width=True):
                reset_analysis()

def display_configuration_panel():
    """Enhanced configuration panel"""
    
    st.markdown("### ⚙️ Analysis Configuration")
    
    # Location settings
    with st.expander("📍 Location Settings", expanded=True):
        st.markdown("**Geographical Coordinates**")
        
        col1, col2 = st.columns(2)
        with col1:
            latitude = st.number_input(
                "Latitude",
                value=37.7749,
                format="%.6f",
                help="Enter precise latitude for accurate solar irradiance data"
            )
        with col2:
            longitude = st.number_input(
                "Longitude",
                value=-122.4194,
                format="%.6f",
                help="Enter precise longitude for accurate solar irradiance data"
            )
        
        # Location validation
        if st.button("📍 Validate Location"):
            if -90 <= latitude <= 90 and -180 <= longitude <= 180:
                st.success(f"✅ Valid coordinates: {latitude:.4f}°, {longitude:.4f}°")
            else:
                st.error("❌ Invalid coordinates")
    
    # System configuration
    with st.expander("🔧 System Configuration", expanded=True):
        panel_type = st.selectbox(
            "Solar Panel Type",
            options=list(PANEL_SPECS.keys()),
            format_func=lambda x: x.replace('_', ' ').title(),
            help="Choose panel technology based on efficiency and budget requirements"
        )
        
        electricity_rate = st.number_input(
            "Electricity Rate ($/kWh)",
            value=0.20,
            min_value=0.01,
            max_value=1.0,
            format="%.3f",
            help="Local electricity rate for savings calculations"
        )
        
        installation_cost = st.number_input(
            "Installation Cost ($/Watt)",
            value=3.0,
            min_value=1.0,
            max_value=10.0,
            format="%.2f",
            help="Total installation cost including equipment and labor"
        )
    
    # Advanced settings
    with st.expander("🔬 Advanced Analysis Settings"):
        st.markdown("**Computer Vision Parameters**")
        
        confidence_threshold = st.slider(
            "Detection Confidence Threshold",
            min_value=0.1,
            max_value=1.0,
            value=0.8,
            step=0.1,
            help="Minimum confidence for roof detection"
        )
        
        enable_3d_modeling = st.checkbox(
            "Enable 3D Roof Modeling",
            value=True,
            help="Generate detailed 3D models for visualization"
        )
        
        enable_advanced_shading = st.checkbox(
            "Advanced Shading Analysis",
            value=True,
            help="Detailed shadow pattern analysis throughout the day"
        )
    
    # Store configuration in session state
    st.session_state.config = {
        'latitude': latitude,
        'longitude': longitude,
        'panel_type': panel_type,
        'electricity_rate': electricity_rate,
        'installation_cost': installation_cost,
        'confidence_threshold': confidence_threshold,
        'enable_3d_modeling': enable_3d_modeling,
        'enable_advanced_shading': enable_advanced_shading
    }

def perform_quick_analysis(uploaded_file):
    """Perform quick analysis for preview"""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            temp_image_path = tmp_file.name
        
        # Quick roof analysis
        analyzer = RoofAnalyzer()
        roof_metrics = analyzer.analyze_roof(temp_image_path)
        
        # Clean up
        os.unlink(temp_image_path)
        
        return roof_metrics
        
    except Exception as e:
        st.error(f"Preview analysis failed: {str(e)}")
        return None

def display_preview_results(results):
    """Display quick preview results"""
    if results:
        st.markdown("**Quick Analysis Results:**")
        st.write(f"• Roof Area: {results['total_area']:.1f} m²")
        st.write(f"• Orientation: {results['orientation']}")
        st.write(f"• Estimated Panels: {int(results['usable_area'] / 2)}")

def display_3d_placeholder():
    """Display 3D visualization placeholder"""
    # For now, show a placeholder - would integrate with the 3D viewer component
    st.markdown("""
    <div style="background: linear-gradient(45deg, #f0f0f0, #e0e0e0); 
                height: 200px; 
                border-radius: 8px; 
                display: flex; 
                align-items: center; 
                justify-content: center;
                border: 2px dashed #ccc;">
        <div style="text-align: center; color: #666;">
            <h4>🏠 3D Roof Model</h4>
            <p>Upload and analyze image to view 3D model</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

def perform_comprehensive_analysis(uploaded_file):
    """Perform comprehensive analysis with advanced CV"""
    
    config = st.session_state.config
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            temp_image_path = tmp_file.name
        
        # Step 1: Advanced Computer Vision Analysis
        status_text.text("🔍 Performing roof analysis...")
        progress_bar.progress(20)
        
        if st.session_state.analysis_mode == "advanced_cv_analysis" and ADVANCED_CV_AVAILABLE and AdvancedRoofAnalyzer:
            analyzer = AdvancedRoofAnalyzer()
            roof_analysis = analyzer.analyze_roof_advanced(
                temp_image_path,
                location_data={'latitude': config['latitude'], 'longitude': config['longitude']}
            )
        else:
            analyzer = RoofAnalyzer()
            basic_analysis = analyzer.analyze_roof(temp_image_path)
            roof_analysis = convert_basic_to_advanced_format(basic_analysis)
        
        # Step 2: NASA Solar Data
        status_text.text("🌞 Retrieving solar irradiance data...")
        progress_bar.progress(40)
        
        nasa_provider = NASADataProvider()
        solar_data = nasa_provider.get_solar_data(config['latitude'], config['longitude'])
        
        # Step 3: Solar Calculations
        status_text.text("⚡ Calculating solar potential...")
        progress_bar.progress(60)
        
        calculator = SolarCalculator()
        # Extract roof metrics for compatibility
        roof_metrics = extract_roof_metrics_for_calculator(roof_analysis)
        solar_potential = calculator.calculate_potential(
            roof_metrics, solar_data, config['panel_type'],
            config['electricity_rate'], config['installation_cost']
        )
        
        # Step 4: AI Recommendations
        status_text.text("🤖 Generating AI recommendations...")
        progress_bar.progress(80)
        
        llm_generator = LLMGenerator()
        recommendations = llm_generator.generate_recommendations(
            roof_metrics, solar_potential, config['latitude'], config['longitude']
        )
        
        # Compile comprehensive results
        results = {
            'roof_analysis': roof_analysis,
            'roof_metrics': roof_metrics,
            'solar_data': solar_data,
            'solar_potential': solar_potential,
            'recommendations': recommendations,
            'analysis_timestamp': datetime.now(),
            'location': {'latitude': config['latitude'], 'longitude': config['longitude']},
            'configuration': config,
            'analysis_mode': st.session_state.analysis_mode
        }
        
        status_text.text("✅ Analysis complete!")
        progress_bar.progress(100)
        
        # Store results
        st.session_state.analysis_results = results
        st.session_state.analysis_complete = True
        
        # Clean up
        os.unlink(temp_image_path)
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        st.success("🎉 Comprehensive analysis completed successfully!")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Analysis failed: {str(e)}")
        progress_bar.empty()
        status_text.empty()
        
        # Clean up on error
        if 'temp_image_path' in locals():
            try:
                os.unlink(temp_image_path)
            except:
                pass

def display_enhanced_results():
    """Display enhanced analysis results with 3D visualization"""
    
    results = st.session_state.analysis_results
    
    st.markdown("## 📊 Comprehensive Analysis Results")
    
    # Key metrics dashboard
    display_metrics_dashboard(results)
    
    # Tabbed results interface
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🏠 Roof Analysis", 
        "📈 Solar Potential", 
        "💰 Financial Analysis",
        "🤖 AI Recommendations",
        "🌍 3D Visualization",
        "📋 Professional Report"
    ])
    
    with tab1:
        display_advanced_roof_analysis(results)
    
    with tab2:
        display_solar_potential_analysis(results)
    
    with tab3:
        display_financial_analysis(results)
    
    with tab4:
        display_ai_recommendations(results)
    
    with tab5:
        display_3d_visualization(results)
    
    with tab6:
        display_report_section(results)

def display_metrics_dashboard(results):
    """Display key metrics in an attractive dashboard"""
    
    # Extract key metrics
    roof_analysis = results.get('roof_analysis', {})
    solar_potential = results['solar_potential']
    
    # Top-level metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    metrics = [
        ("🏠 Roof Area", f"{format_number(roof_analysis.get('roof_segmentation', {}).get('total_roof_area_m2', 0))} m²"),
        ("⚡ System Size", f"{format_number(solar_potential['system_size_kw'])} kW"),
        ("🔋 Annual Energy", f"{format_number(solar_potential['annual_energy_kwh'])} kWh"),
        ("💰 Annual Savings", format_currency(solar_potential['annual_savings'])),
        ("⏱️ Payback", f"{solar_potential['payback_years']:.1f} years")
    ]
    
    for col, (label, value) in zip([col1, col2, col3, col4, col5], metrics):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 14px; opacity: 0.9;">{label}</div>
                <div style="font-size: 20px; font-weight: bold; margin-top: 5px;">{value}</div>
            </div>
            """, unsafe_allow_html=True)

def display_advanced_roof_analysis(results):
    """Display advanced roof analysis results"""
    
    roof_analysis = results.get('roof_analysis', {})
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🔬 Computer Vision Analysis")
        
        if 'roof_segmentation' in roof_analysis:
            seg_data = roof_analysis['roof_segmentation']
            
            analysis_df = pd.DataFrame([
                {"Property": "Total Roof Area", "Value": f"{seg_data.get('total_roof_area_m2', 0):.1f} m²"},
                {"Property": "Usable Area", "Value": f"{seg_data.get('usable_area_m2', 0):.1f} m²"},
                {"Property": "Primary Orientation", "Value": seg_data.get('primary_orientation', 'Unknown')},
                {"Property": "Average Slope", "Value": f"{seg_data.get('average_slope_degrees', 0):.1f}°"},
                {"Property": "Roof Complexity", "Value": f"{seg_data.get('roof_complexity_score', 0):.2f}"},
                {"Property": "Detected Polygons", "Value": str(len(seg_data.get('roof_polygons', [])))}
            ])
            
            st.dataframe(analysis_df, use_container_width=True, hide_index=True)
        
        # Obstacle detection results
        if 'obstacle_detection' in roof_analysis:
            st.markdown("### 🚧 Obstacle Detection")
            obs_data = roof_analysis['obstacle_detection']
            
            st.metric("Obstacles Detected", obs_data.get('obstacles_detected', 0))
            st.metric("Total Obstruction Area", f"{obs_data.get('total_obstruction_area_m2', 0):.1f} m²")
    
    with col2:
        st.markdown("### ☀️ Shading Analysis")
        
        if 'shading_analysis' in roof_analysis:
            shading_data = roof_analysis['shading_analysis']
            
            # Shading factor visualization
            shading_factor = shading_data.get('shading_factor', 0)
            
            fig = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = (1 - shading_factor) * 100,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Solar Efficiency %"},
                delta = {'reference': 85},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 80], 'color': "yellow"},
                        {'range': [80, 100], 'color': "green"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
            
            st.metric("Optimal Sun Hours", f"{shading_data.get('optimal_hours', 0):.1f} hours/day")

def display_solar_potential_analysis(results):
    """Display solar potential analysis"""
    
    solar_potential = results['solar_potential']
    solar_data = results['solar_data']
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🔋 System Specifications")
        
        specs_df = pd.DataFrame([
            {"Specification": "System Capacity", "Value": f"{format_number(solar_potential['system_size_kw'])} kW"},
            {"Specification": "Panel Count", "Value": str(solar_potential['panel_count'])},
            {"Specification": "Panel Type", "Value": results['configuration']['panel_type'].title()},
            {"Specification": "Annual Energy", "Value": f"{format_number(solar_potential['annual_energy_kwh'])} kWh"},
            {"Specification": "Capacity Factor", "Value": f"{solar_potential['capacity_factor']*100:.1f}%"}
        ])
        
        st.dataframe(specs_df, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("### 📊 Monthly Energy Production")
        
        if 'monthly_irradiance' in solar_data:
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            
            monthly_energy = [
                solar_potential['annual_energy_kwh'] / 12 * (irr / sum(solar_data['monthly_irradiance']) * 12)
                for irr in solar_data['monthly_irradiance']
            ]
            
            fig = px.bar(
                x=months,
                y=monthly_energy,
                title="Monthly Energy Production",
                labels={'x': 'Month', 'y': 'Energy (kWh)'},
                color=monthly_energy,
                color_continuous_scale='Viridis'
            )
            
            fig.update_layout(showlegend=False, height=300)
            st.plotly_chart(fig, use_container_width=True)

def display_financial_analysis(results):
    """Display financial analysis"""
    
    solar_potential = results['solar_potential']
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 💰 Investment Summary")
        
        financial_df = pd.DataFrame([
            {"Item": "Total System Cost", "Amount": format_currency(solar_potential['total_cost'])},
            {"Item": "Federal Incentive", "Amount": format_currency(solar_potential.get('federal_incentive', 0))},
            {"Item": "Net Investment", "Amount": format_currency(solar_potential.get('net_cost', solar_potential['total_cost']))},
            {"Item": "Annual Savings", "Amount": format_currency(solar_potential['annual_savings'])},
            {"Item": "25-Year Savings", "Amount": format_currency(solar_potential.get('lifetime_savings', 0))},
            {"Item": "ROI", "Amount": f"{solar_potential.get('roi_percent', 0):.1f}%"}
        ])
        
        st.dataframe(financial_df, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("### 📈 Payback Timeline")
        
        # Generate payback chart
        years = list(range(0, 26))
        cumulative_savings = [year * solar_potential['annual_savings'] for year in years]
        initial_cost = [solar_potential['total_cost']] * len(years)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=years, y=cumulative_savings,
            mode='lines', name='Cumulative Savings',
            line=dict(color='green', width=3)
        ))
        
        fig.add_trace(go.Scatter(
            x=years, y=initial_cost,
            mode='lines', name='Initial Investment',
            line=dict(color='red', width=2, dash='dash')
        ))
        
        fig.update_layout(
            title="Investment Payback Analysis",
            xaxis_title="Years", yaxis_title="Amount ($)",
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)

def display_ai_recommendations(results):
    """Display AI-generated recommendations"""
    
    recommendations = results['recommendations']
    
    # Installation recommendations
    if 'installation_plan' in recommendations:
        st.markdown("### 🔧 Installation Plan")
        st.markdown(recommendations['installation_plan'])
    
    # Optimization tips
    if 'optimization_tips' in recommendations:
        st.markdown("### ⚡ Optimization Recommendations")
        st.markdown(recommendations['optimization_tips'])
    
    # Compliance information
    if 'compliance_info' in recommendations:
        st.markdown("### 📋 Regulatory Compliance")
        st.markdown(recommendations['compliance_info'])

def display_3d_visualization(results):
    """Display 3D visualization interface"""
    
    st.markdown("### 🏠 Interactive 3D Roof Model")
    
    # For now, display a message about 3D integration
    st.info("🚀 3D visualization is being integrated. This will include:")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        **3D Features:**
        - Interactive roof model
        - Solar panel placement simulation
        - Real-time shading analysis
        - Sun path visualization
        - Export to CAD formats
        """)
    
    with col2:
        st.markdown("""
        **Analysis Tools:**
        - Optimal panel orientation
        - Seasonal shading patterns
        - Installation zone mapping
        - Performance optimization
        - Visual impact assessment
        """)
    
    # Placeholder for 3D viewer integration
    st.markdown("""
    <iframe src="frontend/components/roof_3d_viewer.html" 
            width="100%" height="500" 
            style="border: none; border-radius: 10px;">
    </iframe>
    """, unsafe_allow_html=True)

def display_report_section(results):
    """Enhanced report generation section"""
    
    st.markdown("### 📋 Professional Report Generation")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        **Comprehensive Professional Report includes:**
        
        🔬 **Technical Analysis**
        - Advanced computer vision results
        - Detailed roof geometry analysis
        - Obstacle detection mapping
        - Shading pattern analysis
        
        📊 **Performance Projections**
        - Monthly energy production forecasts
        - Seasonal variation analysis
        - Long-term performance modeling
        - System degradation considerations
        
        💰 **Financial Analysis**
        - Detailed cost breakdown
        - Incentive optimization
        - Cash flow projections
        - ROI sensitivity analysis
        
        🤖 **AI Recommendations**
        - Installation optimization
        - Maintenance planning
        - Regulatory compliance
        - Performance monitoring
        """)
    
    with col2:
        st.markdown("**Report Options:**")
        
        report_format = st.selectbox(
            "Report Format",
            ["PDF Professional", "PDF Summary", "JSON Data Export"],
            help="Choose report format based on your needs"
        )
        
        include_3d = st.checkbox("Include 3D Models", value=True)
        include_detailed_cv = st.checkbox("Include CV Analysis", value=True)
        
        if st.button("📄 Generate Report", type="primary", use_container_width=True):
            generate_enhanced_report(report_format, include_3d, include_detailed_cv)

def generate_enhanced_report(format_type="PDF Professional", include_3d=True, include_cv=True):
    """Generate enhanced professional report"""
    
    try:
        with st.spinner("Generating comprehensive report..."):
            if format_type == "JSON Data Export":
                # Export JSON data
                json_data = json.dumps(st.session_state.analysis_results, 
                                     default=str, indent=2)
                
                st.download_button(
                    label="⬇️ Download JSON Data",
                    data=json_data,
                    file_name=f"solar_analysis_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
            else:
                # Generate PDF report
                report_generator = ReportGenerator()
                pdf_buffer = report_generator.generate_report(st.session_state.analysis_results)
                
                st.download_button(
                    label="⬇️ Download PDF Report",
                    data=pdf_buffer.getvalue(),
                    file_name=f"solar_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        
        st.success("✅ Report generated successfully!")
        
    except Exception as e:
        st.error(f"❌ Failed to generate report: {str(e)}")

def reset_analysis():
    """Reset analysis state"""
    st.session_state.analysis_complete = False
    st.session_state.analysis_results = None
    st.rerun()

# Helper functions
def convert_basic_to_advanced_format(basic_analysis):
    """Convert basic analysis to advanced format for compatibility"""
    return {
        'roof_segmentation': {
            'total_roof_area_m2': basic_analysis.get('total_area', 0),
            'usable_area_m2': basic_analysis.get('usable_area', 0),
            'primary_orientation': basic_analysis.get('orientation', 'south'),
            'average_slope_degrees': basic_analysis.get('slope', 25),
            'roof_complexity_score': 0.3,
            'roof_polygons': []
        },
        'obstacle_detection': {
            'obstacles_detected': basic_analysis.get('obstruction_count', 0),
            'obstacle_details': basic_analysis.get('obstructions', []),
            'total_obstruction_area_m2': 2.0
        },
        'shading_analysis': {
            'shading_factor': basic_analysis.get('shading_factor', 0.15),
            'shadow_patterns': [],
            'seasonal_variation': 0.3,
            'optimal_hours': 6.5
        }
    }

def extract_roof_metrics_for_calculator(roof_analysis):
    """Extract roof metrics compatible with solar calculator"""
    seg_data = roof_analysis.get('roof_segmentation', {})
    shading_data = roof_analysis.get('shading_analysis', {})
    obs_data = roof_analysis.get('obstacle_detection', {})
    
    return {
        'total_area': seg_data.get('total_roof_area_m2', 120),
        'usable_area': seg_data.get('usable_area_m2', 90),
        'orientation': seg_data.get('primary_orientation', 'south'),
        'slope': seg_data.get('average_slope_degrees', 25),
        'shading_factor': shading_data.get('shading_factor', 0.15),
        'obstruction_count': obs_data.get('obstacles_detected', 0)
    }

if __name__ == "__main__":
    main()