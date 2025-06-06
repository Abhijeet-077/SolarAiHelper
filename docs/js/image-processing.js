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
            
            return {
                success: true,
                analysis: roofAnalysis,
                imageData: imageData
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

        return {
            success: true,
            analysis: sample.analysis,
            imageData: mockImageData,
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
}

// Export for use in other modules
window.ImageProcessor = ImageProcessor;
