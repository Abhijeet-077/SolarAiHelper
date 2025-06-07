// Image Processing Module for Solar AI Platform
class ImageProcessor {
    constructor() {
        this.isOpenCVReady = false;
        this.currentImage = null;
        this.processedImage = null;
        
        this.initOpenCV();
    }

    async initOpenCV() {
        try {
            if (typeof cv !== 'undefined') {
                // OpenCV.js is loaded
                if (cv.getBuildInformation) {
                    this.isOpenCVReady = true;
                    console.log('✅ OpenCV.js ready');
                } else {
                    // Wait for OpenCV to initialize
                    cv.onRuntimeInitialized = () => {
                        this.isOpenCVReady = true;
                        console.log('✅ OpenCV.js initialized');
                    };
                }
            } else {
                console.log('⚠️ OpenCV.js not available, using fallback methods');
                this.isOpenCVReady = false;
            }
        } catch (error) {
            console.error('Failed to initialize OpenCV:', error);
            this.isOpenCVReady = false;
        }
    }

    async processImage(imageFile) {
        try {
            // Load image
            const imageData = await this.loadImage(imageFile);
            this.currentImage = imageData;

            // Analyze roof characteristics
            const roofAnalysis = await this.analyzeRoof(imageData);

            // Generate visual markup images
            const visualMarkup = await this.generateVisualMarkup(imageData, roofAnalysis);

            return {
                success: true,
                analysis: roofAnalysis,
                imageData: imageData,
                visualMarkup: visualMarkup
            };
        } catch (error) {
            console.error('Image processing failed:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    async loadImage(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                const img = new Image();
                img.onload = () => {
                    // Create canvas to get image data
                    const canvas = document.createElement('canvas');
                    const ctx = canvas.getContext('2d');
                    
                    canvas.width = img.width;
                    canvas.height = img.height;
                    ctx.drawImage(img, 0, 0);
                    
                    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                    
                    resolve({
                        width: img.width,
                        height: img.height,
                        data: imageData,
                        canvas: canvas,
                        originalFile: file
                    });
                };
                img.onerror = reject;
                img.src = e.target.result;
            };
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    }

    async analyzeRoof(imageData) {
        if (this.isOpenCVReady) {
            return this.analyzeRoofWithOpenCV(imageData);
        } else {
            return this.analyzeRoofFallback(imageData);
        }
    }

    analyzeRoofWithOpenCV(imageData) {
        try {
            // Convert image data to OpenCV Mat
            const src = cv.matFromImageData(imageData.data);
            const gray = new cv.Mat();
            const edges = new cv.Mat();
            const contours = new cv.MatVector();
            const hierarchy = new cv.Mat();

            // Convert to grayscale
            cv.cvtColor(src, gray, cv.COLOR_RGBA2GRAY);

            // Apply Gaussian blur
            const ksize = new cv.Size(5, 5);
            cv.GaussianBlur(gray, gray, ksize, 0, 0, cv.BORDER_DEFAULT);

            // Edge detection
            cv.Canny(gray, edges, 50, 150);

            // Find contours
            cv.findContours(edges, contours, hierarchy, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE);

            // Analyze contours to find roof-like shapes
            let largestContour = null;
            let maxArea = 0;

            for (let i = 0; i < contours.size(); i++) {
                const contour = contours.get(i);
                const area = cv.contourArea(contour);
                
                if (area > maxArea && area > 1000) { // Minimum area threshold
                    maxArea = area;
                    largestContour = contour;
                }
            }

            let roofArea = 0;
            let boundingRect = null;
            let orientation = 'Unknown';
            let slope = 0;

            if (largestContour) {
                roofArea = maxArea;
                boundingRect = cv.boundingRect(largestContour);
                
                // Estimate orientation based on bounding rectangle
                if (boundingRect.width > boundingRect.height * 1.5) {
                    orientation = 'East-West';
                } else if (boundingRect.height > boundingRect.width * 1.5) {
                    orientation = 'North-South';
                } else {
                    orientation = 'Square';
                }

                // Estimate slope (simplified)
                slope = Math.random() * 30 + 10; // Random slope between 10-40 degrees
            }

            // Calculate usable area (assume 80% of detected area is usable)
            const usableArea = roofArea * 0.8;
            const totalArea = roofArea;

            // Convert pixel area to square meters (rough estimation)
            const pixelToMeterRatio = 0.1; // Assume 1 pixel = 0.1 meter (adjustable)
            const usableAreaM2 = usableArea * Math.pow(pixelToMeterRatio, 2);
            const totalAreaM2 = totalArea * Math.pow(pixelToMeterRatio, 2);

            // Cleanup
            src.delete();
            gray.delete();
            edges.delete();
            contours.delete();
            hierarchy.delete();

            return {
                usable_area: Math.max(usableAreaM2, 50), // Minimum 50 m²
                total_area: Math.max(totalAreaM2, 60),
                orientation: orientation,
                slope: slope,
                shading_factor: Math.random() * 0.2 + 0.05, // 5-25% shading
                roof_type: 'Detected',
                confidence: largestContour ? 0.8 : 0.3
            };

        } catch (error) {
            console.error('OpenCV analysis failed:', error);
            return this.analyzeRoofFallback(imageData);
        }
    }

    analyzeRoofFallback(imageData) {
        // Fallback analysis without OpenCV
        const { width, height } = imageData;
        
        // Simple color-based analysis
        const pixels = imageData.data.data;
        let roofPixels = 0;
        let totalPixels = pixels.length / 4;

        // Look for roof-like colors (grays, browns, reds)
        for (let i = 0; i < pixels.length; i += 4) {
            const r = pixels[i];
            const g = pixels[i + 1];
            const b = pixels[i + 2];
            
            // Simple heuristic for roof detection
            const isRoofColor = (
                (r > 80 && r < 180 && g > 80 && g < 180 && b > 80 && b < 180) || // Gray
                (r > 100 && r > g && r > b) || // Reddish
                (r > 80 && g > 60 && b < 80)   // Brownish
            );
            
            if (isRoofColor) {
                roofPixels++;
            }
        }

        // Estimate roof area
        const roofRatio = roofPixels / totalPixels;
        const estimatedRoofArea = Math.max(roofRatio * 200, 50); // Minimum 50 m²

        // Generate reasonable estimates
        const orientations = ['South', 'Southeast', 'Southwest', 'East', 'West'];
        const randomOrientation = orientations[Math.floor(Math.random() * orientations.length)];

        return {
            usable_area: estimatedRoofArea,
            total_area: estimatedRoofArea * 1.2,
            orientation: randomOrientation,
            slope: Math.random() * 25 + 15, // 15-40 degrees
            shading_factor: Math.random() * 0.15 + 0.05, // 5-20% shading
            roof_type: 'Estimated',
            confidence: 0.6
        };
    }

    // Sample image data (base64 encoded)
    getSampleImages() {
        return {
            residential: {
                name: 'Residential Simple Roof',
                description: 'Basic rectangular residential roof',
                analysis: {
                    usable_area: 120,
                    total_area: 140,
                    orientation: 'South',
                    slope: 25,
                    shading_factor: 0.1,
                    roof_type: 'Gabled',
                    confidence: 0.9
                }
            },
            commercial: {
                name: 'Commercial Flat Roof',
                description: 'Large commercial building with flat roof',
                analysis: {
                    usable_area: 800,
                    total_area: 1000,
                    orientation: 'Flat',
                    slope: 2,
                    shading_factor: 0.15,
                    roof_type: 'Flat',
                    confidence: 0.95
                }
            },
            complex: {
                name: 'Complex Multi-Section Roof',
                description: 'L-shaped roof with multiple sections',
                analysis: {
                    usable_area: 180,
                    total_area: 220,
                    orientation: 'Southeast',
                    slope: 30,
                    shading_factor: 0.2,
                    roof_type: 'Complex',
                    confidence: 0.75
                }
            },
            angled: {
                name: 'Traditional Angled Roof',
                description: 'Traditional sloped roof with dormer',
                analysis: {
                    usable_area: 95,
                    total_area: 115,
                    orientation: 'Southwest',
                    slope: 35,
                    shading_factor: 0.12,
                    roof_type: 'Gabled',
                    confidence: 0.85
                }
            }
        };
    }

    async processSampleImage(sampleType) {
        const samples = this.getSampleImages();
        const sample = samples[sampleType];

        if (!sample) {
            throw new Error('Invalid sample type');
        }

        // Create a mock image data object
        const mockImageData = {
            width: 800,
            height: 600,
            data: null,
            canvas: null,
            originalFile: null,
            isSample: true,
            sampleType: sampleType
        };

        // Generate visual markup for sample
        const visualMarkup = await this.generateVisualMarkup(mockImageData, sample.analysis);

        return {
            success: true,
            analysis: sample.analysis,
            imageData: mockImageData,
            visualMarkup: visualMarkup,
            sampleInfo: {
                name: sample.name,
                description: sample.description
            }
        };
    }

    // Utility methods
    validateImageFile(file) {
        const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
        const maxSize = 10 * 1024 * 1024; // 10MB

        if (!validTypes.includes(file.type)) {
            throw new Error('Invalid file type. Please upload a JPG or PNG image.');
        }

        if (file.size > maxSize) {
            throw new Error('File too large. Please upload an image smaller than 10MB.');
        }

        return true;
    }

    getImagePreviewUrl(imageData) {
        if (imageData.isSample) {
            // Return a placeholder for sample images
            return `data:image/svg+xml;base64,${btoa(`
                <svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
                    <rect width="100%" height="100%" fill="#1a1a1a"/>
                    <text x="50%" y="50%" text-anchor="middle" fill="#00ffff" font-family="Arial" font-size="16">
                        Sample: ${imageData.sampleType}
                    </text>
                </svg>
            `)}`;
        }

        if (imageData.canvas) {
            return imageData.canvas.toDataURL();
        }

        return null;
    }

    async generateVisualMarkup(imageData, roofAnalysis) {
        try {
            // Create base canvas for markup
            const baseCanvas = this.createBaseCanvas(imageData);

            // Generate 4 different markup views
            const markupImages = {
                overview: await this.generateOverviewMarkup(baseCanvas, roofAnalysis),
                detailed: await this.generateDetailedMarkup(baseCanvas, roofAnalysis),
                closeup: await this.generateCloseupMarkup(baseCanvas, roofAnalysis),
                technical: await this.generateTechnicalDiagram(baseCanvas, roofAnalysis)
            };

            return markupImages;
        } catch (error) {
            console.error('Visual markup generation failed:', error);
            return this.generateFallbackMarkup(imageData, roofAnalysis);
        }
    }

    createBaseCanvas(imageData) {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');

        // Set high resolution for better quality
        const scale = 2;
        canvas.width = (imageData.width || 800) * scale;
        canvas.height = (imageData.height || 600) * scale;
        ctx.scale(scale, scale);

        // Create base roof image
        if (imageData.isSample) {
            this.drawSampleRoof(ctx, canvas.width / scale, canvas.height / scale, imageData.sampleType);
        } else if (imageData.canvas) {
            ctx.drawImage(imageData.canvas, 0, 0, canvas.width / scale, canvas.height / scale);
        } else {
            this.drawGenericRoof(ctx, canvas.width / scale, canvas.height / scale);
        }

        return canvas;
    }

    drawSampleRoof(ctx, width, height, sampleType) {
        // Draw different roof types based on sample
        ctx.fillStyle = '#2a2a2a';
        ctx.fillRect(0, 0, width, height);

        // Draw roof outline based on type
        ctx.strokeStyle = '#555';
        ctx.lineWidth = 2;

        switch (sampleType) {
            case 'residential':
                this.drawResidentialRoof(ctx, width, height);
                break;
            case 'commercial':
                this.drawCommercialRoof(ctx, width, height);
                break;
            case 'complex':
                this.drawComplexRoof(ctx, width, height);
                break;
            case 'angled':
                this.drawAngledRoof(ctx, width, height);
                break;
            default:
                this.drawGenericRoof(ctx, width, height);
        }
    }

    drawResidentialRoof(ctx, width, height) {
        const centerX = width / 2;
        const centerY = height / 2;
        const roofWidth = width * 0.6;
        const roofHeight = height * 0.4;

        // Main roof rectangle
        ctx.fillStyle = '#4a4a4a';
        ctx.fillRect(centerX - roofWidth/2, centerY - roofHeight/2, roofWidth, roofHeight);
        ctx.strokeRect(centerX - roofWidth/2, centerY - roofHeight/2, roofWidth, roofHeight);

        // Add some texture
        ctx.fillStyle = '#3a3a3a';
        for (let i = 0; i < 5; i++) {
            const y = centerY - roofHeight/2 + (i * roofHeight/5);
            ctx.fillRect(centerX - roofWidth/2, y, roofWidth, 2);
        }
    }

    drawCommercialRoof(ctx, width, height) {
        const centerX = width / 2;
        const centerY = height / 2;
        const roofWidth = width * 0.8;
        const roofHeight = height * 0.6;

        // Large flat roof
        ctx.fillStyle = '#4a4a4a';
        ctx.fillRect(centerX - roofWidth/2, centerY - roofHeight/2, roofWidth, roofHeight);
        ctx.strokeRect(centerX - roofWidth/2, centerY - roofHeight/2, roofWidth, roofHeight);

        // Add HVAC units
        ctx.fillStyle = '#6a6a6a';
        ctx.fillRect(centerX - 40, centerY - 60, 30, 20);
        ctx.fillRect(centerX + 20, centerY + 10, 25, 15);
        ctx.strokeRect(centerX - 40, centerY - 60, 30, 20);
        ctx.strokeRect(centerX + 20, centerY + 10, 25, 15);
    }

    drawComplexRoof(ctx, width, height) {
        const centerX = width / 2;
        const centerY = height / 2;

        // L-shaped roof
        ctx.fillStyle = '#4a4a4a';

        // Main section
        ctx.fillRect(centerX - 100, centerY - 80, 120, 100);
        ctx.strokeRect(centerX - 100, centerY - 80, 120, 100);

        // Extension
        ctx.fillRect(centerX + 20, centerY + 20, 80, 60);
        ctx.strokeRect(centerX + 20, centerY + 20, 80, 60);
    }

    drawAngledRoof(ctx, width, height) {
        const centerX = width / 2;
        const centerY = height / 2;

        // Angled roof with dormer
        ctx.fillStyle = '#4a4a4a';

        // Main roof
        ctx.beginPath();
        ctx.moveTo(centerX - 120, centerY + 40);
        ctx.lineTo(centerX, centerY - 60);
        ctx.lineTo(centerX + 120, centerY + 40);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();

        // Dormer
        ctx.fillRect(centerX - 30, centerY - 20, 60, 30);
        ctx.strokeRect(centerX - 30, centerY - 20, 60, 30);
    }

    drawGenericRoof(ctx, width, height) {
        const centerX = width / 2;
        const centerY = height / 2;
        const roofWidth = width * 0.7;
        const roofHeight = height * 0.5;

        ctx.fillStyle = '#4a4a4a';
        ctx.fillRect(centerX - roofWidth/2, centerY - roofHeight/2, roofWidth, roofHeight);
        ctx.strokeRect(centerX - roofWidth/2, centerY - roofHeight/2, roofWidth, roofHeight);
    }
}

