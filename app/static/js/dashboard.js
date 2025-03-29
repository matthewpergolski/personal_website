// Dashboard initialization and chart rendering
document.addEventListener('DOMContentLoaded', function() {
    // Filter controls
    const filterButtons = document.querySelectorAll('.filter-pill');
    const dashboardCards = document.querySelectorAll('.dashboard-card');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove active class from all buttons
            filterButtons.forEach(btn => btn.classList.remove('active'));
            
            // Add active class to clicked button
            this.classList.add('active');
            
            const filter = this.getAttribute('data-filter');
            
            // Show all cards if 'all' filter, otherwise filter by category
            dashboardCards.forEach(card => {
                if (filter === 'all' || card.getAttribute('data-category') === filter) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });
    
    // Initialize charts with visualization data
    initDashboardCharts();
    
    // Initialize dark mode detection for chart updates
    const darkModeToggle = document.getElementById('darkModeToggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', () => {
            // Use setTimeout to let the DOM update with the new dark mode state
            setTimeout(() => {
                updateChartsForDarkMode();
            }, 50);
        });
    }
    
    // Add event listener for the prediction button in ML demo
    const predictBtn = document.getElementById('predictBtn');
    if (predictBtn) {
        predictBtn.addEventListener('click', generatePrediction);
    }
});

// Main function to initialize charts
function initDashboardCharts() {
    // Get the visualization data from the template
    const vizData = window.dashboardData || getSampleData();
    
    // Check if we're in dark mode
    const isDarkMode = document.documentElement.classList.contains('dark');
    const textColor = isDarkMode ? '#f3f4f6' : '#374151';
    const gridColor = isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
    
    // Initialize Language Distribution Chart
    if (document.getElementById('languagesChart')) {
        initLanguageChart(vizData.language_distribution, textColor);
    }
    
    // Initialize Repository Size Chart
    if (document.getElementById('repoSizeChart')) {
        initRepoSizeChart(vizData.repository_sizes, textColor, gridColor);
    }
    
    // Initialize Stars Timeline Chart
    if (document.getElementById('starsTimelineChart')) {
        initStarsChart(vizData.stars_timeline, textColor, gridColor);
    }
    
    // Initialize ML Model Chart
    if (document.getElementById('mlModelChart')) {
        initMLModelChart(vizData.ml_models, textColor, gridColor);
    }
    
    // Initialize Contribution Heatmap
    if (document.getElementById('contributionHeatmap')) {
        initContributionHeatmap(vizData.contributions, isDarkMode);
    }
    
    // Initialize Data Flow Diagram
    if (document.getElementById('dataFlowDiagram')) {
        initDataFlowDiagram(isDarkMode);
    }
    
    // Initialize ML Demo Chart
    if (document.getElementById('mlDemoChart')) {
        initMLDemoChart(textColor, gridColor);
    }
}

// Update charts for dark mode
function updateChartsForDarkMode() {
    // Re-initialize all charts with the current dark mode setting
    initDashboardCharts();
}

// Individual chart initialization functions
function initLanguageChart(data, textColor) {
    const ctx = document.getElementById('languagesChart').getContext('2d');
    
    window.languageChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(data),
            datasets: [{
                data: Object.values(data),
                backgroundColor: [
                    'rgba(54, 162, 235, 0.7)',  // Blue
                    'rgba(255, 206, 86, 0.7)',  // Yellow
                    'rgba(75, 192, 192, 0.7)',  // Teal
                    'rgba(153, 102, 255, 0.7)', // Purple
                    'rgba(255, 99, 132, 0.7)',  // Pink
                    'rgba(201, 203, 207, 0.7)'  // Gray
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        color: textColor
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            return `${label}: ${value}%`;
                        }
                    }
                }
            }
        }
    });
}

function initRepoSizeChart(data, textColor, gridColor) {
    const ctx = document.getElementById('repoSizeChart').getContext('2d');
    
    window.repoSizeChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.names,
            datasets: [{
                label: 'Code Size (KB)',
                data: data.code_size,
                backgroundColor: 'rgba(54, 162, 235, 0.7)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }, {
                label: 'Commits',
                data: data.commits,
                backgroundColor: 'rgba(255, 99, 132, 0.7)',
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    grid: {
                        display: false,
                        color: gridColor
                    },
                    ticks: {
                        color: textColor
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: gridColor
                    },
                    ticks: {
                        color: textColor
                    }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        color: textColor
                    }
                }
            }
        }
    });
}

function initStarsChart(data, textColor, gridColor) {
    const ctx = document.getElementById('starsTimelineChart').getContext('2d');
    
    window.starsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.months,
            datasets: [{
                label: 'Cumulative Stars',
                data: data.cumulative,
                fill: true,
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    grid: {
                        color: gridColor
                    },
                    ticks: {
                        color: textColor
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: gridColor
                    },
                    ticks: {
                        color: textColor
                    }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        color: textColor
                    }
                }
            }
        }
    });
}

