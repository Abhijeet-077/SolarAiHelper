// 3D Neural Network Background with Three.js
class Neural3DBackground {
    constructor() {
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.neurons = [];
        this.connections = [];
        this.particles = [];
        this.animationId = null;
        this.mouseX = 0;
        this.mouseY = 0;
        
        // Configuration
        this.config = {
            neuronCount: 75,
            layers: 5,
            layerSpacing: 8,
            connectionDistance: 12,
            particleCount: 150,
            colors: {
                neurons: [0x00ffff, 0x00ff00, 0xff00ff, 0xffff00],
                connections: 0xffffff,
                particles: 0xffffff
            },
            performance: {
                targetFPS: 60,
                adaptiveQuality: true,
                lodDistance: 50
            }
        };
        
        this.init();
    }

    async init() {
        try {
            // Load Three.js from CDN
            await this.loadThreeJS();
            
            this.createScene();
            this.createCamera();
            this.createRenderer();
            this.createLights();
            this.createControls();
            this.generateNeurons();
            this.generateConnections();
            this.generateParticles();
            this.bindEvents();
            this.animate();
            
            console.log('🧠 3D Neural Network Background initialized');
        } catch (error) {
            console.error('Failed to initialize 3D neural background:', error);
            this.fallbackTo2D();
        }
    }