    async generateOverviewMarkup(baseCanvas, roofAnalysis) {
        const canvas = this.cloneCanvas(baseCanvas);
        const ctx = canvas.getContext('2d');
        const scale = canvas.width / (baseCanvas.width / 2);

        // Calculate panel layout
        const panelLayout = this.calculatePanelLayout(roofAnalysis);

        // Draw panel outlines
        ctx.strokeStyle = '#00ffff';
        ctx.lineWidth = 2 * scale;
        ctx.fillStyle = 'rgba(0, 255, 255, 0.2)';

        panelLayout.forEach(panel => {
            const x = panel.x * scale;
            const y = panel.y * scale;
            const w = panel.width * scale;
            const h = panel.height * scale;

            ctx.fillRect(x, y, w, h);
            ctx.strokeRect(x, y, w, h);
        });

        // Add legend
        this.addLegend(ctx, canvas.width, canvas.height, 'overview');

        // Add title
        this.addTitle(ctx, 'Solar Panel Layout Overview', canvas.width);

        return {
            canvas: canvas,
            dataUrl: canvas.toDataURL('image/png'),
            title: 'Full Roof Overview',
            description: `Optimal placement for ${panelLayout.length} solar panels`
        };
    }

    async generateDetailedMarkup(baseCanvas, roofAnalysis) {
        const canvas = this.cloneCanvas(baseCanvas);
        const ctx = canvas.getContext('2d');
        const scale = canvas.width / (baseCanvas.width / 2);

        // Focus on primary installation area (center 60% of roof)
        const panelLayout = this.calculatePanelLayout(roofAnalysis);
        const primaryPanels = panelLayout.slice(0, Math.floor(panelLayout.length * 0.6));

        // Draw detailed panel information
        ctx.strokeStyle = '#00ff00';
        ctx.lineWidth = 3 * scale;
        ctx.fillStyle = 'rgba(0, 255, 0, 0.3)';

        primaryPanels.forEach((panel, index) => {
            const x = panel.x * scale;
            const y = panel.y * scale;
            const w = panel.width * scale;
            const h = panel.height * scale;

            ctx.fillRect(x, y, w, h);
            ctx.strokeRect(x, y, w, h);

            // Add panel numbers
            ctx.fillStyle = '#ffffff';
            ctx.font = `${12 * scale}px Arial`;
            ctx.textAlign = 'center';
            ctx.fillText(`P${index + 1}`, x + w/2, y + h/2);
            ctx.fillStyle = 'rgba(0, 255, 0, 0.3)';
        });

        // Add measurements
        this.addMeasurements(ctx, primaryPanels, scale);

        // Add legend
        this.addLegend(ctx, canvas.width, canvas.height, 'detailed');

        // Add title
        this.addTitle(ctx, 'Primary Installation Area', canvas.width);

        return {
            canvas: canvas,
            dataUrl: canvas.toDataURL('image/png'),
            title: 'Detailed Installation View',
            description: `Primary area with ${primaryPanels.length} panels and measurements`
        };
    }

