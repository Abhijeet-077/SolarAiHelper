import streamlit as st
import os
import tempfile
from PIL import Image
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io

# Import backend modules
from backend.image_analysis import RoofAnalyzer
from backend.llm_integration import LLMGenerator
from backend.solar_calculations import SolarCalculator
from backend.nasa_api import NASADataProvider
from backend.report_generator import ReportGenerator
from utils.validators import ImageValidator
from utils.helpers import format_currency, format_number
from config.constants import PANEL_SPECS, UI_CONFIG

# Configure page
st.set_page_config(
    page_title="🌞 AI Solar Analysis Platform",
    page_icon="🌞",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None

def main():
    """Main application function"""
    
    # Header
    st.title("☀️ AI-Powered Solar Rooftop Analysis")
    st.markdown("**Analyze your rooftop's solar potential using satellite imagery and AI**")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Analysis Configuration")
        
        # Location input
        st.subheader("📍 Location Details")
        latitude = st.number_input("Latitude", value=37.7749, format="%.6f", help="Enter the latitude of your location")
        longitude = st.number_input("Longitude", value=-122.4194, format="%.6f", help="Enter the longitude of your location")
        
        # Panel preferences
        st.subheader("🔧 System Preferences")
        panel_type = st.selectbox("Panel Type", options=list(PANEL_SPECS.keys()))
        electricity_rate = st.number_input("Electricity Rate ($/kWh)", value=0.20, format="%.3f")
        
        # Installation details
        installation_cost_per_watt = st.number_input("Installation Cost ($/Watt)", value=3.0, format="%.2f")
        
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📤 Upload Satellite Image")
        
        uploaded_file = st.file_uploader(
            "Choose a satellite image of your rooftop",
            type=['jpg', 'jpeg', 'png'],
            help="Upload a clear satellite image of your property"
        )
        
        if uploaded_file is not None:
            # Validate image
            validator = ImageValidator()
            is_valid, message = validator.validate_image(uploaded_file)
            
            if not is_valid:
                st.error(f"❌ {message}")
                return
            
            # Display uploaded image
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Satellite Image", use_column_width=True)
            
            # Analysis button
            if st.button("🔍 Analyze Solar Potential", type="primary", use_container_width=True):
                analyze_rooftop(uploaded_file, latitude, longitude, panel_type, 
                              electricity_rate, installation_cost_per_watt)
    
    with col2:
        if st.session_state.analysis_complete and st.session_state.analysis_results:
            display_results()
        else:
            st.header("📊 Analysis Results")
            st.info("Upload an image and click 'Analyze Solar Potential' to see results")

def analyze_rooftop(uploaded_file, latitude, longitude, panel_type, electricity_rate, installation_cost_per_watt):
    """Perform complete rooftop analysis"""
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            temp_image_path = tmp_file.name
        
        # Step 1: Image Analysis
        status_text.text("🔍 Analyzing roof characteristics...")
        progress_bar.progress(20)
        
        roof_analyzer = RoofAnalyzer()
        roof_metrics = roof_analyzer.analyze_roof(temp_image_path)
        
        # Step 2: Get NASA solar data
        status_text.text("🌞 Fetching solar irradiance data...")
        progress_bar.progress(40)
        
        nasa_provider = NASADataProvider()
        solar_data = nasa_provider.get_solar_data(latitude, longitude)
        
        # Step 3: Perform solar calculations
        status_text.text("⚡ Calculating solar potential...")
        progress_bar.progress(60)
        
        calculator = SolarCalculator()
        solar_potential = calculator.calculate_potential(
            roof_metrics, solar_data, panel_type, 
            electricity_rate, installation_cost_per_watt
        )
        
        # Step 4: Generate LLM recommendations
        status_text.text("🤖 Generating AI recommendations...")
        progress_bar.progress(80)
        
        llm_generator = LLMGenerator()
        recommendations = llm_generator.generate_recommendations(
            roof_metrics, solar_potential, latitude, longitude
        )
        
        # Compile results
        results = {
            'roof_metrics': roof_metrics,
            'solar_data': solar_data,
            'solar_potential': solar_potential,
            'recommendations': recommendations,
            'analysis_timestamp': datetime.now(),
            'location': {'latitude': latitude, 'longitude': longitude},
            'panel_type': panel_type,
            'electricity_rate': electricity_rate,
            'installation_cost_per_watt': installation_cost_per_watt
        }
        
        status_text.text("✅ Analysis complete!")
        progress_bar.progress(100)
        
        # Store results in session state
        st.session_state.analysis_results = results
        st.session_state.analysis_complete = True
        
        # Clean up
        os.unlink(temp_image_path)
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        st.success("🎉 Analysis completed successfully!")
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

def display_results():
    """Display analysis results with visualizations"""
    
    results = st.session_state.analysis_results
    
    st.header("📊 Analysis Results")
    
    # Key metrics cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Roof Area",
            f"{format_number(results['roof_metrics']['usable_area'])} m²",
            help="Usable roof area for solar panels"
        )
    
    with col2:
        st.metric(
            "Annual Energy",
            f"{format_number(results['solar_potential']['annual_energy_kwh'])} kWh",
            help="Estimated annual energy production"
        )
    
    with col3:
        st.metric(
            "Annual Savings",
            format_currency(results['solar_potential']['annual_savings']),
            help="Estimated annual electricity bill savings"
        )
    
    with col4:
        st.metric(
            "Payback Period",
            f"{results['solar_potential']['payback_years']:.1f} years",
            help="Time to recover initial investment"
        )
    
    # Tabs for detailed information
    tab1, tab2, tab3, tab4 = st.tabs(["🏠 Roof Analysis", "📈 Financial Analysis", "🤖 AI Recommendations", "📋 Report"])
    
    with tab1:
        display_roof_analysis(results)
    
    with tab2:
        display_financial_analysis(results)
    
    with tab3:
        display_recommendations(results)
    
    with tab4:
        display_report_section(results)