    async loadThreeJS() {
        return new Promise((resolve, reject) => {
            if (window.THREE) {
                resolve();
                return;
            }

            const script = document.createElement('script');
            script.src = 'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js';
            script.onload = () => {
                // Load OrbitControls
                const controlsScript = document.createElement('script');
                controlsScript.src = 'https://threejs.org/examples/js/controls/OrbitControls.js';
                controlsScript.onload = resolve;
                controlsScript.onerror = () => {
                    // Fallback: try alternative CDN
                    const fallbackScript = document.createElement('script');
                    fallbackScript.src = 'https://cdn.skypack.dev/three@0.128.0/examples/jsm/controls/OrbitControls.js';
                    fallbackScript.onload = resolve;
                    fallbackScript.onerror = reject;
                    document.head.appendChild(fallbackScript);
                };
                document.head.appendChild(controlsScript);
            };
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    createScene() {
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x000000);
        this.scene.fog = new THREE.Fog(0x000000, 50, 200);
    }

    createCamera() {
        this.camera = new THREE.PerspectiveCamera(
            75,
            window.innerWidth / window.innerHeight,
            0.1,
            1000
        );
        this.camera.position.set(0, 0, 30);
    }

    createRenderer() {
        this.renderer = new THREE.WebGLRenderer({ 
            antialias: true, 
            alpha: true,
            powerPreference: "high-performance"
        });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        
        // Add to DOM
        this.renderer.domElement.style.position = 'fixed';
        this.renderer.domElement.style.top = '0';
        this.renderer.domElement.style.left = '0';
        this.renderer.domElement.style.zIndex = '-1';
        this.renderer.domElement.style.pointerEvents = 'none';
        
        document.body.insertBefore(this.renderer.domElement, document.body.firstChild);
    }

    createLights() {
        // Ambient light
        const ambientLight = new THREE.AmbientLight(0x404040, 0.3);
        this.scene.add(ambientLight);

        // Point lights
        const light1 = new THREE.PointLight(0x00ffff, 1, 100);
        light1.position.set(20, 20, 20);
        this.scene.add(light1);

        const light2 = new THREE.PointLight(0x00ff00, 0.8, 80);
        light2.position.set(-20, -20, 20);
        this.scene.add(light2);

        const light3 = new THREE.PointLight(0xff00ff, 0.6, 60);
        light3.position.set(0, 20, -20);
        this.scene.add(light3);
    }

    createControls() {
        if (THREE.OrbitControls) {
            this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
            this.controls.enableDamping = true;
            this.controls.dampingFactor = 0.05;
            this.controls.enableZoom = true;
            this.controls.minDistance = 10;
            this.controls.maxDistance = 100;
            this.controls.autoRotate = true;
            this.controls.autoRotateSpeed = 0.5;
        }
    }

    generateNeurons() {
        this.neurons = [];
        const { neuronCount, layers, layerSpacing, colors } = this.config;
        
        for (let layer = 0; layer < layers; layer++) {
            const neuronsInLayer = Math.floor(neuronCount / layers) + (layer === 0 ? neuronCount % layers : 0);
            
            for (let i = 0; i < neuronsInLayer; i++) {
                const neuron = this.createNeuron(layer, i, neuronsInLayer);
                this.neurons.push(neuron);
                this.scene.add(neuron.mesh);
            }
        }
    }

    createNeuron(layer, index, totalInLayer) {
        const geometry = new THREE.SphereGeometry(0.3 + Math.random() * 0.4, 16, 16);
        const color = this.config.colors.neurons[Math.floor(Math.random() * this.config.colors.neurons.length)];
        
        const material = new THREE.MeshPhongMaterial({
            color: color,
            emissive: color,
            emissiveIntensity: 0.2,
            shininess: 100,
            transparent: true,
            opacity: 0.8
        });

        const mesh = new THREE.Mesh(geometry, material);
        
        // Position in layer
        const angle = (index / totalInLayer) * Math.PI * 2;
        const radius = 8 + Math.random() * 4;
        const z = (layer - this.config.layers / 2) * this.config.layerSpacing;
        
        mesh.position.set(
            Math.cos(angle) * radius + (Math.random() - 0.5) * 4,
            Math.sin(angle) * radius + (Math.random() - 0.5) * 4,
            z + (Math.random() - 0.5) * 2
        );

        return {
            mesh: mesh,
            originalPosition: mesh.position.clone(),
            velocity: new THREE.Vector3(
                (Math.random() - 0.5) * 0.02,
                (Math.random() - 0.5) * 0.02,
                (Math.random() - 0.5) * 0.01
            ),
            pulse: Math.random() * Math.PI * 2,
            pulseSpeed: 0.01 + Math.random() * 0.02,
            layer: layer,
            connections: []
        };
    }

    generateConnections() {
        this.connections = [];
        const { connectionDistance } = this.config;

        this.neurons.forEach((neuron, i) => {
            let connectionCount = 0;
            const maxConnections = 3;

            this.neurons.forEach((otherNeuron, j) => {
                if (i !== j && connectionCount < maxConnections) {
                    const distance = neuron.mesh.position.distanceTo(otherNeuron.mesh.position);
                    
                    if (distance < connectionDistance) {
                        const connection = this.createConnection(neuron, otherNeuron);
                        this.connections.push(connection);
                        this.scene.add(connection.line);
                        connectionCount++;
                    }
                }
            });
        });
    }

    createConnection(neuron1, neuron2) {
        const geometry = new THREE.BufferGeometry().setFromPoints([
            neuron1.mesh.position,
            neuron2.mesh.position
        ]);

        const material = new THREE.LineBasicMaterial({
            color: this.config.colors.connections,
            transparent: true,
            opacity: 0.3
        });

        const line = new THREE.Line(geometry, material);

        return {
            line: line,
            from: neuron1,
            to: neuron2,
            pulse: Math.random() * Math.PI * 2,
            pulseSpeed: 0.005 + Math.random() * 0.01,
            active: Math.random() < 0.3,
            dataFlow: 0
        };
    }

    generateParticles() {
        this.particles = [];
        const { particleCount } = this.config;

        for (let i = 0; i < particleCount; i++) {
            if (this.connections.length > 0) {
                const connection = this.connections[Math.floor(Math.random() * this.connections.length)];
                const particle = this.createParticle(connection);
                this.particles.push(particle);
                this.scene.add(particle.mesh);
            }
        }
    }

    createParticle(connection) {
        const geometry = new THREE.SphereGeometry(0.05, 8, 8);
        const material = new THREE.MeshBasicMaterial({
            color: this.config.colors.particles,
            transparent: true,
            opacity: 0.8
        });

        const mesh = new THREE.Mesh(geometry, material);

        return {
            mesh: mesh,
            connection: connection,
            progress: Math.random(),
            speed: 0.005 + Math.random() * 0.01,
            size: 0.05 + Math.random() * 0.03
        };
    }

    update() {
        // Update neurons
        this.neurons.forEach(neuron => {
            // Floating movement
            neuron.mesh.position.add(neuron.velocity);
            
            // Boundary constraints
            const bounds = 15;
            if (Math.abs(neuron.mesh.position.x) > bounds) neuron.velocity.x *= -1;
            if (Math.abs(neuron.mesh.position.y) > bounds) neuron.velocity.y *= -1;
            
            // Pulse effect
            neuron.pulse += neuron.pulseSpeed;
            const scale = 1 + Math.sin(neuron.pulse) * 0.2;
            neuron.mesh.scale.setScalar(scale);
            
            // Emissive intensity pulse
            neuron.mesh.material.emissiveIntensity = 0.2 + Math.sin(neuron.pulse) * 0.1;
        });

        // Update connections
        this.connections.forEach(connection => {
            // Update line geometry
            const positions = connection.line.geometry.attributes.position.array;
            positions[0] = connection.from.mesh.position.x;
            positions[1] = connection.from.mesh.position.y;
            positions[2] = connection.from.mesh.position.z;
            positions[3] = connection.to.mesh.position.x;
            positions[4] = connection.to.mesh.position.y;
            positions[5] = connection.to.mesh.position.z;
            connection.line.geometry.attributes.position.needsUpdate = true;

            // Pulse effect
            connection.pulse += connection.pulseSpeed;
            connection.line.material.opacity = 0.3 + Math.sin(connection.pulse) * 0.2;

            // Data flow
            if (connection.active) {
                connection.dataFlow += 0.02;
                if (connection.dataFlow > 1) {
                    connection.dataFlow = 0;
                    connection.active = Math.random() < 0.1;
                }
            } else {
                connection.active = Math.random() < 0.005;
            }
        });

        // Update particles
        this.particles.forEach(particle => {
            if (particle.connection) {
                particle.progress += particle.speed;
                
                if (particle.progress > 1) {
                    particle.progress = 0;
                    // Assign new random connection
                    if (this.connections.length > 0) {
                        particle.connection = this.connections[Math.floor(Math.random() * this.connections.length)];
                    }
                }

                // Interpolate position along connection
                const from = particle.connection.from.mesh.position;
                const to = particle.connection.to.mesh.position;
                particle.mesh.position.lerpVectors(from, to, particle.progress);
            }
        });

        // Update controls
        if (this.controls) {
            this.controls.update();
        }
    }

    render() {
        this.renderer.render(this.scene, this.camera);
    }

    animate() {
        this.update();
        this.render();
        this.animationId = requestAnimationFrame(() => this.animate());
    }

    bindEvents() {
        // Mouse tracking
        document.addEventListener('mousemove', (e) => {
            this.mouseX = (e.clientX / window.innerWidth) * 2 - 1;
            this.mouseY = -(e.clientY / window.innerHeight) * 2 + 1;
        });

        // Resize handling
        window.addEventListener('resize', () => {
            this.camera.aspect = window.innerWidth / window.innerHeight;
            this.camera.updateProjectionMatrix();
            this.renderer.setSize(window.innerWidth, window.innerHeight);
        });

        // Visibility change
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                if (this.animationId) {
                    cancelAnimationFrame(this.animationId);
                }
            } else {
                this.animate();
            }
        });
    }

    fallbackTo2D() {
        console.log('Falling back to 2D neural network');
        // Initialize 2D version as fallback
        if (window.NeuralNetworkBackground) {
            window.neuralNetwork = new NeuralNetworkBackground();
        }
    }

    destroy() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        
        if (this.renderer) {
            this.renderer.domElement.remove();
            this.renderer.dispose();
        }
        
        // Clean up geometries and materials
        this.neurons.forEach(neuron => {
            neuron.mesh.geometry.dispose();
            neuron.mesh.material.dispose();
        });
        
        this.connections.forEach(connection => {
            connection.line.geometry.dispose();
            connection.line.material.dispose();
        });
        
        this.particles.forEach(particle => {
            particle.mesh.geometry.dispose();
            particle.mesh.material.dispose();
        });
    }
}

// Initialize 3D neural network background
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        window.neural3D = new Neural3DBackground();
        console.log('🌟 3D Neural Network Background loading...');
    }, 500);
});

// Export for manual control
window.Neural3DBackground = Neural3DBackground;