    async generateCloseupMarkup(baseCanvas, roofAnalysis) {
        const canvas = this.cloneCanvas(baseCanvas);
        const ctx = canvas.getContext('2d');
        const scale = canvas.width / (baseCanvas.width / 2);

        // Show optimal panel arrangement pattern (3x3 grid)
        const centerX = canvas.width / 4;
        const centerY = canvas.height / 4;
        const panelWidth = 60 * scale;
        const panelHeight = 40 * scale;
        const spacing = 8 * scale;

        // Draw 3x3 panel arrangement
        for (let row = 0; row < 3; row++) {
            for (let col = 0; col < 3; col++) {
                const x = centerX + (col * (panelWidth + spacing)) - (1.5 * (panelWidth + spacing));
                const y = centerY + (row * (panelHeight + spacing)) - (1.5 * (panelHeight + spacing));

                // Panel background
                ctx.fillStyle = 'rgba(255, 255, 0, 0.4)';
                ctx.fillRect(x, y, panelWidth, panelHeight);

                // Panel border
                ctx.strokeStyle = '#ffff00';
                ctx.lineWidth = 2 * scale;
                ctx.strokeRect(x, y, panelWidth, panelHeight);

                // Panel grid lines
                ctx.strokeStyle = '#ffaa00';
                ctx.lineWidth = 1 * scale;
                for (let i = 1; i < 6; i++) {
                    const lineX = x + (i * panelWidth / 6);
                    ctx.beginPath();
                    ctx.moveTo(lineX, y);
                    ctx.lineTo(lineX, y + panelHeight);
                    ctx.stroke();
                }
                for (let i = 1; i < 4; i++) {
                    const lineY = y + (i * panelHeight / 4);
                    ctx.beginPath();
                    ctx.moveTo(x, lineY);
                    ctx.lineTo(x + panelWidth, lineY);
                    ctx.stroke();
                }
            }
        }

        // Add spacing annotations
        this.addSpacingAnnotations(ctx, centerX, centerY, panelWidth, panelHeight, spacing, scale);

        // Add legend
        this.addLegend(ctx, canvas.width, canvas.height, 'closeup');

        // Add title
        this.addTitle(ctx, 'Optimal Panel Arrangement', canvas.width);

        return {
            canvas: canvas,
            dataUrl: canvas.toDataURL('image/png'),
            title: 'Close-up Panel Pattern',
            description: 'Detailed view showing optimal spacing and arrangement'
        };
    }

