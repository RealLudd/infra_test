// Global variables
let currentPeriod = 'today';
let charts = {};

// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', () => {
    initializePeriodSelector();
    loadAllData();
    updateLastUpdatedTime();

    // Auto-refresh every 5 minutes
    setInterval(() => {
        loadAllData();
        updateLastUpdatedTime();
    }, 300000);
});

// Period selector functionality
function initializePeriodSelector() {
    const periodButtons = document.querySelectorAll('.period-btn');

    periodButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            // Update active state
            periodButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Update current period
            currentPeriod = btn.dataset.period;

            // Reload data
            loadAllData();
        });
    });
}

// Load all dashboard data
async function loadAllData() {
    try {
        await Promise.all([
            loadOverviewData(),
            loadAutomationTrend(),
            loadAutomationEfficiency(),
            loadExceptionsData(),
            loadRemittanceInsights(),
            loadMonthEndSummary()
        ]);
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

// Format currency
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'EUR'
    }).format(value);
}

// Format number
function formatNumber(value) {
    return new Intl.NumberFormat('en-US').format(value);
}

// Load overview data
async function loadOverviewData() {
    try {
        const response = await fetch(`/api/overview?period=${currentPeriod}`);
        const data = await response.json();

        document.getElementById('total-payments').textContent = formatNumber(data.total_payments);
        document.getElementById('total-value').textContent = formatCurrency(data.total_value);
        document.getElementById('auto-processed-pct').textContent = `${data.auto_processed_pct}%`;
        document.getElementById('auto-processed-count').textContent = `${formatNumber(data.auto_processed_count)} payments`;
        document.getElementById('manual-workload').textContent = formatNumber(data.manual_workload);
        document.getElementById('total-value-assigned').textContent = formatCurrency(data.total_value_assigned);
        document.getElementById('avg-time-auto').textContent = `${data.avg_time_auto} min (auto)`;
        document.getElementById('avg-time-manual').textContent = `${data.avg_time_manual} min (manual)`;
    } catch (error) {
        console.error('Error loading overview data:', error);
    }
}

