// PDF Generator Module for Solar AI Platform
class PDFGenerator {
    constructor() {
        this.isJsPDFReady = false;
        this.initJsPDF();
    }

    initJsPDF() {
        try {
            // Check for jsPDF in multiple possible locations
            if (typeof window.jsPDF !== 'undefined') {
                this.jsPDF = window.jsPDF;
                this.isJsPDFReady = true;
                console.log('✅ jsPDF ready (window.jsPDF)');
            } else if (typeof window.jspdf !== 'undefined' && window.jspdf.jsPDF) {
                this.jsPDF = window.jspdf.jsPDF;
                this.isJsPDFReady = true;
                console.log('✅ jsPDF ready (window.jspdf.jsPDF)');
            } else if (typeof jsPDF !== 'undefined') {
                this.jsPDF = jsPDF;
                this.isJsPDFReady = true;
                console.log('✅ jsPDF ready (global jsPDF)');
            } else {
                console.log('⚠️ jsPDF not available, will use fallback');
                this.isJsPDFReady = false;
            }
        } catch (error) {
            console.error('Failed to initialize jsPDF:', error);
            this.isJsPDFReady = false;
        }
    }

    async generateReport(roofAnalysis, solarResults, aiRecommendations, config, visualMarkup = null) {
        if (!this.isJsPDFReady) {
            console.warn('jsPDF not available, using fallback method');
            return this.generateFallbackReport(roofAnalysis, solarResults, aiRecommendations, config);
        }

        try {
            // Create new PDF document
            const doc = new this.jsPDF({
                orientation: 'portrait',
                unit: 'mm',
                format: 'a4'
            });

            // Set up document properties
            doc.setProperties({
                title: 'Solar Analysis Report',
                subject: 'Solar Rooftop Analysis',
                author: 'Solar AI Platform',
                creator: 'Solar AI Platform',
                keywords: 'solar, analysis, renewable energy, AI'
            });

            let yPosition = 20;

            // Header with branding
            yPosition = this.addEnhancedHeader(doc, yPosition);

            // Executive Summary
            yPosition = this.addExecutiveSummary(doc, yPosition, roofAnalysis, solarResults);

            // Visual Markup Images (if available)
            if (visualMarkup) {
                yPosition = this.addVisualMarkupSection(doc, yPosition, visualMarkup);
            }

            // Roof Analysis Section
            yPosition = this.addRoofAnalysis(doc, yPosition, roofAnalysis);

            // Solar System Specifications
            yPosition = this.addSystemSpecs(doc, yPosition, solarResults, config);

            // Financial Analysis with Charts
            yPosition = this.addEnhancedFinancialAnalysis(doc, yPosition, solarResults);

            // Environmental Impact
            yPosition = this.addEnvironmentalImpact(doc, yPosition, solarResults);

            // AI Recommendations
            if (aiRecommendations && aiRecommendations.recommendations) {
                yPosition = this.addAIRecommendations(doc, yPosition, aiRecommendations);
            }

            // Technical Specifications
            yPosition = this.addTechnicalSpecifications(doc, yPosition, roofAnalysis, solarResults);

            // Footer with page numbers
            this.addEnhancedFooter(doc);

            // Generate filename with timestamp
            const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
            const filename = `Solar_Analysis_Report_${timestamp}.pdf`;

            // Save the PDF
            doc.save(filename);

            console.log(`✅ PDF report generated: ${filename}`);

            return {
                success: true,
                filename: filename,
                message: 'Professional PDF report generated successfully',
                pages: doc.internal.getNumberOfPages(),
                fileSize: 'Estimated 2-5 MB'
            };

        } catch (error) {
            console.error('PDF generation failed:', error);
            console.warn('Falling back to JSON export');
            return this.generateFallbackReport(roofAnalysis, solarResults, aiRecommendations, config);
        }
    }