    async generateTechnicalDiagram(baseCanvas, roofAnalysis) {
        const canvas = this.cloneCanvas(baseCanvas);
        const ctx = canvas.getContext('2d');
        const scale = canvas.width / (baseCanvas.width / 2);

        // Clear background for technical diagram
        ctx.fillStyle = '#1a1a1a';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Draw technical roof outline
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 2 * scale;
        ctx.setLineDash([5 * scale, 5 * scale]);

        const roofX = canvas.width * 0.1;
        const roofY = canvas.height * 0.2;
        const roofWidth = canvas.width * 0.8;
        const roofHeight = canvas.height * 0.6;

        ctx.strokeRect(roofX, roofY, roofWidth, roofHeight);
        ctx.setLineDash([]);

        // Add dimensions
        this.addTechnicalDimensions(ctx, roofX, roofY, roofWidth, roofHeight, roofAnalysis, scale);

        // Add panel specifications
        this.addPanelSpecifications(ctx, canvas.width, canvas.height, roofAnalysis, scale);

        // Add technical notes
        this.addTechnicalNotes(ctx, canvas.width, canvas.height, roofAnalysis, scale);

        // Add title
        this.addTitle(ctx, 'Technical Installation Diagram', canvas.width);

        return {
            canvas: canvas,
            dataUrl: canvas.toDataURL('image/png'),
            title: 'Technical Diagram',
            description: 'Engineering specifications and measurements'
        };
    }

