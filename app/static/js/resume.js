// Resume page interactive elements
document.addEventListener('DOMContentLoaded', function() {
    // Initialize AOS animations
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 800,
            easing: 'ease-out',
            once: true
        });
    }

    // Fix recommendation section positioning on navigation
    ensureRecommendationSectionVisibility();
    
    // Add event listener to make sure recommendations are fully visible after animations
    window.addEventListener('load', function() {
        setTimeout(ensureRecommendationSectionVisibility, 500);
    });

    // Function to ensure the recommendations section is fully visible
    function ensureRecommendationSectionVisibility() {
        // Recommendation section is now commented out in the HTML, so we don't need to do anything
        // This function is kept for future use when the recommendations section is un-commented
        
        // Uncomment this when recommendations are added back to the template
        /*
        const recommendationsSection = document.querySelector('section.bg-gradient-to-r.from-indigo-600.to-blue-500');
        if (recommendationsSection) {
            // Ensure section has enough bottom margin
            recommendationsSection.classList.remove('mb-12');
            recommendationsSection.classList.add('mb-20');
            
            // Force recalculation of layout
            document.documentElement.style.setProperty('--recommendations-visibility', 'visible');
        }
        */
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

    // Animation for skill bars
    document.addEventListener('DOMContentLoaded', () => {
        // Animate skill bars
        setTimeout(() => {
            document.querySelectorAll('.skill-bar').forEach(bar => {
                const width = bar.getAttribute('data-width');
                bar.style.width = width;
            });
        }, 500);

        // Initialize the skills radar chart
        const ctx = document.getElementById('skillsRadarChart');
        if (ctx) {
            const isDarkMode = document.documentElement.classList.contains('dark');
            const textColor = isDarkMode ? '#f3f4f6' : '#374151';
            
            new Chart(ctx, {
                type: 'radar',
                data: {
                    labels: ['Python', 'Machine Learning', 'Data Analysis', 'Deep Learning', 'SQL', 'Statistics'],
                    datasets: [{
                        label: 'Skills',
                        data: [95, 90, 92, 85, 88, 89],
                        fill: true,
                        backgroundColor: 'rgba(59, 130, 246, 0.2)',
                        borderColor: 'rgba(59, 130, 246, 1)',
                        pointBackgroundColor: 'rgba(59, 130, 246, 1)',
                        pointBorderColor: '#fff',
                        pointHoverBackgroundColor: '#fff',
                        pointHoverBorderColor: 'rgba(59, 130, 246, 1)'
                    }]
                },
                options: {
                    scales: {
                        r: {
                            angleLines: {
                                color: isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
                            },
                            grid: {
                                color: isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
                            },
                            pointLabels: {
                                color: textColor
                            },
                            ticks: {
                                backdropColor: 'transparent',
                                color: textColor
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: false
                        }
                    }
                }
            });
        }

        // Add animation to timeline dots
        document.querySelectorAll('.timeline-dot').forEach(dot => {
            dot.addEventListener('click', () => {
                // Add pulse animation
                dot.classList.add('animate-pulse');
                
                // Find and highlight the associated content
                const content = dot.parentElement.querySelector('.timeline-content');
                if (content) {
                    content.style.transform = 'scale(1.05)';
                    content.style.boxShadow = '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)';
                    
                    // Reset after animation
                    setTimeout(() => {
                        dot.classList.remove('animate-pulse');
                        content.style.transform = '';
                        content.style.boxShadow = '';
                    }, 500);
                }
            });
        });

        // Chatbot functionality
        const chatButton = document.getElementById('chatButton');
        const chatWindow = document.getElementById('chatWindow');
        const closeChat = document.getElementById('closeChat');
        const chatInput = document.getElementById('chatInput');
        const sendMessage = document.getElementById('sendMessage');
        const chatMessages = document.getElementById('chatMessages');
        const chatSuggestions = document.querySelectorAll('.chat-suggestion');

        // Toggle chat window
        if (chatButton && chatWindow) {
            chatButton.addEventListener('click', () => {
                chatWindow.classList.toggle('hidden');
                // Add animation
                setTimeout(() => {
                    chatWindow.classList.toggle('scale-95');
                    chatWindow.classList.toggle('opacity-0');
                }, 10);
                // Focus input
                if (!chatWindow.classList.contains('hidden')) {
                    setTimeout(() => chatInput.focus(), 300);
                }
            });
        }

        // Close chat window
        if (closeChat && chatWindow) {
            closeChat.addEventListener('click', () => {
                chatWindow.classList.add('scale-95', 'opacity-0');
                setTimeout(() => {
                    chatWindow.classList.add('hidden');
                }, 300);
            });
        }

        // Send message function
        const sendChatMessage = () => {
            const message = chatInput.value.trim();
            if (message) {
                // Add user message to chat
                addMessage(message, 'user');
                chatInput.value = '';
                
                // Simulate typing indicator
                addTypingIndicator();
                
                // Simulate response (replace with actual API call in the future)
                setTimeout(() => {
                    // Remove typing indicator
                    const typingIndicator = document.querySelector('.typing-indicator');
                    if (typingIndicator) typingIndicator.remove();
                    
                    // Respond based on message content
                    respondToMessage(message);
                }, 1500);
            }
        };

        // Add message to chat
        const addMessage = (message, sender) => {
            const messageElement = document.createElement('div');
            messageElement.classList.add('flex', 'items-start', sender === 'user' ? 'justify-end' : '');
            
            const messageContent = document.createElement('div');
            messageContent.classList.add('p-3', 'rounded-lg', 'max-w-3/4');
            
            if (sender === 'user') {
                messageContent.classList.add('bg-blue-600', 'text-white');
            } else {
                messageContent.classList.add('bg-blue-100', 'dark:bg-blue-900', 'text-gray-800', 'dark:text-gray-200');
            }
            
            messageContent.textContent = message;
            messageElement.appendChild(messageContent);
            chatMessages.appendChild(messageElement);
            
            // Scroll to bottom
            chatMessages.scrollTop = chatMessages.scrollHeight;
        };

        // Add typing indicator
        const addTypingIndicator = () => {
            const typingElement = document.createElement('div');
            typingElement.classList.add('flex', 'items-start', 'typing-indicator');
            
            const typingContent = document.createElement('div');
            typingContent.classList.add('bg-gray-200', 'dark:bg-gray-700', 'p-3', 'rounded-lg', 'flex', 'space-x-1');
            
            for (let i = 0; i < 3; i++) {
                const dot = document.createElement('div');
                dot.classList.add('w-2', 'h-2', 'bg-gray-500', 'dark:bg-gray-400', 'rounded-full', 'animate-bounce');
                dot.style.animationDelay = `${i * 0.2}s`;
                typingContent.appendChild(dot);
            }
            
            typingElement.appendChild(typingContent);
            chatMessages.appendChild(typingElement);
            
            // Scroll to bottom
            chatMessages.scrollTop = chatMessages.scrollHeight;
        };

        // Respond to message (placeholder for future AI integration)
        const respondToMessage = (message) => {
            const lowerMessage = message.toLowerCase();
            let response = '';
            
            if (lowerMessage.includes('skill') || lowerMessage.includes('know') || lowerMessage.includes('can you')) {
                response = "I specialize in data science and machine learning with expertise in Python, TensorFlow, and data visualization. I've built models for predictive analytics and NLP, with experience in both supervised and unsupervised learning techniques.";
            } else if (lowerMessage.includes('project') || lowerMessage.includes('work') || lowerMessage.includes('portfolio')) {
                response = "I've worked on several significant projects including predictive models for business analytics, NLP systems for text classification, and interactive data visualizations. My GitHub has a collection of these projects with detailed documentation.";
            } else if (lowerMessage.includes('experience') || lowerMessage.includes('background') || lowerMessage.includes('history')) {
                response = "I have 4+ years of experience in data science roles, starting as a Data Analyst and progressing to Senior Data Scientist. I've worked across industries including finance, healthcare, and e-commerce, applying machine learning solutions to real-world problems.";
            } else if (lowerMessage.includes('education') || lowerMessage.includes('degree') || lowerMessage.includes('study')) {
                response = "I hold a Master's degree in Data Science and a Bachelor's in Computer Science. I've also completed specialized certifications in machine learning and deep learning from leading institutions.";
            } else if (lowerMessage.includes('contact') || lowerMessage.includes('email') || lowerMessage.includes('reach')) {
                response = "You can reach me via email at email@example.com or connect with me on LinkedIn. I'm always open to discussing interesting data science opportunities and collaborations.";
            } else {
                response = "Thanks for your message! I'm a placeholder chatbot for now. In the future, I'll be able to answer detailed questions about Matthew's portfolio, resume, and GitHub repositories. Is there something specific about Matthew's data science background you'd like to know?";
            }
            
            addMessage(response, 'bot');
        };

        // Send message on button click
        if (sendMessage) {
            sendMessage.addEventListener('click', sendChatMessage);
        }

        // Send message on Enter key
        if (chatInput) {
            chatInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    sendChatMessage();
                }
            });
        }

        // Handle suggestion buttons
        if (chatSuggestions) {
            chatSuggestions.forEach(button => {
                button.addEventListener('click', () => {
                    const suggestion = button.textContent.trim();
                    chatInput.value = suggestion;
                    sendChatMessage();
                });
            });
        }
    });
});