function initMLModelChart(data, textColor, gridColor) {
    const ctx = document.getElementById('mlModelChart').getContext('2d');
    
    // Prepare datasets
    const datasets = [];
    const colors = [
        { bg: 'rgba(54, 162, 235, 0.2)', border: 'rgba(54, 162, 235, 1)' },
        { bg: 'rgba(255, 99, 132, 0.2)', border: 'rgba(255, 99, 132, 1)' },
        { bg: 'rgba(75, 192, 192, 0.2)', border: 'rgba(75, 192, 192, 1)' }
    ];
    
    let i = 0;
    for (const [model, values] of Object.entries(data.models)) {
        datasets.push({
            label: model,
            data: values,
            fill: true,
            backgroundColor: colors[i].bg,
            borderColor: colors[i].border,
            pointBackgroundColor: colors[i].border,
            pointBorderColor: '#fff',
            pointHoverBackgroundColor: '#fff',
            pointHoverBorderColor: colors[i].border
        });
        i = (i + 1) % colors.length;
    }
    
    window.mlModelChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: data.metrics,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    angleLines: {
                        display: true,
                        color: gridColor
                    },
                    grid: {
                        color: gridColor
                    },
                    pointLabels: {
                        color: textColor
                    },
                    ticks: {
                        color: textColor,
                        backdropColor: 'transparent'
                    },
                    suggestedMin: 50,
                    suggestedMax: 100
                }
            },
            plugins: {
                legend: {
                    labels: {
                        color: textColor
                    }
                }
            }
        }
    });
}

function initContributionHeatmap(data, isDarkMode) {
    // Create a simulated heatmap from the monthly data
    const zValues = [];
    const monthsPerRow = 3; // 4 rows (quarters) of 3 months
    
    for (let i = 0; i < data.values.length; i += monthsPerRow) {
        zValues.push(data.values.slice(i, i + monthsPerRow).map(value => value / 3));
    }
    
    const heatmapData = [
        {
            z: zValues,
            x: ['Month 1', 'Month 2', 'Month 3'],
            y: ['Q1', 'Q2', 'Q3', 'Q4'],
            type: 'heatmap',
            colorscale: isDarkMode ? 'Blues' : 'YlGnBu',
            showscale: false
        }
    ];
    
    const heatmapLayout = {
        title: {
            text: 'Monthly Contribution Activity',
            font: {
                color: isDarkMode ? '#f3f4f6' : '#374151'
            }
        },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        margin: { t: 50, l: 80, b: 50, r: 20 },
        height: 300,
        font: {
            color: isDarkMode ? '#f3f4f6' : '#374151'
        }
    };
    
    Plotly.newPlot('contributionHeatmap', heatmapData, heatmapLayout, {displayModeBar: false});
}

function initDataFlowDiagram(isDarkMode) {
    const nodeColor = isDarkMode ? '#60a5fa' : '#4299e1';
    const edgeColor = isDarkMode ? '#9ca3af' : '#a0aec0';
    const textColor = isDarkMode ? '#f3f4f6' : '#374151';
    
    const nodes = [
        { id: 'data', label: 'Raw Data', x: 0, y: 0 },
        { id: 'clean', label: 'Data Cleaning', x: 1, y: 0 },
        { id: 'feature', label: 'Feature Engineering', x: 2, y: 0 },
        { id: 'split', label: 'Train/Test Split', x: 3, y: 0 },
        { id: 'model_train', label: 'Model Training', x: 4, y: 0 },
        { id: 'model_eval', label: 'Model Evaluation', x: 5, y: 0 },
        { id: 'deploy', label: 'Deployment', x: 6, y: 0 }
    ];
    
    const edges = [
        { from: 'data', to: 'clean' },
        { from: 'clean', to: 'feature' },
        { from: 'feature', to: 'split' },
        { from: 'split', to: 'model_train' },
        { from: 'model_train', to: 'model_eval' },
        { from: 'model_eval', to: 'deploy' }
    ];
    
    const nodeTrace = {
        x: nodes.map(node => node.x),
        y: nodes.map(node => node.y),
        mode: 'markers+text',
        marker: {
            size: 30,
            color: nodeColor,
            line: { width: 2, color: isDarkMode ? '#3b82f6' : '#2b6cb0' }
        },
        text: nodes.map(node => node.label),
        textposition: 'bottom',
        textfont: {
            color: textColor
        },
        hoverinfo: 'text',
        name: ''
    };
    
    const edgeTraces = edges.map(edge => {
        const fromNode = nodes.find(node => node.id === edge.from);
        const toNode = nodes.find(node => node.id === edge.to);
        
        return {
            x: [fromNode.x, toNode.x],
            y: [fromNode.y, toNode.y],
            mode: 'lines',
            line: {
                color: edgeColor,
                width: 2
            },
            hoverinfo: 'none'
        };
    });
    
    const data = [nodeTrace, ...edgeTraces];
    
    const layout = {
        showlegend: false,
        hovermode: 'closest',
        margin: { t: 30, b: 90, l: 20, r: 20 },
        xaxis: {
            showgrid: false,
            zeroline: false,
            showticklabels: false
        },
        yaxis: {
            showgrid: false,
            zeroline: false,
            showticklabels: false
        },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        height: 300
    };
    
    Plotly.newPlot('dataFlowDiagram', data, layout, {displayModeBar: false});
}