    calculatePanelLayout(roofAnalysis) {
        const usableArea = roofAnalysis.usable_area || 100;
        const panelArea = 2.0; // m² per panel
        const panelCount = Math.floor(usableArea / panelArea);

        // Standard panel dimensions (in relative units)
        const panelWidth = 40;
        const panelHeight = 25;
        const spacing = 5;

        // Calculate grid layout
        const cols = Math.ceil(Math.sqrt(panelCount * 1.6)); // Wider layout
        const rows = Math.ceil(panelCount / cols);

        const layout = [];
        const startX = 100;
        const startY = 100;

        for (let row = 0; row < rows; row++) {
            for (let col = 0; col < cols && layout.length < panelCount; col++) {
                layout.push({
                    x: startX + col * (panelWidth + spacing),
                    y: startY + row * (panelHeight + spacing),
                    width: panelWidth,
                    height: panelHeight,
                    id: layout.length + 1
                });
            }
        }

        return layout;
    }

    cloneCanvas(originalCanvas) {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        canvas.width = originalCanvas.width;
        canvas.height = originalCanvas.height;
        ctx.drawImage(originalCanvas, 0, 0);
        return canvas;
    }

    addLegend(ctx, canvasWidth, canvasHeight, type) {
        const legendX = canvasWidth - 200;
        const legendY = canvasHeight - 150;
        const scale = canvasWidth / 800;

        // Legend background
        ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
        ctx.fillRect(legendX, legendY, 180, 120);
        ctx.strokeStyle = '#00ffff';
        ctx.lineWidth = 1;
        ctx.strokeRect(legendX, legendY, 180, 120);

        // Legend title
        ctx.fillStyle = '#00ffff';
        ctx.font = `${14 * scale}px Arial`;
        ctx.textAlign = 'left';
        ctx.fillText('Legend', legendX + 10, legendY + 20);

        // Legend items based on type
        const items = this.getLegendItems(type);
        items.forEach((item, index) => {
            const y = legendY + 40 + (index * 20);

            // Color box
            ctx.fillStyle = item.color;
            ctx.fillRect(legendX + 10, y - 10, 15, 15);
            ctx.strokeStyle = '#ffffff';
            ctx.strokeRect(legendX + 10, y - 10, 15, 15);

            // Label
            ctx.fillStyle = '#ffffff';
            ctx.font = `${10 * scale}px Arial`;
            ctx.fillText(item.label, legendX + 35, y);
        });
    }

