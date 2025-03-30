/**
 * Language Chart Visualization
 * 
 * This script handles the GitHub language distribution chart visualization.
 * It creates an interactive pie chart showing the breakdown of languages
 * used across your GitHub repositories.
 */

// Color mapping for languages
const LANGUAGE_COLORS = {
    'Jupyter Notebook': '#F37626', // Jupyter orange
    'Python': '#3776AB',           // Python blue
    'HTML': '#E34F26',             // HTML orange/red
    'JavaScript': '#F7DF1E',       // JavaScript yellow
    'CSS': '#563D7C',              // CSS purple
    'R': '#276DC3',                // R blue
    'Shell': '#89E051',            // Shell green
    'TypeScript': '#3178C6',       // TypeScript blue
    'Java': '#007396',             // Java blue
    'C++': '#00599C',              // C++ blue
    'Ruby': '#CC342D',             // Ruby red
    'Other': '#9CA3AF'             // Gray
};

// Initialize the chart when DOM is ready
document.addEventListener('DOMContentLoaded', initializeChart);

/**
 * Main initialization function
 */
function initializeChart() {
    // Get data from the data attribute
    const dataContainer = document.getElementById('chartDataContainer');
    if (!dataContainer) {
        console.error('Chart data container not found');
        return;
    }
    
    let languageData = {};
    try {
        // Parse the JSON data from the data attribute
        languageData = JSON.parse(dataContainer.getAttribute('data-chart-data') || '{}');
        console.log('Language distribution:', languageData);
    } catch (error) {
        console.error('Error parsing chart data:', error);
        showFallbackContent("Error parsing chart data");
        return;
    }
    
    if (Object.keys(languageData).length > 0) {
        // Create the chart
        createLanguageChart(languageData);
        
        // Handle dark mode toggle if needed
        const darkModeToggle = document.getElementById('darkModeToggle');
        if (darkModeToggle) {
            darkModeToggle.addEventListener('click', function() {
                setTimeout(function() {
                    // Destroy and recreate chart with new colors
                    if (window.langChart) {
                        window.langChart.destroy();
                    }
                    createLanguageChart(languageData);
                }, 100);
            });
        }
    } else {
        // Show fallback content for no data
        showFallbackContent("No language data available");
    }
}

/**
 * Show fallback content when chart cannot be displayed
 * @param {string} message - The message to display
 */
function showFallbackContent(message) {
    const canvas = document.getElementById('langChart');
    const fallback = document.getElementById('fallbackContent');
    
    if (canvas && fallback) {
        canvas.style.display = 'none';
        fallback.classList.remove('hidden');
        fallback.textContent = message;
    }
}

/**
 * Create the language chart
 * @param {Object} data - The language distribution data
 */
function createLanguageChart(data) {
    try {
        // Check if we're in dark mode
        const isDarkMode = document.documentElement.classList.contains('dark');
        const textColor = isDarkMode ? '#e5e7eb' : '#374151';
        
        // Generate colors with opacity
        const colors = Object.keys(data).map(function(lang) {
            const baseColor = LANGUAGE_COLORS[lang] || '#9CA3AF';
            // Add opacity to the hex color
            return isDarkMode ? baseColor + 'CC' : baseColor + 'CC'; // CC = 80% opacity
        });
        
        // Create chart
        const ctx = document.getElementById('langChart').getContext('2d');
        window.langChart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: Object.keys(data),
                datasets: [{
                    data: Object.values(data),
                    backgroundColor: colors,
                    borderColor: isDarkMode ? '#1e293b' : 'white',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            color: textColor,
                            font: {
                                size: 14
                            },
                            padding: 20
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const lang = context.label;
                                const value = context.raw;
                                return `${lang}: ${value}%`;
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error creating chart:', error);
        showFallbackContent("Error loading chart data");
    }
} 