// PDF Generator Module for Solar AI Platform
class PDFGenerator {
    constructor() {
        this.isJsPDFReady = false;
        this.initJsPDF();
    }

    initJsPDF() {
        try {
            if (typeof window.jsPDF !== 'undefined') {
                this.isJsPDFReady = true;
                console.log('✅ jsPDF ready');
            } else {
                console.log('⚠️ jsPDF not available');
                this.isJsPDFReady = false;
            }
        } catch (error) {
            console.error('Failed to initialize jsPDF:', error);
            this.isJsPDFReady = false;
        }
    }

    async generateReport(roofAnalysis, solarResults, aiRecommendations, config) {
        if (!this.isJsPDFReady) {
            throw new Error('PDF generation not available. Please check if jsPDF is loaded.');
        }

        try {
            const doc = new window.jsPDF.jsPDF();
            
            // Set up document properties
            doc.setProperties({
                title: 'Solar Analysis Report',
                subject: 'Solar Rooftop Analysis',
                author: 'Solar AI Platform',
                creator: 'Solar AI Platform'
            });

            let yPosition = 20;

            // Header
            yPosition = this.addHeader(doc, yPosition);
            
            // Executive Summary
            yPosition = this.addExecutiveSummary(doc, yPosition, roofAnalysis, solarResults);
            
            // Roof Analysis Section
            yPosition = this.addRoofAnalysis(doc, yPosition, roofAnalysis);
            
            // Solar System Specifications
            yPosition = this.addSystemSpecs(doc, yPosition, solarResults, config);
            
            // Financial Analysis
            yPosition = this.addFinancialAnalysis(doc, yPosition, solarResults);
            
            // Environmental Impact
            yPosition = this.addEnvironmentalImpact(doc, yPosition, solarResults);
            
            // AI Recommendations
            if (aiRecommendations && aiRecommendations.recommendations) {
                yPosition = this.addAIRecommendations(doc, yPosition, aiRecommendations);
            }
            
            // Footer
            this.addFooter(doc);
            
            // Generate filename
            const timestamp = new Date().toISOString().slice(0, 10);
            const filename = `solar_analysis_report_${timestamp}.pdf`;
            
            // Download the PDF
            doc.save(filename);
            
            return {
                success: true,
                filename: filename,
                message: 'PDF report generated successfully'
            };
            
        } catch (error) {
            console.error('PDF generation failed:', error);
            throw new Error(`Failed to generate PDF: ${error.message}`);
        }
    }

    addHeader(doc, yPosition) {
        // Title
        doc.setFontSize(24);
        doc.setTextColor(0, 100, 200);
        doc.text('🌞 Solar Analysis Report', 20, yPosition);
        
        yPosition += 15;
        
        // Subtitle
        doc.setFontSize(12);
        doc.setTextColor(100, 100, 100);
        doc.text('AI-Powered Solar Rooftop Analysis', 20, yPosition);
        
        yPosition += 10;
        
        // Date
        doc.setFontSize(10);
        doc.setTextColor(150, 150, 150);
        const currentDate = new Date().toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
        doc.text(`Generated: ${currentDate}`, 20, yPosition);
        
        yPosition += 20;
        
        // Horizontal line
        doc.setDrawColor(200, 200, 200);
        doc.line(20, yPosition, 190, yPosition);
        
        return yPosition + 15;
    }

    addExecutiveSummary(doc, yPosition, roofAnalysis, solarResults) {
        yPosition = this.checkPageBreak(doc, yPosition, 60);
        
        doc.setFontSize(16);
        doc.setTextColor(0, 0, 0);
        doc.text('Executive Summary', 20, yPosition);
        
        yPosition += 10;
        
        doc.setFontSize(10);
        doc.setTextColor(80, 80, 80);
        
        const summary = [
            `Your roof offers ${roofAnalysis.usable_area.toFixed(0)} m² of usable space for solar panels.`,
            `The recommended system size is ${solarResults.system_size_kw} kW with ${solarResults.panel_count} solar panels.`,
            `Expected annual energy production: ${solarResults.annual_energy_kwh.toLocaleString()} kWh`,
            `Estimated annual savings: $${solarResults.annual_savings.toLocaleString()}`,
            `Simple payback period: ${solarResults.payback_years} years`,
            `25-year return on investment: ${solarResults.roi_percent}%`
        ];
        
        summary.forEach(line => {
            doc.text(`• ${line}`, 25, yPosition);
            yPosition += 6;
        });
        
        return yPosition + 10;
    }

