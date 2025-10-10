// Mobile menu toggle functionality
const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
const navLinks = document.querySelector('.nav-links');

if (mobileMenuToggle) {
    mobileMenuToggle.addEventListener('click', function() {
        navLinks.classList.toggle('active');
        // Animate hamburger menu
        this.classList.toggle('active');
        // Prevent body scroll on iOS when menu is open
        document.body.classList.toggle('menu-open');
    });
}

// Close mobile menu when clicking outside
document.addEventListener('click', function(event) {
    if (navLinks && navLinks.classList.contains('active')) {
        const isClickInsideNav = navLinks.contains(event.target);
        const isClickOnToggle = mobileMenuToggle && mobileMenuToggle.contains(event.target);
        
        if (!isClickInsideNav && !isClickOnToggle) {
            navLinks.classList.remove('active');
            if (mobileMenuToggle) {
                mobileMenuToggle.classList.remove('active');
            }
            document.body.classList.remove('menu-open');
        }
    }
});

// Enhanced smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        
        // Close mobile menu if open
        if (navLinks.classList.contains('active')) {
            navLinks.classList.remove('active');
            if (mobileMenuToggle) {
                mobileMenuToggle.classList.remove('active');
            }
            document.body.classList.remove('menu-open');
        }
        
        const targetId = this.getAttribute('href');
        const targetElement = document.querySelector(targetId);
        
        if (!targetElement) return;
        
        // iOS-friendly scrolling
        const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
        
        if (isIOS) {
            // Use native smooth scroll on iOS for better performance
            targetElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
        } else {
            // Custom smooth scroll for other devices
            const targetPosition = targetElement.getBoundingClientRect().top + window.pageYOffset;
            const startPosition = window.pageYOffset;
            const distance = targetPosition - startPosition;
            const duration = 800; // ms
            let start = null;
            
            function step(timestamp) {
                if (!start) start = timestamp;
                const progress = timestamp - start;
                const percentage = Math.min(progress / duration, 1);
                
                // Easing function for smooth acceleration and deceleration
                const easing = t => t < 0.5 ? 4 * t * t * t : (t - 1) * (2 * t - 2) * (2 * t - 2) + 1;
                
                window.scrollTo(0, startPosition + distance * easing(percentage));
                
                if (progress < duration) {
                    window.requestAnimationFrame(step);
                }
            }
            
            window.requestAnimationFrame(step);
        }
    });
});

// Update scroll event listener for navbar
window.addEventListener('scroll', function() {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 50) {
        navbar.style.background = '#1a1a1a';
    } else {
        navbar.style.background = '#1a1a1a';
    }
});

// Section visibility observer with more subtle transitions
const sections = document.querySelectorAll('section');

const observerOptions = {
    root: null,
    rootMargin: '-10% 0px',
    threshold: [0.15, 0.3, 0.5, 0.7, 0.9] // Multiple thresholds for smoother transitions
};

const sectionObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        // Only update navigation when section is at least 50% visible
        if (entry.isIntersecting && entry.intersectionRatio >= 0.5) {
            updateNavigation(entry.target.id);
        }
    });
}, observerOptions);

// Observe all sections
sections.forEach(section => {
    sectionObserver.observe(section);
});

// Update navigation highlighting
function updateNavigation(currentSection) {
    document.querySelectorAll('.nav-links a').forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${currentSection}`) {
            link.classList.add('active');
        }
    });
}

// Add scroll progress indicator
const scrollProgress = document.createElement('div');
scrollProgress.className = 'scroll-progress';
document.body.appendChild(scrollProgress);

window.addEventListener('scroll', () => {
    const windowHeight = document.documentElement.clientHeight;
    const fullHeight = document.documentElement.scrollHeight;
    const scrolled = window.scrollY;
    
    const progress = (scrolled / (fullHeight - windowHeight)) * 100;
    scrollProgress.style.width = `${progress}%`;
});


// Enhanced interactions for project cards with iOS touch support
document.addEventListener('DOMContentLoaded', () => {
    const projectCards = document.querySelectorAll('.project-card');
    
    // Detect if device is iOS
    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
    const isTouchDevice = ('ontouchstart' in window) || (navigator.maxTouchPoints > 0);
    
    projectCards.forEach(card => {
        // Enhance hover effects (only for non-touch devices)
        if (!isTouchDevice) {
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'translateY(-8px)';
                
                // Add subtle transition to tech stack icons
                const techIcons = card.querySelectorAll('.tech-stack i');
                techIcons.forEach((icon, index) => {
                    setTimeout(() => {
                        icon.style.transform = 'scale(1.15)';
                    }, index * 50);
                });
            });
            
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'translateY(0)';
                
                // Reset tech stack icons
                const techIcons = card.querySelectorAll('.tech-stack i');
                techIcons.forEach(icon => {
                    icon.style.transform = 'scale(1)';
                });
            });
        }
    });
    
    // Fix iOS viewport height issue
    if (isIOS) {
        const setVH = () => {
            const vh = window.innerHeight * 0.01;
            document.documentElement.style.setProperty('--vh', `${vh}px`);
        };
        setVH();
        window.addEventListener('resize', setVH);
        window.addEventListener('orientationchange', setVH);
    }
}); 