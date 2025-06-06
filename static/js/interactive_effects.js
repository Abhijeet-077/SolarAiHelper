// Interactive Effects for Solar AI Platform

// Particle System for Background
class ParticleSystem {
    constructor() {
        this.particles = [];
        this.canvas = null;
        this.ctx = null;
        this.init();
    }

    init() {
        // Create canvas for particles
        this.canvas = document.createElement('canvas');
        this.canvas.style.position = 'fixed';
        this.canvas.style.top = '0';
        this.canvas.style.left = '0';
        this.canvas.style.width = '100%';
        this.canvas.style.height = '100%';
        this.canvas.style.zIndex = '-1';
        this.canvas.style.pointerEvents = 'none';
        document.body.appendChild(this.canvas);

        this.ctx = this.canvas.getContext('2d');
        this.resize();
        this.createParticles();
        this.animate();

        window.addEventListener('resize', () => this.resize());
    }

    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }

    createParticles() {
        const particleCount = Math.floor((this.canvas.width * this.canvas.height) / 15000);
        
        for (let i = 0; i < particleCount; i++) {
            this.particles.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                vx: (Math.random() - 0.5) * 0.5,
                vy: (Math.random() - 0.5) * 0.5,
                size: Math.random() * 3 + 1,
                opacity: Math.random() * 0.5 + 0.2,
                color: this.getRandomColor()
            });
        }
    }

    getRandomColor() {
        const colors = ['#FFD700', '#FFA500', '#4ECDC4', '#FF6B6B', '#A8E6CF'];
        return colors[Math.floor(Math.random() * colors.length)];
    }

    animate() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        this.particles.forEach(particle => {
            // Update position
            particle.x += particle.vx;
            particle.y += particle.vy;

            // Wrap around edges
            if (particle.x < 0) particle.x = this.canvas.width;
            if (particle.x > this.canvas.width) particle.x = 0;
            if (particle.y < 0) particle.y = this.canvas.height;
            if (particle.y > this.canvas.height) particle.y = 0;

            // Draw particle
            this.ctx.beginPath();
            this.ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
            this.ctx.fillStyle = particle.color;
            this.ctx.globalAlpha = particle.opacity;
            this.ctx.fill();
        });

        this.ctx.globalAlpha = 1;
        requestAnimationFrame(() => this.animate());
    }
}

// Enhanced Button Effects
class ButtonEffects {
    static init() {
        // Add ripple effect to buttons
        document.addEventListener('click', (e) => {
            if (e.target.tagName === 'BUTTON' || e.target.closest('button')) {
                this.createRipple(e);
            }
        });

        // Add hover sound effects (optional)
        document.querySelectorAll('button').forEach(button => {
            button.addEventListener('mouseenter', () => {
                button.style.transform = 'translateY(-2px)';
            });
            
            button.addEventListener('mouseleave', () => {
                button.style.transform = 'translateY(0)';
            });
        });
    }

    static createRipple(event) {
        const button = event.target.closest('button');
        if (!button) return;

        const ripple = document.createElement('span');
        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;

        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        ripple.classList.add('ripple');

        button.appendChild(ripple);

        setTimeout(() => {
            ripple.remove();
        }, 600);
    }
}

// Progress Animation
class ProgressAnimator {
    static animateProgress(element, targetWidth, duration = 1000) {
        const startWidth = 0;
        const startTime = performance.now();

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function (ease-out)
            const easeOut = 1 - Math.pow(1 - progress, 3);
            const currentWidth = startWidth + (targetWidth - startWidth) * easeOut;
            
            element.style.width = currentWidth + '%';
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };

        requestAnimationFrame(animate);
    }

    static pulseElement(element, duration = 2000) {
        element.style.animation = `pulse ${duration}ms infinite`;
    }
}

// Card Hover Effects
class CardEffects {
    static init() {
        document.querySelectorAll('.metric-card, .analysis-card').forEach(card => {
            card.addEventListener('mouseenter', (e) => {
                this.addHoverEffect(e.target);
            });

            card.addEventListener('mouseleave', (e) => {
                this.removeHoverEffect(e.target);
            });
        });
    }

    static addHoverEffect(card) {
        card.style.transform = 'translateY(-10px) scale(1.02)';
        card.style.boxShadow = '0 20px 40px rgba(0, 0, 0, 0.2)';
        
        // Add glow effect
        card.style.filter = 'brightness(1.1)';
    }

    static removeHoverEffect(card) {
        card.style.transform = 'translateY(0) scale(1)';
        card.style.boxShadow = '0 8px 25px rgba(0, 0, 0, 0.1)';
        card.style.filter = 'brightness(1)';
    }
}

// Smooth Scrolling
class SmoothScroll {
    static init() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }
}

// Loading Animations
class LoadingAnimations {
    static showSpinner(container) {
        const spinner = document.createElement('div');
        spinner.className = 'loading-spinner';
        spinner.innerHTML = '<div class="spinner-inner"></div>';
        container.appendChild(spinner);
        return spinner;
    }

    static hideSpinner(spinner) {
        if (spinner && spinner.parentNode) {
            spinner.parentNode.removeChild(spinner);
        }
    }

    static typeWriter(element, text, speed = 50) {
        let i = 0;
        element.innerHTML = '';
        
        const timer = setInterval(() => {
            if (i < text.length) {
                element.innerHTML += text.charAt(i);
                i++;
            } else {
                clearInterval(timer);
            }
        }, speed);
    }
}

// Notification System
class NotificationSystem {
    static show(message, type = 'info', duration = 3000) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-icon">${this.getIcon(type)}</span>
                <span class="notification-message">${message}</span>
                <button class="notification-close">&times;</button>
            </div>
        `;

        document.body.appendChild(notification);

        // Animate in
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);

        // Auto remove
        setTimeout(() => {
            this.hide(notification);
        }, duration);

        // Manual close
        notification.querySelector('.notification-close').addEventListener('click', () => {
            this.hide(notification);
        });
    }

    static hide(notification) {
        notification.classList.remove('show');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }

    static getIcon(type) {
        const icons = {
            'success': '✅',
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️'
        };
        return icons[type] || icons.info;
    }
}

// Initialize all effects when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize particle system
    new ParticleSystem();
    
    // Initialize button effects
    ButtonEffects.init();
    
    // Initialize card effects
    CardEffects.init();
    
    // Initialize smooth scrolling
    SmoothScroll.init();
    
    console.log('🌞 Solar AI Platform interactive effects loaded!');
});

// Export for use in other scripts
window.SolarAI = {
    ParticleSystem,
    ButtonEffects,
    ProgressAnimator,
    CardEffects,
    LoadingAnimations,
    NotificationSystem
};
