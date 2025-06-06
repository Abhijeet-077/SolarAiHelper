// Neural Network Animated Background Engine
class NeuralNetworkBackground {
    constructor() {
        this.container = null;
        this.canvas = null;
        this.ctx = null;
        this.nodes = [];
        this.connections = [];
        this.particles = [];
        this.mouseX = 0;
        this.mouseY = 0;
        this.animationId = null;
        
        // Configuration
        this.config = {
            nodeCount: 50,
            maxConnections: 3,
            connectionDistance: 150,
            particleCount: 20,
            colors: {
                nodes: ['#00ffff', '#00ff00', '#ff00ff', '#ffff00'],
                connections: '#ffffff',
                particles: '#ffffff'
            },
            animation: {
                nodeSpeed: 0.5,
                pulseSpeed: 0.02,
                particleSpeed: 2
            }
        };
        
        this.init();
    }

    init() {
        this.createContainer();
        this.createCanvas();
        this.generateNodes();
        this.generateConnections();
        this.generateParticles();
        this.bindEvents();
        this.animate();
    }

    createContainer() {
        // Remove existing neural background
        const existing = document.querySelector('.neural-background');
        if (existing) {
            existing.remove();
        }

        // Create main container
        this.container = document.createElement('div');
        this.container.className = 'neural-background';
        document.body.insertBefore(this.container, document.body.firstChild);

        // Add ambient glow effects
        for (let i = 0; i < 5; i++) {
            const glow = document.createElement('div');
            glow.className = 'neural-glow';
            glow.style.width = `${200 + Math.random() * 300}px`;
            glow.style.height = glow.style.width;
            glow.style.left = `${Math.random() * 100}%`;
            glow.style.top = `${Math.random() * 100}%`;
            glow.style.animationDelay = `${Math.random() * 6}s`;
            this.container.appendChild(glow);
        }
    }

    createCanvas() {
        this.canvas = document.createElement('canvas');
        this.canvas.className = 'neural-canvas';
        this.ctx = this.canvas.getContext('2d');
        this.container.appendChild(this.canvas);
        
        this.resizeCanvas();
    }

    resizeCanvas() {
        const rect = this.container.getBoundingClientRect();
        this.canvas.width = rect.width;
        this.canvas.height = rect.height;
        this.canvas.style.width = rect.width + 'px';
        this.canvas.style.height = rect.height + 'px';
    }

    generateNodes() {
        this.nodes = [];
        const { nodeCount, colors } = this.config;

        for (let i = 0; i < nodeCount; i++) {
            const node = {
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                vx: (Math.random() - 0.5) * this.config.animation.nodeSpeed,
                vy: (Math.random() - 0.5) * this.config.animation.nodeSpeed,
                radius: 3 + Math.random() * 8,
                color: colors.nodes[Math.floor(Math.random() * colors.nodes.length)],
                pulse: Math.random() * Math.PI * 2,
                pulseSpeed: 0.01 + Math.random() * 0.02,
                opacity: 0.6 + Math.random() * 0.4,
                layer: Math.floor(Math.random() * 3)
            };
            this.nodes.push(node);
        }
    }

    generateConnections() {
        this.connections = [];
        const { maxConnections, connectionDistance } = this.config;

        this.nodes.forEach((node, i) => {
            let connectionCount = 0;
            
            this.nodes.forEach((otherNode, j) => {
                if (i !== j && connectionCount < maxConnections) {
                    const distance = this.getDistance(node, otherNode);
                    
                    if (distance < connectionDistance) {
                        const connection = {
                            from: node,
                            to: otherNode,
                            opacity: Math.max(0.1, 1 - distance / connectionDistance),
                            pulse: Math.random() * Math.PI * 2,
                            pulseSpeed: 0.005 + Math.random() * 0.01,
                            active: Math.random() < 0.3,
                            dataFlow: 0
                        };
                        this.connections.push(connection);
                        connectionCount++;
                    }
                }
            });
        });
    }

    generateParticles() {
        this.particles = [];
        const { particleCount } = this.config;

        for (let i = 0; i < particleCount; i++) {
            if (this.connections.length > 0) {
                const connection = this.connections[Math.floor(Math.random() * this.connections.length)];
                const particle = {
                    connection: connection,
                    progress: Math.random(),
                    speed: 0.005 + Math.random() * 0.01,
                    size: 2 + Math.random() * 3,
                    opacity: 0.8,
                    color: this.config.colors.particles
                };
                this.particles.push(particle);
            }
        }
    }

    getDistance(node1, node2) {
        const dx = node1.x - node2.x;
        const dy = node1.y - node2.y;
        return Math.sqrt(dx * dx + dy * dy);
    }

    updateNodes() {
        this.nodes.forEach(node => {
            // Update position
            node.x += node.vx;
            node.y += node.vy;

            // Bounce off edges
            if (node.x < 0 || node.x > this.canvas.width) {
                node.vx *= -1;
                node.x = Math.max(0, Math.min(this.canvas.width, node.x));
            }
            if (node.y < 0 || node.y > this.canvas.height) {
                node.vy *= -1;
                node.y = Math.max(0, Math.min(this.canvas.height, node.y));
            }

            // Update pulse
            node.pulse += node.pulseSpeed;

            // Mouse interaction
            const mouseDistance = Math.sqrt(
                Math.pow(node.x - this.mouseX, 2) + 
                Math.pow(node.y - this.mouseY, 2)
            );
            
            if (mouseDistance < 100) {
                const force = (100 - mouseDistance) / 100;
                node.vx += (node.x - this.mouseX) * force * 0.001;
                node.vy += (node.y - this.mouseY) * force * 0.001;
            }
        });
    }