// Initialize the radar chart for skills
function initSkillsChart() {
    // Check if the skills and radar chart element exist
    if (!window.resumeData || !document.getElementById('skillsRadarChart')) {
        return;
    }

    try {
        // Get skills data from resume data object
        const technicalSkills = window.resumeData?.skills?.technical || [];
        let skillLabels = [];
        let skillValues = [];

        // Check if we have skills data
        if (technicalSkills.length > 0) {
            // Extract skill names and proficiency values
            skillLabels = technicalSkills.map(skill => skill.name);
            skillValues = technicalSkills.map(skill => skill.proficiency);
        } else {
            // Fallback to default labels and values
            skillLabels = ['Python', 'Machine Learning', 'Data Analysis', 'Data Visualization', 'SQL', 'Statistics', 'NLP'];
            skillValues = [95, 90, 92, 88, 85, 89, 83];
        }

        // Get the canvas and create the chart context
        const ctx = document.getElementById('skillsRadarChart').getContext('2d');
        const isDarkTheme = document.documentElement.classList.contains('dark');
        
        // Set colors based on theme
        const textColor = isDarkTheme ? '#f3f4f6' : '#374151';
        const gridColor = isDarkTheme ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
        
        // Create gradient background
        const backgroundColor = function(context) {
            const gradient = context.chart.ctx.createLinearGradient(0, 0, 0, 400);
            gradient.addColorStop(0, isDarkTheme ? 'rgba(59, 130, 246, 0.5)' : 'rgba(59, 130, 246, 0.2)');
            gradient.addColorStop(1, isDarkTheme ? 'rgba(37, 99, 235, 0.1)' : 'rgba(59, 130, 246, 0.05)');
            return gradient;
        };
        
        // Create the chart
        const radarChart = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: skillLabels,
                datasets: [{
                    label: 'Skills Proficiency',
                    data: skillValues,
                    fill: true,
                    backgroundColor: backgroundColor,
                    borderColor: isDarkTheme ? 'rgba(96, 165, 250, 1)' : 'rgba(59, 130, 246, 1)',
                    borderWidth: 2,
                    pointBackgroundColor: isDarkTheme ? 'rgba(96, 165, 250, 1)' : 'rgba(59, 130, 246, 1)',
                    pointBorderColor: isDarkTheme ? '#1e293b' : '#ffffff',
                    pointHoverBackgroundColor: '#ffffff',
                    pointHoverBorderColor: 'rgba(59, 130, 246, 1)',
                    pointRadius: 5,
                    pointHoverRadius: 7
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                aspectRatio: 1.5,
                scales: {
                    r: {
                        min: 50,
                        max: 100,
                        beginAtZero: false,
                        angleLines: {
                            color: gridColor
                        },
                        grid: {
                            color: gridColor
                        },
                        pointLabels: {
                            color: textColor,
                            font: {
                                size: 14,
                                weight: 'bold'
                            },
                            padding: 10
                        },
                        ticks: {
                            backdropColor: 'transparent',
                            color: textColor,
                            showLabelBackdrop: false,
                            stepSize: 10,
                            font: {
                                size: 10
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            color: textColor,
                            font: {
                                size: 14
                            },
                            boxWidth: 15,
                            padding: 15
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.label}: ${context.raw}% proficiency`;
                            }
                        }
                    }
                },
                elements: {
                    line: {
                        tension: 0.2
                    }
                }
            }
        });
        
        // Store the chart instance in the window object for future reference
        window.skillsChart = radarChart;
    } catch (error) {
        console.error('Error initializing skills chart:', error);
    }
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

// Add function to handle skill pulse animation
function pulseSkill(element) {
    // Add pulse animation to the container with more noticeable effect
    element.classList.add('bg-blue-100', 'dark:bg-blue-900/30', 'scale-105', 'shadow-md');
    
    // Find the skill bar inside this container
    const skillBar = element.querySelector('.skill-bar');
    if (skillBar) {
        // Add a quick animation to the skill bar with more dramatic effect
        skillBar.style.transition = 'width 0.4s ease-in-out, background-color 0.4s ease';
        
        // Store the original properties
        const targetWidth = skillBar.getAttribute('data-width');
        const originalBgColor = skillBar.style.backgroundColor;
        
        // First expand the bar
        skillBar.style.width = '100%';
        skillBar.style.backgroundColor = '#4338ca'; // Indigo-700 color
        
        // Then contract and then expand to target width with color change
        setTimeout(() => {
            skillBar.style.width = '10%';
            skillBar.style.backgroundColor = '#ef4444'; // Red-500 color
            
            setTimeout(() => {
                skillBar.style.width = targetWidth;
                skillBar.style.backgroundColor = '#3b82f6'; // Blue-500 color
                
                // Remove highlight after animation completes
                setTimeout(() => {
                    element.classList.remove('bg-blue-100', 'dark:bg-blue-900/30', 'scale-105', 'shadow-md');
                    skillBar.style.backgroundColor = originalBgColor;
                }, 700);
            }, 300);
        }, 400);
        
        // Show a tooltip or message (optional)
        const tooltip = element.querySelector('.text-xs');
        if (tooltip) {
            tooltip.textContent = "Proficiency: " + targetWidth;
            tooltip.classList.remove('opacity-0');
            tooltip.classList.add('opacity-100');
            
            setTimeout(() => {
                tooltip.textContent = "Click to see animation";
                tooltip.classList.remove('opacity-100');
                tooltip.classList.add('opacity-0');
            }, 1500);
        }
    }
} 