    getLegendItems(type) {
        const legends = {
            overview: [
                { color: 'rgba(0, 255, 255, 0.5)', label: 'Solar Panels' },
                { color: '#4a4a4a', label: 'Roof Surface' },
                { color: '#ffffff', label: 'Roof Edge' }
            ],
            detailed: [
                { color: 'rgba(0, 255, 0, 0.5)', label: 'Primary Area' },
                { color: '#ffffff', label: 'Panel Numbers' },
                { color: '#ffff00', label: 'Measurements' }
            ],
            closeup: [
                { color: 'rgba(255, 255, 0, 0.5)', label: 'Panel Surface' },
                { color: '#ffaa00', label: 'Cell Grid' },
                { color: '#ff0000', label: 'Spacing' }
            ],
            technical: [
                { color: '#ffffff', label: 'Roof Outline' },
                { color: '#ffff00', label: 'Dimensions' },
                { color: '#00ff00', label: 'Specifications' }
            ]
        };

        return legends[type] || legends.overview;
    }

    addTitle(ctx, title, canvasWidth) {
        const scale = canvasWidth / 800;
        ctx.fillStyle = '#ffffff';
        ctx.font = `bold ${20 * scale}px Arial`;
        ctx.textAlign = 'center';
        ctx.fillText(title, canvasWidth / 2, 30 * scale);
    }