    addRoofAnalysis(doc, yPosition, roofAnalysis) {
        yPosition = this.checkPageBreak(doc, yPosition, 50);
        
        doc.setFontSize(14);
        doc.setTextColor(0, 0, 0);
        doc.text('Roof Characteristics', 20, yPosition);
        
        yPosition += 10;
        
        doc.setFontSize(10);
        doc.setTextColor(80, 80, 80);
        
        const roofData = [
            ['Total Area:', `${(roofAnalysis.total_area || roofAnalysis.usable_area * 1.2).toFixed(0)} m²`],
            ['Usable Area:', `${roofAnalysis.usable_area.toFixed(0)} m²`],
            ['Orientation:', roofAnalysis.orientation],
            ['Slope:', `${roofAnalysis.slope.toFixed(1)}°`],
            ['Shading Factor:', `${(roofAnalysis.shading_factor * 100).toFixed(1)}%`],
            ['Roof Type:', roofAnalysis.roof_type || 'Standard']
        ];
        
        roofData.forEach(([label, value]) => {
            doc.text(label, 25, yPosition);
            doc.text(value, 80, yPosition);
            yPosition += 6;
        });
        
        return yPosition + 10;
    }

    addSystemSpecs(doc, yPosition, solarResults, config) {
        yPosition = this.checkPageBreak(doc, yPosition, 50);
        
        doc.setFontSize(14);
        doc.setTextColor(0, 0, 0);
        doc.text('Solar System Specifications', 20, yPosition);
        
        yPosition += 10;
        
        doc.setFontSize(10);
        doc.setTextColor(80, 80, 80);
        
        const systemData = [
            ['System Size:', `${solarResults.system_size_kw} kW`],
            ['Panel Count:', `${solarResults.panel_count} panels`],
            ['Panel Type:', config.panelType.charAt(0).toUpperCase() + config.panelType.slice(1)],
            ['Annual Production:', `${solarResults.annual_energy_kwh.toLocaleString()} kWh`],
            ['Monthly Production:', `${solarResults.monthly_energy_kwh.toLocaleString()} kWh`],
            ['Daily Production:', `${solarResults.daily_energy_kwh} kWh`],
            ['Capacity Factor:', `${solarResults.capacity_factor}%`]
        ];
        
        systemData.forEach(([label, value]) => {
            doc.text(label, 25, yPosition);
            doc.text(value, 80, yPosition);
            yPosition += 6;
        });
        
        return yPosition + 10;
    }

    addFinancialAnalysis(doc, yPosition, solarResults) {
        yPosition = this.checkPageBreak(doc, yPosition, 50);
        
        doc.setFontSize(14);
        doc.setTextColor(0, 0, 0);
        doc.text('Financial Analysis', 20, yPosition);
        
        yPosition += 10;
        
        doc.setFontSize(10);
        doc.setTextColor(80, 80, 80);
        
        const financialData = [
            ['Total System Cost:', `$${solarResults.total_cost.toLocaleString()}`],
            ['Annual Savings:', `$${solarResults.annual_savings.toLocaleString()}`],
            ['Payback Period:', `${solarResults.payback_years} years`],
            ['25-Year Savings:', `$${solarResults.lifetime_savings.toLocaleString()}`],
            ['Return on Investment:', `${solarResults.roi_percent}%`]
        ];
        
        financialData.forEach(([label, value]) => {
            doc.text(label, 25, yPosition);
            doc.text(value, 80, yPosition);
            yPosition += 6;
        });
        
        return yPosition + 10;
    }

