// API Configuration
const API_BASE_URL = 'http://localhost:8001/api';

// Chart instance
let segmentChart = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    loadChurnRateKPIs();
    loadSegmentAnalysis();
    setupPredictionForm();
});

// Load KPI metrics
async function loadChurnRateKPIs() {
    try {
        const response = await fetch(`${API_BASE_URL}/analytics/churn-rate/`);
        const data = await response.json();

        document.getElementById('total-customers').textContent = data.total_customers.toLocaleString();
        document.getElementById('churn-rate').textContent = `${data.churn_rate}%`;

        // Calculate average charges from breakdown
        const breakdown = data.breakdown || [];
        const avgCharges = breakdown.reduce((sum, item) => sum + (item.avg_monthly_charges || 0), 0) / breakdown.length;
        document.getElementById('avg-charges').textContent = `$${avgCharges.toFixed(2)}`;

    } catch (error) {
        console.error('Error loading KPIs:', error);
        showError('Failed to load dashboard metrics');
    }
}

// Load segment analysis
async function loadSegmentAnalysis() {
    const segmentBy = document.getElementById('segment-by').value;

    try {
        const response = await fetch(`${API_BASE_URL}/analytics/segment-analysis/?segment_by=${segmentBy}`);
        const data = await response.json();

        renderSegmentChart(data.segments);

    } catch (error) {
        console.error('Error loading segment analysis:', error);
        showError('Failed to load segment analysis');
    }
}

// Render segment chart
function renderSegmentChart(segments) {
    const ctx = document.getElementById('segmentChart').getContext('2d');

    // Destroy existing chart
    if (segmentChart) {
        segmentChart.destroy();
    }

    const labels = segments.map(s => s.segment || s._id);
    const churnRates = segments.map(s => s.churn_rate);
    const totals = segments.map(s => s.total);

    segmentChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Churn Rate (%)',
                    data: churnRates,
                    backgroundColor: 'rgba(255, 99, 132, 0.6)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 2,
                    yAxisID: 'y'
                },
                {
                    label: 'Total Customers',
                    data: totals,
                    backgroundColor: 'rgba(54, 162, 235, 0.6)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 2,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += context.datasetIndex === 0
                                    ? context.parsed.y.toFixed(2) + '%'
                                    : context.parsed.y.toLocaleString();
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Churn Rate (%)'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Total Customers'
                    },
                    grid: {
                        drawOnChartArea: false,
                    }
                }
            }
        }
    });
}

// Setup prediction form
function setupPredictionForm() {
    const form = document.getElementById('prediction-form');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData(form);
        const data = {};

        formData.forEach((value, key) => {
            // Convert numeric fields
            if (['tenure', 'MonthlyCharges', 'SeniorCitizen'].includes(key)) {
                data[key] = parseFloat(value);
            } else {
                data[key] = value;
            }
        });

        await predictChurn(data);
    });
}

// Predict churn
async function predictChurn(customerData) {
    const resultDiv = document.getElementById('prediction-result');

    try {
        const response = await fetch(`${API_BASE_URL}/predict/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(customerData)
        });

        if (!response.ok) {
            throw new Error('Prediction failed');
        }

        const result = await response.json();

        // Display results
        document.getElementById('result-probability').textContent =
            `${(result.churn_probability * 100).toFixed(1)}%`;

        const riskBadge = document.getElementById('result-risk');
        riskBadge.textContent = result.risk_level;
        riskBadge.className = 'metric-value risk-badge risk-' + result.risk_level.toLowerCase();

        document.getElementById('result-prediction').textContent =
            result.churn_prediction === 'Yes' ? '⚠️ Likely to Churn' : '✅ Likely to Stay';

        resultDiv.classList.remove('hidden');
        resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

    } catch (error) {
        console.error('Prediction error:', error);
        showError('Failed to predict churn. Please try again.');
    }
}

// Show error message
function showError(message) {
    alert(message); // Simple alert for now, can be enhanced with toast notifications
}