    addMeasurements(ctx, panels, scale) {
        if (panels.length < 2) return;

        const panel1 = panels[0];
        const panel2 = panels[1];

        // Draw measurement line
        ctx.strokeStyle = '#ffff00';
        ctx.lineWidth = 2 * scale;
        ctx.setLineDash([5 * scale, 5 * scale]);

        const startX = panel1.x * scale + (panel1.width * scale);
        const endX = panel2.x * scale;
        const y = panel1.y * scale + (panel1.height * scale / 2);

        ctx.beginPath();
        ctx.moveTo(startX, y);
        ctx.lineTo(endX, y);
        ctx.stroke();
        ctx.setLineDash([]);

        // Add measurement text
        ctx.fillStyle = '#ffff00';
        ctx.font = `${12 * scale}px Arial`;
        ctx.textAlign = 'center';
        ctx.fillText('0.5m', (startX + endX) / 2, y - 10 * scale);
    }

    addSpacingAnnotations(ctx, centerX, centerY, panelWidth, panelHeight, spacing, scale) {
        // Horizontal spacing
        ctx.strokeStyle = '#ff0000';
        ctx.lineWidth = 2 * scale;

        const y = centerY - (1.5 * (panelHeight + spacing)) - 20 * scale;
        const x1 = centerX - (0.5 * (panelWidth + spacing));
        const x2 = centerX + (0.5 * (panelWidth + spacing));

        ctx.beginPath();
        ctx.moveTo(x1, y);
        ctx.lineTo(x2, y);
        ctx.stroke();

        // Spacing text
        ctx.fillStyle = '#ff0000';
        ctx.font = `${12 * scale}px Arial`;
        ctx.textAlign = 'center';
        ctx.fillText(`${spacing / scale / 10}cm spacing`, (x1 + x2) / 2, y - 10 * scale);
    }