    updateConnections() {
        this.connections.forEach(connection => {
            connection.pulse += connection.pulseSpeed;
            
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
    }

    updateParticles() {
        this.particles.forEach(particle => {
            particle.progress += particle.speed;
            
            if (particle.progress > 1) {
                particle.progress = 0;
                // Assign new random connection
                if (this.connections.length > 0) {
                    particle.connection = this.connections[Math.floor(Math.random() * this.connections.length)];
                }
            }
        });
    }

    drawNodes() {
        this.nodes.forEach(node => {
            const pulseScale = 1 + Math.sin(node.pulse) * 0.3;
            const radius = node.radius * pulseScale;
            
            // Create gradient
            const gradient = this.ctx.createRadialGradient(
                node.x, node.y, 0,
                node.x, node.y, radius * 2
            );
            gradient.addColorStop(0, node.color + 'CC');
            gradient.addColorStop(0.7, node.color + '44');
            gradient.addColorStop(1, 'transparent');

            // Draw glow
            this.ctx.globalAlpha = node.opacity * 0.5;
            this.ctx.fillStyle = gradient;
            this.ctx.beginPath();
            this.ctx.arc(node.x, node.y, radius * 2, 0, Math.PI * 2);
            this.ctx.fill();

            // Draw core
            this.ctx.globalAlpha = node.opacity;
            this.ctx.fillStyle = node.color;
            this.ctx.beginPath();
            this.ctx.arc(node.x, node.y, radius * 0.5, 0, Math.PI * 2);
            this.ctx.fill();
        });
    }

    drawConnections() {
        this.connections.forEach(connection => {
            const pulseOpacity = connection.opacity * (0.5 + Math.sin(connection.pulse) * 0.3);
            
            this.ctx.globalAlpha = pulseOpacity;
            this.ctx.strokeStyle = connection.active ? '#00ff00' : this.config.colors.connections;
            this.ctx.lineWidth = connection.active ? 2 : 1;
            
            this.ctx.beginPath();
            this.ctx.moveTo(connection.from.x, connection.from.y);
            this.ctx.lineTo(connection.to.x, connection.to.y);
            this.ctx.stroke();

            // Draw data flow effect
            if (connection.active && connection.dataFlow > 0) {
                const flowX = connection.from.x + (connection.to.x - connection.from.x) * connection.dataFlow;
                const flowY = connection.from.y + (connection.to.y - connection.from.y) * connection.dataFlow;
                
                this.ctx.globalAlpha = 1;
                this.ctx.fillStyle = '#ffffff';
                this.ctx.beginPath();
                this.ctx.arc(flowX, flowY, 3, 0, Math.PI * 2);
                this.ctx.fill();
            }
        });
    }

    drawParticles() {
        this.particles.forEach(particle => {
            if (particle.connection) {
                const { from, to } = particle.connection;
                const x = from.x + (to.x - from.x) * particle.progress;
                const y = from.y + (to.y - from.y) * particle.progress;
                
                this.ctx.globalAlpha = particle.opacity;
                this.ctx.fillStyle = particle.color;
                this.ctx.beginPath();
                this.ctx.arc(x, y, particle.size, 0, Math.PI * 2);
                this.ctx.fill();
                
                // Add trail effect
                this.ctx.globalAlpha = particle.opacity * 0.3;
                this.ctx.beginPath();
                this.ctx.arc(x, y, particle.size * 2, 0, Math.PI * 2);
                this.ctx.fill();
            }
        });
    }

    render() {
        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw all elements
        this.drawConnections();
        this.drawNodes();
        this.drawParticles();
        
        // Reset global alpha
        this.ctx.globalAlpha = 1;
    }

    animate() {
        this.updateNodes();
        this.updateConnections();
        this.updateParticles();
        this.render();
        
        this.animationId = requestAnimationFrame(() => this.animate());
    }

    bindEvents() {
        // Mouse tracking for interaction
        document.addEventListener('mousemove', (e) => {
            const rect = this.canvas.getBoundingClientRect();
            this.mouseX = e.clientX - rect.left;
            this.mouseY = e.clientY - rect.top;
        });

        // Resize handling
        window.addEventListener('resize', () => {
            this.resizeCanvas();
            this.generateNodes();
            this.generateConnections();
        });

        // Visibility change handling
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

    destroy() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        if (this.container) {
            this.container.remove();
        }
    }
}

// Initialize neural network background when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Wait a moment for other scripts to load
    setTimeout(() => {
        window.neuralNetwork = new NeuralNetworkBackground();
        console.log('🧠 Neural Network Background initialized');
    }, 100);
});

// Export for manual control
window.NeuralNetworkBackground = NeuralNetworkBackground;