def display_roof_analysis(results):
    """Display roof analysis details"""
    
    roof_metrics = results['roof_metrics']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Roof Characteristics")
        
        metrics_df = pd.DataFrame([
            {"Metric": "Total Roof Area", "Value": f"{format_number(roof_metrics['total_area'])} m²"},
            {"Metric": "Usable Area", "Value": f"{format_number(roof_metrics['usable_area'])} m²"},
            {"Metric": "Primary Orientation", "Value": roof_metrics['orientation']},
            {"Metric": "Roof Slope", "Value": f"{roof_metrics['slope']}°"},
            {"Metric": "Shading Factor", "Value": f"{roof_metrics['shading_factor']:.2f}"},
            {"Metric": "Obstructions", "Value": f"{roof_metrics['obstruction_count']} detected"}
        ])
        
        st.dataframe(metrics_df, use_container_width=True, hide_index=True)
    
    with col2:
        st.subheader("Solar Irradiance Data")
        
        solar_data = results['solar_data']
        if 'monthly_irradiance' in solar_data:
            # Create monthly irradiance chart
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=months,
                y=solar_data['monthly_irradiance'],
                mode='lines+markers',
                name='Solar Irradiance',
                line=dict(color='orange', width=3),
                marker=dict(size=8)
            ))
            
            fig.update_layout(
                title="Monthly Solar Irradiance",
                xaxis_title="Month",
                yaxis_title="Irradiance (kWh/m²/day)",
                height=300
            )
            
            st.plotly_chart(fig, use_container_width=True)

def display_financial_analysis(results):
    """Display financial analysis and ROI calculations"""
    
    solar_potential = results['solar_potential']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💰 Financial Summary")
        
        financial_df = pd.DataFrame([
            {"Item": "System Size", "Value": f"{format_number(solar_potential['system_size_kw'])} kW"},
            {"Item": "Total Installation Cost", "Value": format_currency(solar_potential['total_cost'])},
            {"Item": "Annual Energy Production", "Value": f"{format_number(solar_potential['annual_energy_kwh'])} kWh"},
            {"Item": "Annual Savings", "Value": format_currency(solar_potential['annual_savings'])},
            {"Item": "25-Year Savings", "Value": format_currency(solar_potential['lifetime_savings'])},
            {"Item": "ROI", "Value": f"{solar_potential['roi_percent']:.1f}%"}
        ])
        
        st.dataframe(financial_df, use_container_width=True, hide_index=True)
    
    with col2:
        st.subheader("📊 Payback Analysis")
        
        # Generate payback chart
        years = list(range(0, 26))
        cumulative_savings = [year * solar_potential['annual_savings'] for year in years]
        initial_cost = [solar_potential['total_cost']] * len(years)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=years,
            y=cumulative_savings,
            mode='lines',
            name='Cumulative Savings',
            line=dict(color='green', width=3)
        ))
        
        fig.add_trace(go.Scatter(
            x=years,
            y=initial_cost,
            mode='lines',
            name='Initial Investment',
            line=dict(color='red', width=2, dash='dash')
        ))
        
        # Add break-even point
        payback_year = solar_potential['payback_years']
        if payback_year <= 25:
            fig.add_trace(go.Scatter(
                x=[payback_year],
                y=[solar_potential['total_cost']],
                mode='markers',
                name='Break-even Point',
                marker=dict(color='blue', size=12, symbol='star')
            ))
        
        fig.update_layout(
            title="Investment Payback Timeline",
            xaxis_title="Years",
            yaxis_title="Amount ($)",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)

def display_recommendations(results):
    """Display AI-generated recommendations"""
    
    recommendations = results['recommendations']
    
    st.subheader("🤖 AI-Generated Recommendations")
    
    # Installation recommendations
    if 'installation_plan' in recommendations:
        st.markdown("### 🔧 Installation Plan")
        st.markdown(recommendations['installation_plan'])
    
    # System optimization
    if 'optimization_tips' in recommendations:
        st.markdown("### ⚡ System Optimization")
        st.markdown(recommendations['optimization_tips'])
    
    # Compliance information
    if 'compliance_info' in recommendations:
        st.markdown("### 📋 Regulatory Compliance")
        st.markdown(recommendations['compliance_info'])
    
    # Maintenance recommendations
    if 'maintenance_plan' in recommendations:
        st.markdown("### 🔧 Maintenance Guidelines")
        st.markdown(recommendations['maintenance_plan'])

def display_report_section(results):
    """Display report generation section"""
    
    st.subheader("📋 Generate Professional Report")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        Generate a comprehensive PDF report including:
        - Detailed roof analysis results
        - Solar potential assessment
        - Financial projections and ROI analysis
        - AI-generated recommendations
        - Compliance checklist
        """)
    
    with col2:
        if st.button("📄 Generate PDF Report", type="primary", use_container_width=True):
            generate_pdf_report(results)

def generate_pdf_report(results):
    """Generate and download PDF report"""
    
    try:
        with st.spinner("Generating PDF report..."):
            report_generator = ReportGenerator()
            pdf_buffer = report_generator.generate_report(results)
            
            st.download_button(
                label="⬇️ Download Report",
                data=pdf_buffer.getvalue(),
                file_name=f"solar_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
        st.success("✅ Report generated successfully!")
        
    except Exception as e:
        st.error(f"❌ Failed to generate report: {str(e)}")

if __name__ == "__main__":
    main()