// Load automation trend chart
async function loadAutomationTrend() {
    try {
        const response = await fetch(`/api/automation-trend?period=${currentPeriod}`);
        const data = await response.json();

        const ctx = document.getElementById('automation-trend-chart');

        // Destroy existing chart if it exists
        if (charts.automationTrend) {
            charts.automationTrend.destroy();
        }

        charts.automationTrend = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Automation %',
                    data: data.data,
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: '#2563eb',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => `Automation: ${context.parsed.y}%`
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        min: 70,
                        max: 100,
                        ticks: {
                            callback: (value) => value + '%'
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading automation trend:', error);
    }
}

// Load automation efficiency data
async function loadAutomationEfficiency() {
    try {
        const response = await fetch('/api/automation-efficiency');
        const data = await response.json();

        // Update metrics
        document.getElementById('auto-success-rate').textContent = `${data.auto_success_rate}%`;
        document.getElementById('interventions-saved').textContent = formatNumber(data.manual_interventions_saved);
        document.getElementById('time-saved').textContent = `${data.time_saved_hours} hours`;
        document.getElementById('cost-saved').textContent = formatCurrency(data.cost_saved);

        // Match type distribution chart
        const matchCtx = document.getElementById('match-type-chart');
        if (charts.matchType) {
            charts.matchType.destroy();
        }

        charts.matchType = new Chart(matchCtx, {
            type: 'pie',
            data: {
                labels: ['Bank Account', 'Reference', 'Name', 'Other'],
                datasets: [{
                    data: [
                        data.match_breakdown.bank_account,
                        data.match_breakdown.reference,
                        data.match_breakdown.name,
                        data.match_breakdown.other
                    ],
                    backgroundColor: [
                        '#2563eb',
                        '#7c3aed',
                        '#10b981',
                        '#f59e0b'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });

        // Reprocessing chart
        const reprocessCtx = document.getElementById('reprocessing-chart');
        if (charts.reprocessing) {
            charts.reprocessing.destroy();
        }

        charts.reprocessing = new Chart(reprocessCtx, {
            type: 'bar',
            data: {
                labels: ['Initial Failures', 'Later Fixed'],
                datasets: [{
                    label: 'Count',
                    data: [
                        data.reprocessing.initial_failures,
                        data.reprocessing.later_fixed
                    ],
                    backgroundColor: ['#ef4444', '#10b981']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            afterLabel: (context) => {
                                if (context.dataIndex === 1) {
                                    return `Fix rate: ${data.reprocessing.fix_rate}%`;
                                }
                                return '';
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading automation efficiency:', error);
    }
}

// Load exceptions data
async function loadExceptionsData() {
    try {
        const response = await fetch('/api/exceptions');
        const data = await response.json();

        // Top exceptions table
        const exceptionsTable = document.getElementById('top-exceptions-table').querySelector('tbody');
        exceptionsTable.innerHTML = data.top_exceptions.map(item => `
            <tr>
                <td>${item.customer}</td>
                <td>${item.count}</td>
                <td>${item.last_occurrence}</td>
            </tr>
        `).join('');

        // High-value unassigned table
        const highValueTable = document.getElementById('high-value-table').querySelector('tbody');
        highValueTable.innerHTML = data.high_value_unassigned.map(item => `
            <tr>
                <td>${item.customer}</td>
                <td>${formatCurrency(item.amount)}</td>
                <td>${item.days_pending} days</td>
            </tr>
        `).join('');

        // Update delays
        document.getElementById('sap-delayed').textContent = data.delays.sap_posting_delayed;
        document.getElementById('remittance-delayed').textContent = data.delays.remittance_ingestion_delayed;

        // Error reasons chart
        const errorCtx = document.getElementById('error-reasons-chart');
        if (charts.errorReasons) {
            charts.errorReasons.destroy();
        }

        charts.errorReasons = new Chart(errorCtx, {
            type: 'bar',
            data: {
                labels: ['No Open Items', 'Multiple Customers', 'Remittance Mismatch', 'Missing Reference', 'Other'],
                datasets: [{
                    label: 'Error Count',
                    data: [
                        data.error_reasons.no_open_items,
                        data.error_reasons.multiple_customers,
                        data.error_reasons.remittance_mismatch,
                        data.error_reasons.missing_reference,
                        data.error_reasons.other
                    ],
                    backgroundColor: [
                        '#ef4444',
                        '#f59e0b',
                        '#eab308',
                        '#f97316',
                        '#64748b'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                indexAxis: 'y',
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading exceptions data:', error);
    }
}

// Load remittance insights
async function loadRemittanceInsights() {
    try {
        const response = await fetch('/api/remittance-insights');
        const data = await response.json();

        // Update metrics
        document.getElementById('total-remittances').textContent = formatNumber(data.total_remittances);
        document.getElementById('parsed-pct').textContent = `${data.successfully_parsed_pct}%`;
        document.getElementById('parsed-count').textContent = `${formatNumber(data.successfully_parsed)} files`;
        document.getElementById('manual-review-pct').textContent = `${data.manual_review_pct}%`;
        document.getElementById('manual-review-count').textContent = `${formatNumber(data.manual_review)} files`;
        document.getElementById('avg-processing-time').textContent = `${data.avg_processing_time} min`;

        // Remittance status donut chart
        const statusCtx = document.getElementById('remittance-status-chart');
        if (charts.remittanceStatus) {
            charts.remittanceStatus.destroy();
        }

        charts.remittanceStatus = new Chart(statusCtx, {
            type: 'doughnut',
            data: {
                labels: ['Successfully Parsed', 'Manual Review'],
                datasets: [{
                    data: [data.successfully_parsed, data.manual_review],
                    backgroundColor: ['#10b981', '#f59e0b']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });

        // Customer volume chart
        const volumeCtx = document.getElementById('customer-volume-chart');
        if (charts.customerVolume) {
            charts.customerVolume.destroy();
        }

        charts.customerVolume = new Chart(volumeCtx, {
            type: 'bar',
            data: {
                labels: data.top_customers.map(c => c.customer),
                datasets: [{
                    label: 'Volume',
                    data: data.top_customers.map(c => c.volume),
                    backgroundColor: '#2563eb'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading remittance insights:', error);
    }
}

// Load month-end summary
async function loadMonthEndSummary() {
    try {
        const response = await fetch('/api/month-end-summary');
        const data = await response.json();

        // Current month metrics
        document.getElementById('current-payments').textContent = formatNumber(data.current_month.payments_count);
        document.getElementById('current-value').textContent = formatCurrency(data.current_month.payments_value);
        document.getElementById('current-auto-rate').textContent = `${data.current_month.auto_rate}%`;
        document.getElementById('current-delay').textContent = `${data.current_month.avg_delay} min`;

        // Previous month metrics
        document.getElementById('previous-payments').textContent = formatNumber(data.previous_month.payments_count);
        document.getElementById('previous-value').textContent = formatCurrency(data.previous_month.payments_value);
        document.getElementById('previous-auto-rate').textContent = `${data.previous_month.auto_rate}%`;
        document.getElementById('previous-delay').textContent = `${data.previous_month.avg_delay} min`;

        // Improvements
        const autoRateChange = data.improvements.auto_rate_change;
        document.getElementById('auto-rate-change').textContent =
            `${autoRateChange > 0 ? '+' : ''}${autoRateChange}%`;

        const delayImprovement = data.improvements.delay_improvement;
        document.getElementById('delay-improvement').textContent =
            `${delayImprovement > 0 ? '' : '+'}${Math.abs(delayImprovement)} min`;

        // Time saved
        document.getElementById('month-time-saved').textContent = `${data.time_saved.hours} hours`;
        document.getElementById('month-cost-saved').textContent =
            `${data.time_saved.fte} FTE | ${formatCurrency(data.time_saved.euro_value)}`;

        // Top rules chart
        const rulesCtx = document.getElementById('top-rules-chart');
        if (charts.topRules) {
            charts.topRules.destroy();
        }

        charts.topRules = new Chart(rulesCtx, {
            type: 'bar',
            data: {
                labels: data.top_rules.map(r => r.name),
                datasets: [{
                    label: 'Success Rate (%)',
                    data: data.top_rules.map(r => r.success_rate),
                    backgroundColor: '#10b981'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        min: 70,
                        max: 100,
                        ticks: {
                            callback: (value) => value + '%'
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading month-end summary:', error);
    }
}

// Update last updated time
function updateLastUpdatedTime() {
    const now = new Date();
    const formatted = now.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    document.getElementById('last-updated').textContent = formatted;
}
