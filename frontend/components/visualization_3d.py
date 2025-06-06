"""
Advanced 3D Visualization Component for Solar Panel Placement
Creates interactive Three.js-based roof modeling with solar panel simulation
"""

import streamlit as st
import streamlit.components.v1 as components
import json
from typing import Dict, Any, List
import base64

class Solar3DVisualizer:
    """Interactive 3D visualization for solar panel placement"""
    
    def __init__(self):
        self.scene_data = {}
        self.panel_configurations = []
        
    def generate_3d_scene_data(self, roof_analysis: Dict[str, Any], 
                              solar_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate 3D scene data from analysis results"""
        
        # Extract roof geometry
        roof_geometry = roof_analysis.get('geometry', {})
        roof_area = roof_geometry.get('total_area', 1000)  # sq ft
        roof_orientation = roof_geometry.get('primary_orientation', 'South')
        roof_tilt = roof_geometry.get('average_slope', 15)  # degrees
        
        # Calculate roof dimensions (assuming rectangular for simplicity)
        aspect_ratio = roof_geometry.get('aspect_ratio', 1.5)
        roof_width = (roof_area / aspect_ratio) ** 0.5
        roof_length = roof_width * aspect_ratio
        
        # Generate 3D model data
        scene_data = {
            "roof": {
                "geometry": {
                    "type": "rectangle",
                    "width": roof_width,
                    "length": roof_length,
                    "tilt": roof_tilt,
                    "orientation": self._orientation_to_degrees(roof_orientation),
                    "vertices": self._generate_roof_vertices(roof_width, roof_length, roof_tilt)
                },
                "material": {
                    "color": "#8B4513",
                    "texture": "roof_tiles",
                    "opacity": 0.8
                },
                "obstacles": roof_analysis.get('obstacles', [])
            },
            "panels": {
                "layout": self._generate_panel_layout(roof_width, roof_length, roof_analysis),
                "specifications": self._get_panel_specifications(),
                "optimal_count": roof_analysis.get('panel_layout', {}).get('panels_count', 20)
            },
            "environment": {
                "sun_path": self._generate_sun_path_data(solar_data),
                "shadows": self._calculate_shadow_patterns(roof_analysis),
                "background": "sky_gradient"
            },
            "performance": {
                "energy_production": solar_data.get('annual_production_kwh', 8000),
                "efficiency_map": self._generate_efficiency_heatmap(roof_analysis)
            }
        }
        
        return scene_data
    
    def render_3d_visualization(self, scene_data: Dict[str, Any]):
        """Render the interactive 3D visualization"""
        
        # Custom CSS for 3D container
        st.markdown("""
        <style>
        .visualization-3d-container {
            background: linear-gradient(135deg, #f0f9ff 0%, #e0e7ff 100%);
            border-radius: 12px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            margin: 1rem 0;
        }
        
        .viz-header {
            background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
            color: white;
            padding: 1.5rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .viz-controls {
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
        }
        
        .viz-control-btn {
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.9rem;
            transition: all 0.3s ease;
        }
        
        .viz-control-btn:hover {
            background: rgba(255, 255, 255, 0.3);
            transform: translateY(-1px);
        }
        
        .viz-control-btn.active {
            background: rgba(255, 255, 255, 0.4);
        }
        
        .three-js-container {
            height: 500px;
            width: 100%;
            position: relative;
            background: linear-gradient(135deg, #87CEEB 0%, #98D8E8 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            border-top: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .loading-3d {
            text-align: center;
            color: #6b7280;
        }
        
        .loading-3d .spinner {
            width: 50px;
            height: 50px;
            border: 4px solid #f3f4f6;
            border-top: 4px solid #8b5cf6;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 1rem;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .viz-info-panel {
            background: white;
            padding: 1.5rem;
            border-top: 1px solid #e5e7eb;
        }
        
        .viz-metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 1rem;
        }
        
        .viz-metric {
            text-align: center;
            padding: 1rem;
            background: #f8fafc;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
        }
        
        .viz-metric-value {
            font-size: 1.5rem;
            font-weight: bold;
            color: #1f2937;
            margin-bottom: 0.25rem;
        }
        
        .viz-metric-label {
            font-size: 0.9rem;
            color: #6b7280;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # 3D Visualization Container
        st.markdown('<div class="visualization-3d-container">', unsafe_allow_html=True)
        
        # Header with controls
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("""
            <div class="viz-header">
                <h3 style="margin: 0; font-size: 1.5rem;">🏠 Interactive 3D Roof Model</h3>
            </div>
            """, unsafe_allow_html=True)
        
        # Control panel
        with st.container():
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                show_panels = st.checkbox("Show Panels", value=True, key="show_panels_3d")
            with col2:
                show_shadows = st.checkbox("Show Shadows", value=True, key="show_shadows_3d")
            with col3:
                show_sun_path = st.checkbox("Sun Path", value=False, key="show_sun_path_3d")
            with col4:
                time_of_day = st.slider("Time of Day", 6, 18, 12, key="time_slider_3d")
            with col5:
                season = st.selectbox("Season", ["Spring", "Summer", "Fall", "Winter"], 
                                    index=1, key="season_3d")
        
        # Three.js 3D Scene
        self._render_threejs_scene(scene_data, show_panels, show_shadows, 
                                  show_sun_path, time_of_day, season)
        
        # Information panel
        self._render_info_panel(scene_data)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def _render_threejs_scene(self, scene_data: Dict[str, Any], show_panels: bool, 
                             show_shadows: bool, show_sun_path: bool, 
                             time_of_day: int, season: str):
        """Render the Three.js 3D scene"""
        
        # Generate Three.js HTML
        threejs_html = self._generate_threejs_html(scene_data, {
            'show_panels': show_panels,
            'show_shadows': show_shadows,
            'show_sun_path': show_sun_path,
            'time_of_day': time_of_day,
            'season': season
        })
        
        # Display the 3D scene
        components.html(threejs_html, height=500)
    
    def _generate_threejs_html(self, scene_data: Dict[str, Any], 
                              options: Dict[str, Any]) -> str:
        """Generate Three.js HTML for 3D visualization"""
        
        # Convert scene data to JSON for JavaScript
        scene_json = json.dumps(scene_data, indent=2)
        options_json = json.dumps(options)
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
            <style>
                body {{ margin: 0; padding: 0; overflow: hidden; }}
                #container {{ width: 100%; height: 500px; position: relative; }}
                #loading {{ 
                    position: absolute; 
                    top: 50%; 
                    left: 50%; 
                    transform: translate(-50%, -50%);
                    text-align: center;
                    color: #6b7280;
                }}
                .controls {{ 
                    position: absolute;
                    top: 10px;
                    left: 10px;
                    background: rgba(255, 255, 255, 0.9);
                    padding: 10px;
                    border-radius: 8px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }}
            </style>
        </head>
        <body>
            <div id="container">
                <div id="loading">
                    <div style="width: 50px; height: 50px; border: 4px solid #f3f4f6; 
                               border-top: 4px solid #8b5cf6; border-radius: 50%; 
                               animation: spin 1s linear infinite; margin: 0 auto 1rem;"></div>
                    <p>Loading 3D Model...</p>
                </div>
                <div class="controls" id="info-panel" style="display: none;">
                    <h4 style="margin: 0 0 10px 0;">3D Controls</h4>
                    <p style="margin: 5px 0; font-size: 12px;">🖱️ Drag to rotate</p>
                    <p style="margin: 5px 0; font-size: 12px;">🔍 Scroll to zoom</p>
                    <p style="margin: 5px 0; font-size: 12px;">⚡ Panels: {options.get('show_panels', True)}</p>
                </div>
            </div>
            
            <script>
                // Scene data and options
                const sceneData = {scene_json};
                const options = {options_json};
                
                // Three.js setup
                let scene, camera, renderer, controls;
                let roofMesh, panelMeshes = [];
                
                function init() {{
                    // Create scene
                    scene = new THREE.Scene();
                    scene.background = new THREE.Color(0x87CEEB);
                    
                    // Create camera
                    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
                    camera.position.set(50, 50, 50);
                    
                    // Create renderer
                    renderer = new THREE.WebGLRenderer({{ antialias: true }});
                    renderer.setSize(window.innerWidth, 500);
                    renderer.shadowMap.enabled = true;
                    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
                    
                    const container = document.getElementById('container');
                    container.appendChild(renderer.domElement);
                    
                    // Add controls
                    controls = new THREE.OrbitControls(camera, renderer.domElement);
                    controls.enableDamping = true;
                    controls.dampingFactor = 0.25;
                    
                    // Add lighting
                    addLighting();
                    
                    // Create roof
                    createRoof();
                    
                    // Add solar panels if enabled
                    if (options.show_panels) {{
                        createSolarPanels();
                    }}
                    
                    // Hide loading, show info
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('info-panel').style.display = 'block';
                    
                    // Start render loop
                    animate();
                }}
                
                function addLighting() {{
                    // Ambient light
                    const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
                    scene.add(ambientLight);
                    
                    // Directional light (sun)
                    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
                    const hour = options.time_of_day || 12;
                    const angle = (hour - 6) * Math.PI / 12; // 6 AM to 6 PM
                    directionalLight.position.set(
                        Math.cos(angle) * 100,
                        Math.sin(angle) * 100,
                        50
                    );
                    directionalLight.castShadow = true;
                    directionalLight.shadow.mapSize.width = 2048;
                    directionalLight.shadow.mapSize.height = 2048;
                    scene.add(directionalLight);
                }}
                
                function createRoof() {{
                    const roofData = sceneData.roof;
                    const geometry = new THREE.PlaneGeometry(
                        roofData.geometry.width,
                        roofData.geometry.length
                    );
                    
                    const material = new THREE.MeshLambertMaterial({{
                        color: roofData.material.color,
                        side: THREE.DoubleSide
                    }});
                    
                    roofMesh = new THREE.Mesh(geometry, material);
                    roofMesh.rotation.x = -Math.PI / 2; // Horizontal
                    roofMesh.rotation.z = roofData.geometry.tilt * Math.PI / 180; // Tilt
                    roofMesh.receiveShadow = true;
                    scene.add(roofMesh);
                    
                    // Add ground plane
                    const groundGeometry = new THREE.PlaneGeometry(200, 200);
                    const groundMaterial = new THREE.MeshLambertMaterial({{ color: 0x90EE90 }});
                    const ground = new THREE.Mesh(groundGeometry, groundMaterial);
                    ground.rotation.x = -Math.PI / 2;
                    ground.position.y = -10;
                    ground.receiveShadow = true;
                    scene.add(ground);
                }}
                
                function createSolarPanels() {{
                    const panelData = sceneData.panels;
                    const panelCount = panelData.optimal_count;
                    const roofWidth = sceneData.roof.geometry.width;
                    const roofLength = sceneData.roof.geometry.length;
                    
                    // Panel dimensions (typical residential panel)
                    const panelWidth = 3.25; // feet
                    const panelLength = 5.5; // feet
                    const panelThickness = 0.15;
                    
                    // Calculate grid layout
                    const panelsPerRow = Math.floor(roofWidth / panelWidth);
                    const panelRows = Math.floor(roofLength / panelLength);
                    const actualPanelCount = Math.min(panelCount, panelsPerRow * panelRows);
                    
                    const panelGeometry = new THREE.BoxGeometry(panelWidth, panelLength, panelThickness);
                    const panelMaterial = new THREE.MeshLambertMaterial({{ 
                        color: 0x1a1a2e,
                        transparent: true,
                        opacity: 0.9
                    }});
                    
                    // Create panel grid
                    let panelIndex = 0;
                    for (let row = 0; row < panelRows && panelIndex < actualPanelCount; row++) {{
                        for (let col = 0; col < panelsPerRow && panelIndex < actualPanelCount; col++) {{
                            const panel = new THREE.Mesh(panelGeometry, panelMaterial);
                            
                            // Position panel
                            panel.position.x = (col - panelsPerRow / 2) * panelWidth;
                            panel.position.z = (row - panelRows / 2) * panelLength;
                            panel.position.y = panelThickness / 2 + 0.1; // Slightly above roof
                            
                            panel.castShadow = true;
                            panelMeshes.push(panel);
                            scene.add(panel);
                            panelIndex++;
                        }}
                    }}
                }}
                
                function animate() {{
                    requestAnimationFrame(animate);
                    controls.update();
                    renderer.render(scene, camera);
                }}
                
                function handleResize() {{
                    camera.aspect = window.innerWidth / window.innerHeight;
                    camera.updateProjectionMatrix();
                    renderer.setSize(window.innerWidth, 500);
                }}
                
                window.addEventListener('resize', handleResize);
                
                // Initialize when page loads
                init();
            </script>
        </body>
        </html>
        """
        
        return html_content
    
    def _render_info_panel(self, scene_data: Dict[str, Any]):
        """Render information panel below 3D visualization"""
        
        st.markdown("""
        <div class="viz-info-panel">
            <h4 style="margin: 0 0 1rem 0; color: #1f2937;">📊 3D Model Information</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Metrics grid
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Roof Area",
                f"{scene_data['roof']['geometry'].get('width', 0) * scene_data['roof']['geometry'].get('length', 0):.0f} sq ft",
                help="Total roof area in the 3D model"
            )
        
        with col2:
            st.metric(
                "Panel Count",
                f"{scene_data['panels'].get('optimal_count', 0)}",
                help="Optimal number of solar panels"
            )
        
        with col3:
            st.metric(
                "Roof Tilt",
                f"{scene_data['roof']['geometry'].get('tilt', 0):.1f}°",
                help="Roof slope angle"
            )
        
        with col4:
            st.metric(
                "Annual Production",
                f"{scene_data['performance'].get('energy_production', 0):,.0f} kWh",
                help="Estimated annual energy production"
            )
        
        # Export options
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📷 Capture Screenshot", key="capture_3d"):
                st.info("Screenshot feature will be available in the full version")
        
        with col2:
            if st.button("📄 Export 3D Model", key="export_3d"):
                st.info("3D model export feature will be available in the full version")
        
        with col3:
            if st.button("🔗 Share Visualization", key="share_3d"):
                st.info("Sharing feature will be available in the full version")
    
    def _generate_roof_vertices(self, width: float, length: float, tilt: float) -> List[List[float]]:
        """Generate 3D vertices for roof geometry"""
        half_width = width / 2
        half_length = length / 2
        height_offset = half_length * np.tan(np.radians(tilt))
        
        vertices = [
            [-half_width, 0, -half_length],
            [half_width, 0, -half_length],
            [half_width, height_offset, half_length],
            [-half_width, height_offset, half_length]
        ]
        
        return vertices
    
    def _generate_panel_layout(self, roof_width: float, roof_length: float,
                              roof_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate optimal panel layout for 3D visualization"""

        # Standard residential panel dimensions (feet)
        panel_width = 3.25
        panel_length = 5.5
        panel_spacing = 0.5

        # Calculate grid
        panels_per_row = int((roof_width - panel_spacing) / (panel_width + panel_spacing))
        panel_rows = int((roof_length - panel_spacing) / (panel_length + panel_spacing))

        # Get shading factor from roof analysis
        base_shading = roof_analysis.get('shading_analysis', {}).get('shadow_percentage', 10) / 100

        layout = []
        panel_id = 1

        for row in range(panel_rows):
            for col in range(panels_per_row):
                x_pos = (col - panels_per_row / 2) * (panel_width + panel_spacing)
                z_pos = (row - panel_rows / 2) * (panel_length + panel_spacing)

                # Calculate position-based efficiency and shading
                distance_from_center = ((row - panel_rows/2)**2 + (col - panels_per_row/2)**2)**0.5
                efficiency = 0.95 - (distance_from_center * 0.005)  # Slight efficiency variation
                shading_factor = max(0.7, 1.0 - base_shading - (distance_from_center * 0.01))

                panel = {
                    "id": panel_id,
                    "position": {"x": x_pos, "y": 0.1, "z": z_pos},
                    "rotation": {"x": 0, "y": 0, "z": 0},
                    "dimensions": {
                        "width": panel_width,
                        "length": panel_length,
                        "thickness": 0.15
                    },
                    "efficiency": efficiency,
                    "shading_factor": shading_factor
                }

                layout.append(panel)
                panel_id += 1

        return layout
    
    def _get_panel_specifications(self) -> Dict[str, Any]:
        """Get solar panel specifications for 3D model"""
        return {
            "type": "Monocrystalline",
            "power_rating": 350,  # watts
            "efficiency": 0.20,
            "dimensions": {
                "width": 3.25,  # feet
                "length": 5.5,  # feet
                "thickness": 0.15  # feet
            },
            "color": "#1a1a2e",
            "material": "silicon"
        }
    
    def _generate_sun_path_data(self, solar_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate sun path data for visualization"""
        import math
        
        latitude = solar_data.get('location', {}).get('latitude', 40.0)
        
        # Generate sun positions for different times and seasons
        sun_positions = {}
        
        for season in ['spring', 'summer', 'fall', 'winter']:
            sun_positions[season] = []
            
            # Declination angle for each season
            declination = {'spring': 0, 'summer': 23.5, 'fall': 0, 'winter': -23.5}[season]
            
            for hour in range(6, 19):  # 6 AM to 6 PM
                hour_angle = 15 * (hour - 12)  # degrees
                
                # Calculate sun elevation and azimuth
                elevation = math.asin(
                    math.sin(math.radians(latitude)) * math.sin(math.radians(declination)) +
                    math.cos(math.radians(latitude)) * math.cos(math.radians(declination)) * 
                    math.cos(math.radians(hour_angle))
                )
                
                azimuth = math.atan2(
                    math.sin(math.radians(hour_angle)),
                    math.cos(math.radians(hour_angle)) * math.sin(math.radians(latitude)) -
                    math.tan(math.radians(declination)) * math.cos(math.radians(latitude))
                )
                
                sun_positions[season].append({
                    "hour": hour,
                    "elevation": math.degrees(elevation),
                    "azimuth": math.degrees(azimuth),
                    "intensity": max(0, math.sin(elevation))
                })
        
        return {
            "positions": sun_positions,
            "latitude": latitude,
            "path_color": "#FFD700",
            "sun_size": 5
        }
    
    def _calculate_shadow_patterns(self, roof_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate shadow patterns for visualization"""
        
        obstacles = roof_analysis.get('obstacles', [])
        shading_analysis = roof_analysis.get('shading_analysis', {})
        
        shadow_data = {
            "patterns": [],
            "coverage_percentage": shading_analysis.get('shadow_percentage', 15),
            "dynamic_shadows": True
        }
        
        # Generate shadow patterns for each obstacle
        for i, obstacle in enumerate(obstacles):
            shadow_pattern = {
                "source_id": i,
                "shadow_length": obstacle.get('height', 5) * 2,  # Rough estimation
                "shadow_width": obstacle.get('width', 3),
                "direction": "southeast",  # Typical shadow direction
                "intensity": 0.7
            }
            shadow_data["patterns"].append(shadow_pattern)
        
        return shadow_data
    
    def _generate_efficiency_heatmap(self, roof_analysis: Dict[str, Any]) -> List[List[float]]:
        """Generate efficiency heatmap data for visualization"""
        
        # Create a simple grid-based efficiency map
        grid_size = 10
        efficiency_map = []
        
        base_efficiency = 0.85
        shading_impact = roof_analysis.get('shading_analysis', {}).get('shadow_percentage', 15) / 100
        
        for i in range(grid_size):
            row = []
            for j in range(grid_size):
                # Simulate efficiency variation across roof
                distance_from_center = ((i - grid_size/2)**2 + (j - grid_size/2)**2)**0.5
                efficiency = base_efficiency - (distance_from_center * 0.02) - (shading_impact * 0.5)
                efficiency = max(0.1, min(1.0, efficiency))  # Clamp between 0.1 and 1.0
                row.append(efficiency)
            efficiency_map.append(row)
        
        return efficiency_map
    
    def _orientation_to_degrees(self, orientation: str) -> float:
        """Convert orientation string to degrees"""
        orientations = {
            'North': 0, 'Northeast': 45, 'East': 90, 'Southeast': 135,
            'South': 180, 'Southwest': 225, 'West': 270, 'Northwest': 315
        }
        return orientations.get(orientation, 180)  # Default to South

# Import numpy for calculations
try:
    import numpy as np
except ImportError:
    # Fallback for basic math operations
    import math

    class NumpyFallback:
        @staticmethod
        def tan(x):
            return math.tan(x)
        @staticmethod
        def radians(x):
            return math.radians(x)

    np = NumpyFallback()