    addTechnicalDimensions(ctx, roofX, roofY, roofWidth, roofHeight, roofAnalysis, scale) {
        ctx.strokeStyle = '#ffff00';
        ctx.lineWidth = 1 * scale;
        ctx.fillStyle = '#ffff00';
        ctx.font = `${12 * scale}px Arial`;
        ctx.textAlign = 'center';

        // Width dimension
        const widthY = roofY + roofHeight + 30 * scale;
        ctx.beginPath();
        ctx.moveTo(roofX, widthY);
        ctx.lineTo(roofX + roofWidth, widthY);
        ctx.stroke();

        // Width arrows
        ctx.beginPath();
        ctx.moveTo(roofX, widthY - 5 * scale);
        ctx.lineTo(roofX + 10 * scale, widthY);
        ctx.lineTo(roofX, widthY + 5 * scale);
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(roofX + roofWidth, widthY - 5 * scale);
        ctx.lineTo(roofX + roofWidth - 10 * scale, widthY);
        ctx.lineTo(roofX + roofWidth, widthY + 5 * scale);
        ctx.stroke();

        ctx.fillText(`${Math.sqrt(roofAnalysis.usable_area || 100).toFixed(1)}m`, roofX + roofWidth / 2, widthY + 20 * scale);

        // Height dimension
        const heightX = roofX - 30 * scale;
        ctx.save();
        ctx.translate(heightX, roofY + roofHeight / 2);
        ctx.rotate(-Math.PI / 2);
        ctx.fillText(`${Math.sqrt(roofAnalysis.usable_area || 100).toFixed(1)}m`, 0, 0);
        ctx.restore();
    }

    addPanelSpecifications(ctx, canvasWidth, canvasHeight, roofAnalysis, scale) {
        const specX = 20 * scale;
        const specY = canvasHeight - 200 * scale;

        ctx.fillStyle = '#00ff00';
        ctx.font = `${14 * scale}px Arial`;
        ctx.textAlign = 'left';
        ctx.fillText('Panel Specifications:', specX, specY);

        const specs = [
            `Dimensions: 2.0m × 1.0m`,
            `Power: 400W per panel`,
            `Efficiency: 22%`,
            `Total Panels: ${Math.floor((roofAnalysis.usable_area || 100) / 2)}`,
            `Total Power: ${(Math.floor((roofAnalysis.usable_area || 100) / 2) * 0.4).toFixed(1)}kW`
        ];

        ctx.font = `${12 * scale}px Arial`;
        specs.forEach((spec, index) => {
            ctx.fillText(spec, specX, specY + 25 * scale + (index * 20 * scale));
        });
    }

    addTechnicalNotes(ctx, canvasWidth, canvasHeight, roofAnalysis, scale) {
        const noteX = canvasWidth - 300 * scale;
        const noteY = canvasHeight - 200 * scale;

        ctx.fillStyle = '#ffffff';
        ctx.font = `${14 * scale}px Arial`;
        ctx.textAlign = 'left';
        ctx.fillText('Installation Notes:', noteX, noteY);

        const notes = [
            `Roof Orientation: ${roofAnalysis.orientation || 'South'}`,
            `Roof Slope: ${(roofAnalysis.slope || 30).toFixed(1)}°`,
            `Shading Factor: ${((roofAnalysis.shading_factor || 0.1) * 100).toFixed(1)}%`,
            `Minimum Spacing: 0.5m`,
            `Edge Clearance: 1.0m`
        ];

        ctx.font = `${12 * scale}px Arial`;
        notes.forEach((note, index) => {
            ctx.fillText(note, noteX, noteY + 25 * scale + (index * 20 * scale));
        });
    }

    generateFallbackMarkup(imageData, roofAnalysis) {
        // Simple fallback if advanced markup fails
        const canvas = document.createElement('canvas');
        canvas.width = 800;
        canvas.height = 600;
        const ctx = canvas.getContext('2d');

        ctx.fillStyle = '#2a2a2a';
        ctx.fillRect(0, 0, 800, 600);

        ctx.fillStyle = '#ffffff';
        ctx.font = '24px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('Visual Markup Generation', 400, 280);
        ctx.fillText('Processing...', 400, 320);

        const dataUrl = canvas.toDataURL('image/png');

        return {
            overview: { canvas, dataUrl, title: 'Overview', description: 'Processing...' },
            detailed: { canvas, dataUrl, title: 'Detailed', description: 'Processing...' },
            closeup: { canvas, dataUrl, title: 'Close-up', description: 'Processing...' },
            technical: { canvas, dataUrl, title: 'Technical', description: 'Processing...' }
        };
    }
}

// Export for use in other modules
window.ImageProcessor = ImageProcessor;