    addEnhancedHeader(doc, yPosition) {
        // Background header box
        doc.setFillColor(0, 50, 100);
        doc.rect(10, 10, 190, 40, 'F');

        // Title
        doc.setFontSize(28);
        doc.setTextColor(255, 255, 255);
        doc.setFont('helvetica', 'bold');
        doc.text('Solar Analysis Report', 105, 25, { align: 'center' });

        // Subtitle
        doc.setFontSize(14);
        doc.setTextColor(200, 230, 255);
        doc.setFont('helvetica', 'normal');
        doc.text('AI-Powered Solar Rooftop Analysis', 105, 35, { align: 'center' });

        // Professional badge
        doc.setFontSize(10);
        doc.setTextColor(255, 255, 255);
        doc.text('PROFESSIONAL ANALYSIS', 105, 45, { align: 'center' });

        yPosition = 60;

        // Date and report info
        doc.setFontSize(10);
        doc.setTextColor(100, 100, 100);
        const currentDate = new Date().toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
        doc.text(`Generated: ${currentDate}`, 20, yPosition);
        doc.text('Report ID: ' + Math.random().toString(36).substr(2, 9).toUpperCase(), 140, yPosition);

        yPosition += 15;

        // Decorative line
        doc.setDrawColor(0, 150, 255);
        doc.setLineWidth(1);
        doc.line(20, yPosition, 190, yPosition);

        return yPosition + 10;
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

    addVisualMarkupSection(doc, yPosition, visualMarkup) {
        yPosition = this.checkPageBreak(doc, yPosition, 80);

        // Section header
        doc.setFontSize(16);
        doc.setTextColor(0, 100, 200);
        doc.setFont('helvetica', 'bold');
        doc.text('Visual Analysis & Panel Placement', 20, yPosition);

        yPosition += 15;

        // Add visual markup images
        const images = [
            { key: 'overview', title: 'Full Roof Overview' },
            { key: 'detailed', title: 'Primary Installation Area' }
        ];

        for (const img of images) {
            if (visualMarkup[img.key] && visualMarkup[img.key].dataUrl) {
                yPosition = this.checkPageBreak(doc, yPosition, 70);

                // Image title
                doc.setFontSize(12);
                doc.setTextColor(0, 0, 0);
                doc.setFont('helvetica', 'bold');
                doc.text(img.title, 20, yPosition);
                yPosition += 8;

                try {
                    // Add image to PDF
                    doc.addImage(
                        visualMarkup[img.key].dataUrl,
                        'PNG',
                        20,
                        yPosition,
                        170,
                        60
                    );
                    yPosition += 65;

                    // Image description
                    doc.setFontSize(10);
                    doc.setTextColor(80, 80, 80);
                    doc.setFont('helvetica', 'normal');
                    doc.text(visualMarkup[img.key].description || '', 20, yPosition);
                    yPosition += 10;

                } catch (error) {
                    console.warn('Failed to add image to PDF:', error);
                    doc.setFontSize(10);
                    doc.setTextColor(150, 150, 150);
                    doc.text('[Visual markup image - see web interface]', 20, yPosition);
                    yPosition += 15;
                }
            }
        }

        return yPosition + 10;
    }

    addEnhancedFinancialAnalysis(doc, yPosition, solarResults) {
        yPosition = this.checkPageBreak(doc, yPosition, 80);

        // Section header
        doc.setFontSize(16);
        doc.setTextColor(0, 100, 200);
        doc.setFont('helvetica', 'bold');
        doc.text('Financial Analysis', 20, yPosition);

        yPosition += 15;

        // Key metrics in boxes
        const metrics = [
            { label: 'Total Investment', value: `$${solarResults.total_cost.toLocaleString()}`, color: [255, 100, 100] },
            { label: 'Annual Savings', value: `$${solarResults.annual_savings.toLocaleString()}`, color: [100, 255, 100] },
            { label: 'Payback Period', value: `${solarResults.payback_years} years`, color: [100, 150, 255] },
            { label: 'ROI', value: `${solarResults.roi_percent}%`, color: [255, 200, 100] }
        ];

        const boxWidth = 40;
        const boxHeight = 25;
        const startX = 20;

        metrics.forEach((metric, index) => {
            const x = startX + (index * (boxWidth + 5));

            // Box background
            doc.setFillColor(metric.color[0], metric.color[1], metric.color[2]);
            doc.setDrawColor(0, 0, 0);
            doc.rect(x, yPosition, boxWidth, boxHeight, 'FD');

            // Value
            doc.setFontSize(14);
            doc.setTextColor(0, 0, 0);
            doc.setFont('helvetica', 'bold');
            doc.text(metric.value, x + boxWidth/2, yPosition + 12, { align: 'center' });

            // Label
            doc.setFontSize(8);
            doc.setTextColor(0, 0, 0);
            doc.setFont('helvetica', 'normal');
            doc.text(metric.label, x + boxWidth/2, yPosition + 20, { align: 'center' });
        });

        yPosition += 35;

        // Detailed breakdown
        doc.setFontSize(12);
        doc.setTextColor(0, 0, 0);
        doc.setFont('helvetica', 'bold');
        doc.text('Financial Breakdown:', 20, yPosition);
        yPosition += 10;

        const financialData = [
            ['System Cost:', `$${solarResults.total_cost.toLocaleString()}`, 'Total upfront investment'],
            ['Annual Savings:', `$${solarResults.annual_savings.toLocaleString()}`, 'Yearly electricity bill reduction'],
            ['25-Year Savings:', `$${solarResults.lifetime_savings.toLocaleString()}`, 'Total lifetime savings'],
            ['Monthly Savings:', `$${Math.round(solarResults.annual_savings / 12).toLocaleString()}`, 'Average monthly reduction'],
            ['Break-even Point:', `${solarResults.payback_years} years`, 'When system pays for itself']
        ];

        doc.setFontSize(10);
        doc.setFont('helvetica', 'normal');

        financialData.forEach(([label, value, description]) => {
            doc.setTextColor(0, 0, 0);
            doc.text(label, 25, yPosition);
            doc.setTextColor(0, 100, 0);
            doc.setFont('helvetica', 'bold');
            doc.text(value, 80, yPosition);
            doc.setTextColor(100, 100, 100);
            doc.setFont('helvetica', 'normal');
            doc.text(description, 130, yPosition);
            yPosition += 8;
        });

        return yPosition + 15;
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

    addTechnicalSpecifications(doc, yPosition, roofAnalysis, solarResults) {
        yPosition = this.checkPageBreak(doc, yPosition, 60);

        // Section header
        doc.setFontSize(16);
        doc.setTextColor(0, 100, 200);
        doc.setFont('helvetica', 'bold');
        doc.text('Technical Specifications', 20, yPosition);

        yPosition += 15;

        // Two-column layout
        const col1X = 20;
        const col2X = 110;
        let col1Y = yPosition;
        let col2Y = yPosition;

        // Column 1: System Specifications
        doc.setFontSize(12);
        doc.setTextColor(0, 0, 0);
        doc.setFont('helvetica', 'bold');
        doc.text('System Specifications:', col1X, col1Y);
        col1Y += 8;

        const systemSpecs = [
            ['System Size:', `${solarResults.system_size_kw} kW`],
            ['Panel Count:', `${solarResults.panel_count} panels`],
            ['Annual Production:', `${solarResults.annual_energy_kwh.toLocaleString()} kWh`],
            ['Capacity Factor:', `${solarResults.capacity_factor}%`],
            ['Daily Average:', `${solarResults.daily_energy_kwh} kWh`]
        ];

        doc.setFontSize(9);
        doc.setFont('helvetica', 'normal');
        systemSpecs.forEach(([label, value]) => {
            doc.setTextColor(80, 80, 80);
            doc.text(label, col1X, col1Y);
            doc.setTextColor(0, 0, 0);
            doc.text(value, col1X + 35, col1Y);
            col1Y += 6;
        });

        // Column 2: Roof Characteristics
        doc.setFontSize(12);
        doc.setTextColor(0, 0, 0);
        doc.setFont('helvetica', 'bold');
        doc.text('Roof Characteristics:', col2X, col2Y);
        col2Y += 8;

        const roofSpecs = [
            ['Usable Area:', `${roofAnalysis.usable_area.toFixed(0)} m²`],
            ['Orientation:', roofAnalysis.orientation],
            ['Slope:', `${roofAnalysis.slope.toFixed(1)}°`],
            ['Shading Factor:', `${(roofAnalysis.shading_factor * 100).toFixed(1)}%`],
            ['Roof Type:', roofAnalysis.roof_type || 'Standard']
        ];

        doc.setFontSize(9);
        doc.setFont('helvetica', 'normal');
        roofSpecs.forEach(([label, value]) => {
            doc.setTextColor(80, 80, 80);
            doc.text(label, col2X, col2Y);
            doc.setTextColor(0, 0, 0);
            doc.text(value, col2X + 35, col2Y);
            col2Y += 6;
        });

        return Math.max(col1Y, col2Y) + 10;
    }

    addEnhancedFooter(doc) {
        const pageCount = doc.internal.getNumberOfPages();

        for (let i = 1; i <= pageCount; i++) {
            doc.setPage(i);

            // Footer background
            doc.setFillColor(240, 240, 240);
            doc.rect(10, 275, 190, 20, 'F');

            // Footer line
            doc.setDrawColor(0, 150, 255);
            doc.setLineWidth(0.5);
            doc.line(20, 275, 190, 275);

            // Footer content
            doc.setFontSize(9);
            doc.setTextColor(0, 100, 200);
            doc.setFont('helvetica', 'bold');
            doc.text('Solar AI Platform', 20, 282);

            doc.setFontSize(8);
            doc.setTextColor(100, 100, 100);
            doc.setFont('helvetica', 'normal');
            doc.text('AI-Powered Solar Analysis & Recommendations', 20, 287);

            // Page numbers
            doc.setFontSize(9);
            doc.setTextColor(0, 0, 0);
            doc.text(`Page ${i} of ${pageCount}`, 170, 285);

            // Disclaimer on last page
            if (i === pageCount) {
                yPosition = 300;
                doc.setFontSize(7);
                doc.setTextColor(100, 100, 100);
                doc.setFont('helvetica', 'normal');

                const disclaimer = 'DISCLAIMER: This analysis is based on satellite imagery, AI modeling, and estimated data. Actual results may vary based on site-specific conditions, local regulations, utility policies, equipment specifications, and installation quality. This report is for informational purposes only and should not be considered as professional engineering advice. A professional site assessment by qualified solar installers is strongly recommended before proceeding with any solar installation. The Solar AI Platform and its operators are not responsible for any decisions made based on this analysis.';

                const disclaimerLines = doc.splitTextToSize(disclaimer, 170);
                disclaimerLines.forEach(line => {
                    if (yPosition > 290) {
                        doc.addPage();
                        yPosition = 20;
                    }
                    doc.text(line, 20, yPosition);
                    yPosition += 3;
                });

                // Contact information
                yPosition += 5;
                doc.setFontSize(8);
                doc.setTextColor(0, 100, 200);
                doc.text('For professional solar installation services, consult with certified solar installers in your area.', 20, yPosition);
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