    addEnvironmentalImpact(doc, yPosition, solarResults) {
        yPosition = this.checkPageBreak(doc, yPosition, 40);
        
        doc.setFontSize(14);
        doc.setTextColor(0, 0, 0);
        doc.text('Environmental Impact', 20, yPosition);
        
        yPosition += 10;
        
        doc.setFontSize(10);
        doc.setTextColor(80, 80, 80);
        
        const environmentalData = [
            ['Annual CO₂ Offset:', `${solarResults.co2_offset_kg.toLocaleString()} kg`],
            ['Equivalent Trees Planted:', `${solarResults.trees_equivalent} trees`],
            ['25-Year CO₂ Offset:', `${(solarResults.co2_offset_kg * 25).toLocaleString()} kg`]
        ];
        
        environmentalData.forEach(([label, value]) => {
            doc.text(label, 25, yPosition);
            doc.text(value, 80, yPosition);
            yPosition += 6;
        });
        
        return yPosition + 10;
    }

    addAIRecommendations(doc, yPosition, aiRecommendations) {
        yPosition = this.checkPageBreak(doc, yPosition, 60);
        
        doc.setFontSize(14);
        doc.setTextColor(0, 0, 0);
        doc.text('AI Recommendations', 20, yPosition);
        
        yPosition += 10;
        
        doc.setFontSize(9);
        doc.setTextColor(80, 80, 80);
        
        aiRecommendations.recommendations.forEach((recommendation, index) => {
            yPosition = this.checkPageBreak(doc, yPosition, 25);
            
            // Category header
            doc.setFontSize(10);
            doc.setTextColor(0, 100, 200);
            doc.text(`${recommendation.icon} ${recommendation.category}`, 25, yPosition);
            
            yPosition += 6;
            
            // Content
            doc.setFontSize(9);
            doc.setTextColor(80, 80, 80);
            
            const lines = doc.splitTextToSize(recommendation.content, 160);
            lines.forEach(line => {
                yPosition = this.checkPageBreak(doc, yPosition, 5);
                doc.text(line, 30, yPosition);
                yPosition += 4;
            });
            
            yPosition += 5;
        });
        
        return yPosition + 10;
    }

    addFooter(doc) {
        const pageCount = doc.internal.getNumberOfPages();
        
        for (let i = 1; i <= pageCount; i++) {
            doc.setPage(i);
            
            // Footer line
            doc.setDrawColor(200, 200, 200);
            doc.line(20, 280, 190, 280);
            
            // Footer text
            doc.setFontSize(8);
            doc.setTextColor(150, 150, 150);
            doc.text('Solar AI Platform - AI-Powered Solar Analysis', 20, 285);
            doc.text(`Page ${i} of ${pageCount}`, 170, 285);
            
            // Disclaimer
            if (i === pageCount) {
                doc.setFontSize(7);
                doc.setTextColor(100, 100, 100);
                const disclaimer = 'This analysis is based on satellite imagery and modeled data. Actual results may vary based on site-specific conditions, local regulations, utility policies, and installation quality. A professional site assessment is recommended before proceeding with installation.';
                const disclaimerLines = doc.splitTextToSize(disclaimer, 170);
                let disclaimerY = 290;
                disclaimerLines.forEach(line => {
                    doc.text(line, 20, disclaimerY);
                    disclaimerY += 3;
                });
            }
        }
    }

    checkPageBreak(doc, yPosition, requiredSpace) {
        if (yPosition + requiredSpace > 270) {
            doc.addPage();
            return 20;
        }
        return yPosition;
    }

    // Utility method to check if PDF generation is available
    isAvailable() {
        return this.isJsPDFReady;
    }

    // Method to generate a simple fallback report if jsPDF is not available
    generateFallbackReport(roofAnalysis, solarResults, aiRecommendations, config) {
        const reportData = {
            timestamp: new Date().toISOString(),
            roofAnalysis: roofAnalysis,
            solarResults: solarResults,
            aiRecommendations: aiRecommendations,
            config: config
        };
        
        const dataStr = JSON.stringify(reportData, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `solar_analysis_${new Date().toISOString().slice(0, 10)}.json`;
        link.click();
        
        return {
            success: true,
            filename: link.download,
            message: 'Analysis data exported as JSON file'
        };
    }
}

// Export for use in other modules
window.PDFGenerator = PDFGenerator;
