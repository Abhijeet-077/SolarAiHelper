import os
import io
from datetime import datetime
from typing import Dict, Any
import logging
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from utils.helpers import format_currency, format_number

class ReportGenerator:
    """Generate comprehensive PDF reports for solar analysis results"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles for the report"""
        
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=colors.HexColor('#2E86C1'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1B4F72'),
            spaceBefore=20,
            spaceAfter=10,
            borderWidth=1,
            borderColor=colors.HexColor('#85C1E9'),
            borderPadding=5
        ))
        
        # Subsection header style
        self.styles.add(ParagraphStyle(
            name='SubsectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2874A6'),
            spaceBefore=15,
            spaceAfter=8
        ))
        
        # Highlight style for key metrics
        self.styles.add(ParagraphStyle(
            name='Highlight',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#D35400'),
            fontName='Helvetica-Bold'
        ))
    
    def generate_report(self, analysis_results: Dict[str, Any]) -> io.BytesIO:
        """
        Generate a comprehensive PDF report
        
        Args:
            analysis_results: Complete analysis results from the application
            
        Returns:
            BytesIO buffer containing the PDF report
        """
        
        try:
            # Create PDF buffer
            buffer = io.BytesIO()
            
            # Create document
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Build report content
            story = []
            
            # Title page
            story.extend(self._create_title_page(analysis_results))
            story.append(PageBreak())
            
            # Executive summary
            story.extend(self._create_executive_summary(analysis_results))
            story.append(PageBreak())
            
            # Roof analysis section
            story.extend(self._create_roof_analysis_section(analysis_results))
            story.append(PageBreak())
            
            # Solar potential section
            story.extend(self._create_solar_potential_section(analysis_results))
            story.append(PageBreak())
            
            # Financial analysis section
            story.extend(self._create_financial_analysis_section(analysis_results))
            story.append(PageBreak())
            
            # Recommendations section
            story.extend(self._create_recommendations_section(analysis_results))
            story.append(PageBreak())
            
            # Environmental impact section
            story.extend(self._create_environmental_section(analysis_results))
            story.append(PageBreak())
            
            # Appendix
            story.extend(self._create_appendix(analysis_results))
            
            # Build PDF
            doc.build(story)
            
            # Reset buffer position
            buffer.seek(0)
            
            return buffer
            
        except Exception as e:
            self.logger.error(f"Report generation failed: {str(e)}")
            return self._create_error_report()
    
    def _create_title_page(self, results: Dict) -> list:
        """Create the title page of the report"""
        
        story = []
        
        # Main title
        story.append(Paragraph("Solar Rooftop Analysis Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.5*inch))
        
        # Property information table
        location = results.get('location', {})
        analysis_timestamp = results.get('analysis_timestamp', datetime.now())

        property_data = [
            ['Report Generated:', datetime.now().strftime('%B %d, %Y at %I:%M %p')],
            ['Location:', f"{location.get('latitude', 0):.4f}°, {location.get('longitude', 0):.4f}°"],
            ['Analysis Date:', analysis_timestamp.strftime('%B %d, %Y') if hasattr(analysis_timestamp, 'strftime') else str(analysis_timestamp)],
        ]
        
        property_table = Table(property_data, colWidths=[2*inch, 4*inch])
        property_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#EBF5FB')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#AED6F1'))
        ]))
        
        story.append(property_table)
        story.append(Spacer(1, 1*inch))
        
        # Key results summary
        story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        
        solar_potential = results['solar_potential']
        
        summary_data = [
            ['System Size:', f"{format_number(solar_potential['system_size_kw'])} kW"],
            ['Annual Energy Production:', f"{format_number(solar_potential['annual_energy_kwh'])} kWh"],
            ['Annual Savings:', format_currency(solar_potential['annual_savings'])],
            ['Payback Period:', f"{solar_potential['payback_years']:.1f} years"],
            ['25-Year ROI:', f"{solar_potential['roi_percent']:.1f}%"]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#E8F8F5')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#82E0AA'))
        ]))
        
        story.append(summary_table)
        
        return story
    
    def _create_executive_summary(self, results: Dict) -> list:
        """Create executive summary section"""
        
        story = []
        story.append(Paragraph("Executive Summary", self.styles['CustomTitle']))
        
        solar_results = results.get('solar_results', {})
        roof_analysis = results.get('roof_analysis', {})
        
        # Summary text
        summary_text = f"""
        This comprehensive solar analysis report evaluates the solar potential of your property 
        based on satellite imagery analysis and advanced calculations. Our AI-powered assessment 
        indicates that your roof has excellent potential for solar installation.
        
        <b>Key Findings:</b>
        
        • Your roof offers {format_number(roof_metrics['usable_area'])} m² of usable space for solar panels
        • The recommended system size is {format_number(solar_potential['system_size_kw'])} kW with 
        {solar_potential['panel_count']} solar panels
        • Expected annual energy production: {format_number(solar_potential['annual_energy_kwh'])} kWh
        • Estimated annual savings: {format_currency(solar_potential['annual_savings'])}
        • Simple payback period: {solar_potential['payback_years']:.1f} years
        • 25-year return on investment: {solar_potential['roi_percent']:.1f}%
        
        This analysis takes into account your roof's orientation ({roof_metrics['orientation']}), 
        slope ({roof_metrics['slope']:.1f}°), shading factors, and local solar irradiance data 
        from NASA's satellite measurements.
        """
        
        story.append(Paragraph(summary_text, self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Recommendation
        if solar_potential['payback_years'] <= 10:
            recommendation = "Strong Recommendation: This property is an excellent candidate for solar installation with attractive financial returns."
            rec_color = colors.HexColor('#27AE60')
        elif solar_potential['payback_years'] <= 15:
            recommendation = "Good Recommendation: This property shows good solar potential with reasonable payback period."
            rec_color = colors.HexColor('#F39C12')
        else:
            recommendation = "Moderate Recommendation: Solar installation is feasible but with longer payback period."
            rec_color = colors.HexColor('#E74C3C')
        
        rec_style = ParagraphStyle(
            name='Recommendation',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=rec_color,
            fontName='Helvetica-Bold',
            borderWidth=2,
            borderColor=rec_color,
            borderPadding=10,
            backColor=colors.HexColor('#F8F9FA')
        )
        
        story.append(Paragraph(recommendation, rec_style))
        
        return story
    
    def _create_roof_analysis_section(self, results: Dict) -> list:
        """Create roof analysis section"""
        
        story = []
        story.append(Paragraph("Roof Analysis", self.styles['CustomTitle']))
        
        roof_metrics = results['roof_metrics']
        
        # Roof characteristics table
        story.append(Paragraph("Roof Characteristics", self.styles['SectionHeader']))
        
        roof_data = [
            ['Characteristic', 'Value', 'Impact on Solar Potential'],
            ['Total Roof Area', f"{format_number(roof_metrics['total_area'])} m²", 'Determines maximum system size'],
            ['Usable Area', f"{format_number(roof_metrics['usable_area'])} m²", 'Available space for panels'],
            ['Primary Orientation', roof_metrics['orientation'].title(), self._get_orientation_impact(roof_metrics['orientation'])],
            ['Roof Slope', f"{roof_metrics['slope']:.1f}°", self._get_slope_impact(roof_metrics['slope'])],
            ['Shading Factor', f"{roof_metrics['shading_factor']:.2f}", self._get_shading_impact(roof_metrics['shading_factor'])],
            ['Obstructions', f"{roof_metrics['obstruction_count']} detected", 'May require design modifications']
        ]
        
        roof_table = Table(roof_data, colWidths=[2*inch, 1.5*inch, 2.5*inch])
        roof_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2874A6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#EBF5FB')),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#5DADE2'))
        ]))
        
        story.append(roof_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Analysis methodology
        story.append(Paragraph("Analysis Methodology", self.styles['SubsectionHeader']))
        
        methodology_text = """
        Our roof analysis utilizes advanced computer vision algorithms to process satellite imagery and extract key characteristics:
        
        • <b>Area Calculation:</b> Precise measurement of total and usable roof area using image segmentation
        • <b>Orientation Detection:</b> Algorithmic determination of roof facing direction for optimal panel placement
        • <b>Slope Estimation:</b> Analysis of roof pitch using shadow patterns and perspective calculations
        • <b>Shading Analysis:</b> Identification of shadows and potential shading sources throughout the day
        • <b>Obstruction Detection:</b> Automated detection of chimneys, vents, and other roof features
        
        This analysis provides the foundation for accurate solar potential calculations and system design recommendations.
        """
        
        story.append(Paragraph(methodology_text, self.styles['Normal']))
        
        return story
    
    def _create_solar_potential_section(self, results: Dict) -> list:
        """Create solar potential analysis section"""
        
        story = []
        story.append(Paragraph("Solar Energy Potential", self.styles['CustomTitle']))
        
        solar_potential = results['solar_potential']
        solar_data = results['solar_data']
        
        # System specifications
        story.append(Paragraph("Recommended System Specifications", self.styles['SectionHeader']))
        
        system_data = [
            ['Specification', 'Value'],
            ['System Size', f"{format_number(solar_potential['system_size_kw'])} kW"],
            ['Number of Panels', f"{solar_potential['panel_count']} panels"],
            ['Panel Type', results['panel_type'].title()],
            ['Panel Power Rating', f"{solar_potential['system_specifications']['panel_power']} W each"],
            ['Panel Efficiency', f"{solar_potential['system_specifications']['panel_efficiency']*100:.1f}%"],
            ['System Capacity Factor', f"{solar_potential['capacity_factor']*100:.1f}%"]
        ]
        
        system_table = Table(system_data, colWidths=[3*inch, 2*inch])
        system_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E67E22')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FEF9E7')),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#F7DC6F'))
        ]))
        
        story.append(system_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Energy production
        story.append(Paragraph("Energy Production Estimates", self.styles['SectionHeader']))
        
        energy_data = [
            ['Period', 'Energy Production (kWh)'],
            ['Daily Average', f"{format_number(solar_potential['daily_energy_kwh'])}"],
            ['Monthly Average', f"{format_number(solar_potential['monthly_energy_kwh'])}"],
            ['Annual Total', f"{format_number(solar_potential['annual_energy_kwh'])}"],
            ['25-Year Lifetime', f"{format_number(solar_potential['annual_energy_kwh'] * 25)}"]
        ]
        
        energy_table = Table(energy_data, colWidths=[3*inch, 2*inch])
        energy_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27AE60')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#E8F8F5')),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#82E0AA'))
        ]))
        
        story.append(energy_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Solar resource data
        story.append(Paragraph("Solar Resource Data", self.styles['SubsectionHeader']))
        
        solar_resource_text = f"""
        The energy production estimates are based on NASA satellite data for your location:
        
        • <b>Annual Solar Irradiance:</b> {format_number(solar_data['annual_irradiance'])} kWh/m²/year
        • <b>Data Quality:</b> {solar_data['data_quality'].title()}
        • <b>Seasonal Variation:</b> {solar_data['seasonal_variation']*100:.1f}% between peak and minimum months
        • <b>Data Source:</b> {solar_data['data_source']}
        
        These calculations include system losses for inverter efficiency, DC/AC conversion, 
        soiling, and other real-world factors that affect solar panel performance.
        """
        
        story.append(Paragraph(solar_resource_text, self.styles['Normal']))
        
        return story
    
    def _create_financial_analysis_section(self, results: Dict) -> list:
        """Create financial analysis section"""
        
        story = []
        story.append(Paragraph("Financial Analysis", self.styles['CustomTitle']))
        
        solar_potential = results['solar_potential']
        
        # Cost breakdown
        story.append(Paragraph("Investment Summary", self.styles['SectionHeader']))
        
        cost_data = [
            ['Cost Component', 'Amount'],
            ['Total System Cost', format_currency(solar_potential['total_cost'])],
            ['Federal Tax Credit (30%)', f"-{format_currency(solar_potential['federal_incentive'])}"],
            ['Net Investment', format_currency(solar_potential['net_cost'])],
            ['Cost per Watt', f"${solar_potential['cost_per_watt']:.2f}/W"]
        ]
        
        cost_table = Table(cost_data, colWidths=[3*inch, 2*inch])
        cost_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8E44AD')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F4ECF7')),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BB8FCE'))
        ]))
        
        story.append(cost_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Savings and returns
        story.append(Paragraph("Savings and Returns", self.styles['SectionHeader']))
        
        savings_data = [
            ['Financial Metric', 'Value'],
            ['Annual Electricity Savings', format_currency(solar_potential['annual_savings'])],
            ['Monthly Savings (Year 1)', format_currency(solar_potential['monthly_savings'])],
            ['Simple Payback Period', f"{solar_potential['payback_years']:.1f} years"],
            ['25-Year Total Savings', format_currency(solar_potential['lifetime_savings'])],
            ['Return on Investment (25-year)', f"{solar_potential['roi_percent']:.1f}%"]
        ]
        
        savings_table = Table(savings_data, colWidths=[3*inch, 2*inch])
        savings_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D35400')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FDEAA7')),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#F8C471'))
        ]))
        
        story.append(savings_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Financial assumptions
        story.append(Paragraph("Financial Assumptions", self.styles['SubsectionHeader']))
        
        assumptions_text = f"""
        The financial analysis is based on the following assumptions:
        
        • <b>Electricity Rate:</b> ${results['electricity_rate']:.3f} per kWh
        • <b>Annual Rate Increase:</b> 3% per year (industry average)
        • <b>Federal Tax Credit:</b> 30% of system cost (current rate through 2032)
        • <b>System Degradation:</b> 0.5% per year (industry standard)
        • <b>Analysis Period:</b> 25 years (typical solar panel warranty period)
        
        These calculations assume net metering is available, allowing excess energy 
        to be sold back to the utility at retail rates. Actual savings may vary 
        based on local utility policies and rate structures.
        """
        
        story.append(Paragraph(assumptions_text, self.styles['Normal']))
        
        return story
    
    def _create_recommendations_section(self, results: Dict) -> list:
        """Create AI recommendations section"""
        
        story = []
        story.append(Paragraph("AI-Generated Recommendations", self.styles['CustomTitle']))
        
        recommendations = results['recommendations']
        
        # Installation plan
        if 'installation_plan' in recommendations:
            story.append(Paragraph("Installation Plan", self.styles['SectionHeader']))
            story.append(Paragraph(recommendations['installation_plan'], self.styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Optimization tips
        if 'optimization_tips' in recommendations:
            story.append(Paragraph("System Optimization", self.styles['SectionHeader']))
            story.append(Paragraph(recommendations['optimization_tips'], self.styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Compliance information
        if 'compliance_info' in recommendations:
            story.append(Paragraph("Regulatory Compliance", self.styles['SectionHeader']))
            story.append(Paragraph(recommendations['compliance_info'], self.styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Maintenance plan
        if 'maintenance_plan' in recommendations:
            story.append(Paragraph("Maintenance Guidelines", self.styles['SectionHeader']))
            story.append(Paragraph(recommendations['maintenance_plan'], self.styles['Normal']))
        
        return story
    
    def _create_environmental_section(self, results: Dict) -> list:
        """Create environmental impact section"""
        
        story = []
        story.append(Paragraph("Environmental Impact", self.styles['CustomTitle']))
        
        solar_potential = results['solar_potential']
        
        # Environmental benefits table
        story.append(Paragraph("Environmental Benefits", self.styles['SectionHeader']))
        
        env_data = [
            ['Environmental Metric', 'Annual Impact', '25-Year Impact'],
            ['CO₂ Emissions Offset', 
             f"{format_number(solar_potential['annual_co2_offset_tons'])} tons", 
             f"{format_number(solar_potential['lifetime_co2_offset_tons'])} tons"],
            ['Equivalent Trees Planted', 
             f"{format_number(solar_potential['equivalent_trees_planted'])} trees", 
             f"{format_number(solar_potential['equivalent_trees_planted'] * 25)} trees"],
            ['Equivalent Cars Removed', 
             f"{solar_potential['equivalent_cars_removed']:.1f} cars", 
             f"{solar_potential['equivalent_cars_removed'] * 25:.1f} cars"]
        ]
        
        env_table = Table(env_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
        env_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27AE60')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#E8F8F5')),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#82E0AA'))
        ]))
        
        story.append(env_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Environmental impact explanation
        impact_text = """
        Your solar installation will have significant positive environmental impacts:
        
        <b>Climate Benefits:</b> By generating clean, renewable energy, your solar system 
        will offset thousands of pounds of CO₂ emissions annually. Over its 25-year lifetime, 
        the system will prevent the equivalent emissions of burning thousands of pounds of coal.
        
        <b>Air Quality:</b> Solar energy production creates no air pollutants, contributing 
        to cleaner air in your community and reducing health impacts associated with 
        fossil fuel combustion.
        
        <b>Resource Conservation:</b> Solar energy requires no water for operation, unlike 
        traditional power plants that consume billions of gallons annually for cooling.
        
        <b>Sustainability:</b> Your investment in solar energy supports the transition to 
        a sustainable energy future and helps drive down costs for renewable energy technology.
        """
        
        story.append(Paragraph(impact_text, self.styles['Normal']))
        
        return story
    
    def _create_appendix(self, results: Dict) -> list:
        """Create appendix with technical details"""
        
        story = []
        story.append(Paragraph("Technical Appendix", self.styles['CustomTitle']))
        
        # Analysis metadata
        story.append(Paragraph("Analysis Details", self.styles['SectionHeader']))
        
        metadata_text = f"""
        <b>Report Generation:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
        
        <b>Analysis Confidence:</b> {results['roof_metrics']['confidence_score']*100:.1f}%
        
        <b>Data Sources:</b>
        • Roof Analysis: Computer vision processing of satellite imagery
        • Solar Data: {results['solar_data']['data_source']}
        • Financial Calculations: Industry-standard methodologies
        • AI Recommendations: Google LLM API integration
        
        <b>System Losses Included:</b>
        • Inverter Efficiency: {results['solar_potential']['system_specifications']['system_losses']['inverter_efficiency']*100:.1f}%
        • DC System Losses: {results['solar_potential']['system_specifications']['system_losses']['dc_losses']*100:.1f}%
        • AC System Losses: {results['solar_potential']['system_specifications']['system_losses']['ac_losses']*100:.1f}%
        • Soiling Losses: {results['solar_potential']['system_specifications']['system_losses']['soiling_losses']*100:.1f}%
        
        <b>Disclaimer:</b> This analysis is based on satellite imagery and modeled data. 
        Actual results may vary based on site-specific conditions, local regulations, 
        utility policies, and installation quality. A professional site assessment 
        is recommended before proceeding with installation.
        """
        
        story.append(Paragraph(metadata_text, self.styles['Normal']))
        
        return story
    
    def _get_orientation_impact(self, orientation: str) -> str:
        """Get impact description for roof orientation"""
        
        impacts = {
            'south': 'Optimal for solar production',
            'southeast': 'Excellent for solar production',
            'southwest': 'Excellent for solar production',
            'east': 'Good for morning production',
            'west': 'Good for afternoon production',
            'northeast': 'Moderate solar potential',
            'northwest': 'Moderate solar potential',
            'north': 'Limited solar potential'
        }
        
        return impacts.get(orientation.lower(), 'Variable impact')
    
    def _get_slope_impact(self, slope: float) -> str:
        """Get impact description for roof slope"""
        
        if slope < 10:
            return 'May require ballasted mounting'
        elif slope <= 30:
            return 'Optimal for solar installation'
        elif slope <= 45:
            return 'Good for solar, may need special mounting'
        else:
            return 'Steep roof, special mounting required'
    
    def _get_shading_impact(self, shading_factor: float) -> str:
        """Get impact description for shading"""
        
        if shading_factor < 0.1:
            return 'Minimal impact on production'
        elif shading_factor < 0.3:
            return 'Some reduction in production'
        elif shading_factor < 0.5:
            return 'Moderate impact, consider mitigation'
        else:
            return 'Significant impact, mitigation required'
    
    def _create_error_report(self) -> io.BytesIO:
        """Create a simple error report when generation fails"""
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        
        story = [
            Paragraph("Solar Analysis Report", self.styles['Title']),
            Spacer(1, 0.5*inch),
            Paragraph("Report Generation Error", self.styles['Heading1']),
            Paragraph(
                "An error occurred while generating your solar analysis report. "
                "Please try again or contact support if the problem persists.",
                self.styles['Normal']
            )
        ]
        
        doc.build(story)
        buffer.seek(0)
        return buffer
