// Resume page interactive elements
document.addEventListener('DOMContentLoaded', function() {
    // Initialize AOS animations
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 800,
            easing: 'ease-in-out',
            once: true
        });
    }

    // Animate skill bars
    setTimeout(() => {
        document.querySelectorAll('.skill-bar').forEach(bar => {
            const width = bar.getAttribute('data-width');
            bar.style.width = width;
        });
    }, 500);
    
    // Initialize skills radar chart
    if (document.getElementById('skillsRadarChart')) {
        initSkillsChart();
    }
    
    // Setup dark mode handler for chart
    const darkModeToggle = document.getElementById('darkModeToggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', updateChartColors);
    }
    
    // Add hover effects to timeline items
    const timelineItems = document.querySelectorAll('.timeline-item');
    timelineItems.forEach((item, index) => {
        item.addEventListener('mouseenter', () => {
            item.querySelector('.timeline-content').classList.add('scale-105');
            item.querySelector('.timeline-dot').classList.add('bg-blue-400');
        });
        
        item.addEventListener('mouseleave', () => {
            item.querySelector('.timeline-content').classList.remove('scale-105');
            item.querySelector('.timeline-dot').classList.remove('bg-blue-400');
        });
    });
    
    // Add parallax scroll effect to sections
    window.addEventListener('scroll', function() {
        const scrolled = window.pageYOffset;
        const sections = document.querySelectorAll('[data-aos]');
        
        sections.forEach(section => {
            const speed = 0.3;
            if (!section.classList.contains('aos-animate')) {
                section.style.transform = `translateY(${scrolled * speed}px)`;
            }
        });
    });
    
    // Add typing animation to the resume title
    const resumeTitleElement = document.querySelector('.resume-title');
    if (resumeTitleElement) {
        const text = resumeTitleElement.textContent;
        resumeTitleElement.textContent = '';
        
        let i = 0;
        const typeWriter = () => {
            if (i < text.length) {
                resumeTitleElement.textContent += text.charAt(i);
                i++;
                setTimeout(typeWriter, 100);
            }
        };
        
        setTimeout(typeWriter, 500);
    }
    
    // Enhance tag hover effects
    document.querySelectorAll('.tag').forEach(tag => {
        tag.addEventListener('mouseenter', function() {
            this.classList.add('scale-110');
        });
        
        tag.addEventListener('mouseleave', function() {
            this.classList.remove('scale-110');
        });
    });
    
    // Add click animation to download button
    const downloadButtons = document.querySelectorAll('a[href="/download-resume"]');
    downloadButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            this.classList.add('animate-pulse');
            setTimeout(() => {
                this.classList.remove('animate-pulse');
            }, 500);
        });
    });
});

// Initialize the radar chart for skills
function initSkillsChart() {
    const ctx = document.getElementById('skillsRadarChart').getContext('2d');
    
    // Check if Chart object exists
    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not loaded');
        return;
    }
    
    // Create a gradient background
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(59, 130, 246, 0.3)');
    gradient.addColorStop(1, 'rgba(147, 51, 234, 0.1)');
    
    window.skillsChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: [
                'Python',
                'Machine Learning',
                'Data Analysis',
                'Data Visualization',
                'Deep Learning',
                'NLP',
                'SQL',
                'Statistics'
            ],
            datasets: [{
                label: 'Skills Proficiency',
                data: [95, 90, 92, 88, 85, 82, 90, 85],
                backgroundColor: gradient,
                borderColor: 'rgba(59, 130, 246, 1)',
                pointBackgroundColor: 'rgba(59, 130, 246, 1)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgba(59, 130, 246, 1)',
                borderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        color: isDarkMode() ? '#f3f4f6' : '#374151',
                        font: {
                            size: 14,
                            weight: 'bold'
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Proficiency: ${context.raw}%`;
                        }
                    },
                    backgroundColor: isDarkMode() ? 'rgba(17, 24, 39, 0.8)' : 'rgba(255, 255, 255, 0.8)',
                    titleColor: isDarkMode() ? '#f3f4f6' : '#1f2937',
                    bodyColor: isDarkMode() ? '#f3f4f6' : '#1f2937',
                    borderColor: isDarkMode() ? '#f3f4f6' : '#e5e7eb',
                    borderWidth: 1,
                    padding: 10,
                    displayColors: false
                }
            },
            scales: {
                r: {
                    angleLines: {
                        color: isDarkMode() ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)',
                        lineWidth: 1
                    },
                    grid: {
                        color: isDarkMode() ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)',
                        circular: true
                    },
                    pointLabels: {
                        color: isDarkMode() ? '#f3f4f6' : '#374151',
                        font: {
                            size: 12,
                            weight: 'bold'
                        }
                    },
                    ticks: {
                        backdropColor: 'transparent',
                        color: isDarkMode() ? '#f3f4f6' : '#374151',
                        z: 100,
                        font: {
                            size: 10
                        }
                    },
                    suggestedMin: 50,
                    suggestedMax: 100,
                    beginAtZero: false
                }
            },
            animation: {
                duration: 2000,
                easing: 'easeOutQuart'
            },
            elements: {
                line: {
                    tension: 0.2 // Smooth the lines slightly
                }
            }
        }
    });
    
    // Add animation to the chart on hover
    const canvas = document.getElementById('skillsRadarChart');
    canvas.addEventListener('mouseenter', () => {
        window.skillsChart.options.scales.r.ticks.font.size = 12;
        window.skillsChart.options.scales.r.pointLabels.font.size = 14;
        window.skillsChart.update();
    });
    
    canvas.addEventListener('mouseleave', () => {
        window.skillsChart.options.scales.r.ticks.font.size = 10;
        window.skillsChart.options.scales.r.pointLabels.font.size = 12;
        window.skillsChart.update();
    });
}

// Check if dark mode is currently enabled
function isDarkMode() {
    return document.documentElement.classList.contains('dark');
}

// Update chart colors when switching between light and dark mode
function updateChartColors() {
    if (!window.skillsChart) return;
    
    const isDark = isDarkMode();
    
    window.skillsChart.options.plugins.legend.labels.color = isDark ? '#f3f4f6' : '#374151';
    window.skillsChart.options.scales.r.angleLines.color = isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
    window.skillsChart.options.scales.r.grid.color = isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
    window.skillsChart.options.scales.r.pointLabels.color = isDark ? '#f3f4f6' : '#374151';
    window.skillsChart.options.scales.r.ticks.color = isDark ? '#f3f4f6' : '#374151';
    window.skillsChart.options.plugins.tooltip.backgroundColor = isDark ? 'rgba(17, 24, 39, 0.8)' : 'rgba(255, 255, 255, 0.8)';
    window.skillsChart.options.plugins.tooltip.titleColor = isDark ? '#f3f4f6' : '#1f2937';
    window.skillsChart.options.plugins.tooltip.bodyColor = isDark ? '#f3f4f6' : '#1f2937';
    window.skillsChart.options.plugins.tooltip.borderColor = isDark ? '#f3f4f6' : '#e5e7eb';
    
    window.skillsChart.update();
} 