function initMLDemoChart(textColor, gridColor) {
    const ctx = document.getElementById('mlDemoChart').getContext('2d');
    
    window.mlDemoChart = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Class A',
                data: generateRandomPoints(50, 20, 60, 20, 60),
                backgroundColor: 'rgba(54, 162, 235, 0.5)',
                pointRadius: 6
            }, {
                label: 'Class B',
                data: generateRandomPoints(50, 40, 80, 40, 80),
                backgroundColor: 'rgba(255, 99, 132, 0.5)',
                pointRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    beginAtZero: true,
                    max: 100,
                    grid: {
                        color: gridColor
                    },
                    ticks: {
                        color: textColor
                    },
                    title: {
                        display: true,
                        text: 'Feature 1',
                        color: textColor
                    }
                },
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: {
                        color: gridColor
                    },
                    ticks: {
                        color: textColor
                    },
                    title: {
                        display: true,
                        text: 'Feature 2',
                        color: textColor
                    }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        color: textColor
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `(${context.parsed.x.toFixed(1)}, ${context.parsed.y.toFixed(1)})`;
                        }
                    }
                }
            }
        }
    });
}

// Generate points for the ML demo
function generateRandomPoints(count, minX, maxX, minY, maxY) {
    const points = [];
    for (let i = 0; i < count; i++) {
        points.push({
            x: Math.random() * (maxX - minX) + minX,
            y: Math.random() * (maxY - minY) + minY
        });
    }
    return points;
}

// Handle prediction button click
function generatePrediction() {
    const feature1 = parseInt(document.getElementById('feature1').value);
    const feature2 = parseInt(document.getElementById('feature2').value);
    const feature3 = parseInt(document.getElementById('feature3').value);
    const feature4 = parseInt(document.getElementById('feature4').value);
    
    // Remove any existing prediction point
    if (window.mlDemoChart.data.datasets.length > 2) {
        window.mlDemoChart.data.datasets.pop();
    }
    
    // Add the new point to the chart
    window.mlDemoChart.data.datasets.push({
        label: 'Your Input',
        data: [{x: feature1, y: feature2}],
        backgroundColor: 'rgba(75, 192, 192, 1)',
        pointRadius: 10,
        pointStyle: 'triangle'
    });
    window.mlDemoChart.update();
    
    // Calculate "prediction" (simplified demo version)
    const distanceToA = Math.sqrt(Math.pow(feature1 - 40, 2) + Math.pow(feature2 - 40, 2));
    const distanceToB = Math.sqrt(Math.pow(feature1 - 60, 2) + Math.pow(feature2 - 60, 2));
    
    let predictedClass, confidence;
    if (distanceToA < distanceToB) {
        predictedClass = 'Class A';
        confidence = 100 * (distanceToB / (distanceToA + distanceToB));
    } else {
        predictedClass = 'Class B';
        confidence = 100 * (distanceToA / (distanceToA + distanceToB));
    }
    
    // Display the prediction
    document.getElementById('predictionResult').innerHTML = `
        <div class="text-center">
            <p class="text-lg mb-2">Prediction: <span class="font-bold">${predictedClass}</span></p>
            <p class="mb-4">Confidence: ${confidence.toFixed(2)}%</p>
            <div class="bg-gray-200 dark:bg-gray-700 rounded-full h-2.5 mb-4">
                <div class="bg-blue-600 h-2.5 rounded-full" style="width: ${confidence}%"></div>
            </div>
            <p class="text-sm">Features Used: [${feature1}, ${feature2}, ${feature3}, ${feature4}]</p>
        </div>
    `;
}

// Fallback sample data if none is provided by the template
function getSampleData() {
    return {
        "language_distribution": {
            "Python": 45,
            "JavaScript": 20,
            "R": 15,
            "SQL": 10,
            "Java": 5,
            "Other": 5
        },
        "contributions": {
            "months": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
            "values": [12, 19, 25, 32, 28, 24, 18, 27, 39, 45, 38, 30]
        },
        "repository_sizes": {
            "names": ["Data Analysis", "ML Project", "NLP Research", "Visualization", "Web App"],
            "code_size": [350, 520, 280, 190, 430],
            "commits": [45, 65, 30, 25, 50]
        },
        "stars_timeline": {
            "months": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
            "cumulative": [5, 12, 20, 25, 35, 45, 55, 70, 85, 100, 120, 145]
        },
        "ml_models": {
            "metrics": ["Accuracy", "Precision", "Recall", "F1 Score", "Training Speed", "Inference Speed"],
            "models": {
                "Random Forest": [85, 82, 80, 81, 70, 90],
                "Neural Network": [90, 87, 85, 86, 60, 75],
                "Gradient Boosting": [88, 90, 83, 87, 75, 82]
            }
        }
    };
} 