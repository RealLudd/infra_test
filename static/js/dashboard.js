/**
 * CashWeb Dashboard - Black Dashboard Theme
 * Enhanced JavaScript with automation analytics and charting
 */

// Global variables
let currentPeriod = 'week';
let currentChartPeriod = 'week';
let automationChart = null;
let currentBankAccount = '';  // Combined filter: "company_code|housebank|currency"

// Format currency with USD formatting
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

// Load overview data from API
async function loadOverview() {
    try {
        const params = new URLSearchParams({
            period: currentPeriod,
            bank_account: currentBankAccount
        });
        const response = await fetch(`/api/overview?${params}`);
        const data = await response.json();

        // Update Total Payments Received
        updateStatValue('totalReceived', formatCurrency(data.total_received));
        document.getElementById('paymentCount').innerHTML =
            `<span>${data.total_payments} payment${data.total_payments !== 1 ? 's' : ''}</span>`;

        // Update Automation Percentage
        updateStatValue('automationPercentage', `${data.automation_percentage}%`);
        document.getElementById('automationDetail').innerHTML =
            `<span>${data.automated_count} auto / ${data.manual_count} manual</span>`;

        // Update Unassigned Workload
        updateStatValue('unassignedCount', data.unassigned_count.toString());
        document.getElementById('unassignedValue').innerHTML =
            `<span>${formatCurrency(data.unassigned_value)} value</span>`;

        // Update Total Value Assigned
        updateStatValue('totalAssigned', formatCurrency(data.total_assigned_value));
        const assignedPct = data.total_received > 0
            ? ((data.total_assigned_value / data.total_received) * 100).toFixed(1)
            : 0;
        document.getElementById('assignedPercentage').innerHTML =
            `<span>${assignedPct}% of total</span>`;

        // Update Average Times
        updateStatValue('avgAutoTime', data.avg_auto_time_minutes > 0
            ? data.avg_auto_time_minutes.toFixed(1)
            : '0');
        updateStatValue('avgManualTime', data.avg_manual_time_minutes > 0
            ? data.avg_manual_time_minutes.toFixed(1)
            : '0');

    } catch (error) {
        console.error('Error loading overview:', error);
        showNotification('Error loading overview data', 'error');
    }
}

// Load automation trend data and render chart
async function loadAutomationTrend() {
    try {
        const params = new URLSearchParams({
            period: currentChartPeriod,
            bank_account: currentBankAccount
        });
        const response = await fetch(`/api/automation-trend?${params}`);
        const data = await response.json();

        renderAutomationChart(data);
    } catch (error) {
        console.error('Error loading automation trend:', error);
        showNotification('Error loading chart data', 'error');
    }
}

// Render automation chart with Chart.js
function renderAutomationChart(data) {
    const ctx = document.getElementById('automationChart').getContext('2d');

    // Destroy existing chart if it exists
    if (automationChart) {
        automationChart.destroy();
    }

    // Create gradient for line
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(29, 140, 248, 0.4)');
    gradient.addColorStop(1, 'rgba(29, 140, 248, 0.0)');

    automationChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Automation %',
                data: data.automation_percentages,
                borderColor: '#1d8cf8',
                backgroundColor: gradient,
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#1d8cf8',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 6,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: '#9a9a9a',
                        font: {
                            size: 12,
                            family: 'Poppins'
                        },
                        padding: 15
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(39, 41, 61, 0.95)',
                    titleColor: '#ffffff',
                    bodyColor: '#9a9a9a',
                    borderColor: '#2b3553',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            const index = context.dataIndex;
                            const percentage = context.parsed.y;
                            const count = data.payment_counts[index];
                            return [
                                `Automation: ${percentage}%`,
                                `Payments: ${count}`
                            ];
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        color: '#9a9a9a',
                        font: {
                            size: 11,
                            family: 'Poppins'
                        },
                        callback: function(value) {
                            return value + '%';
                        }
                    },
                    grid: {
                        color: 'rgba(43, 53, 83, 0.5)',
                        drawBorder: false
                    }
                },
                x: {
                    ticks: {
                        color: '#9a9a9a',
                        font: {
                            size: 11,
                            family: 'Poppins'
                        },
                        maxRotation: 45,
                        minRotation: 0
                    },
                    grid: {
                        color: 'rgba(43, 53, 83, 0.3)',
                        drawBorder: false
                    }
                }
            }
        }
    });
}

// Load summary data (legacy - keeping for compatibility)
async function loadSummary() {
    try {
        const response = await fetch('/api/summary');
        const data = await response.json();

        // These are not displayed in new dashboard but keeping for compatibility
        console.log('Summary data loaded:', data);
    } catch (error) {
        console.error('Error loading summary:', error);
    }
}

// Update stat value with fade effect
function updateStatValue(elementId, value) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.opacity = '0.5';
        setTimeout(() => {
            element.textContent = value;
            element.style.opacity = '1';
        }, 150);
    }
}

// Load transactions from API
async function loadTransactions() {
    try {
        const response = await fetch('/api/transactions');
        const transactions = await response.json();

        const listElement = document.getElementById('transactionList');
        listElement.innerHTML = '';

        if (transactions.length === 0) {
            listElement.innerHTML = `
                <li class="loading">
                    <p>No transactions found</p>
                </li>
            `;
            return;
        }

        // Sort transactions by date (newest first)
        transactions.sort((a, b) => new Date(b.date) - new Date(a.date));

        // Show only first 10 transactions
        transactions.slice(0, 10).forEach(transaction => {
            const li = document.createElement('li');
            const typeClass = transaction.type === 'income' ? 'income' : 'expense';
            const amountSign = transaction.type === 'income' ? '+' : '-';
            const icon = transaction.type === 'income' ? '📈' : '📉';

            // Add automation badge
            let automationBadge = '';
            if (transaction.automated === true) {
                automationBadge = '<span style="background: rgba(0, 242, 195, 0.2); color: var(--success-color); padding: 3px 8px; border-radius: 4px; font-size: 0.7rem; margin-left: 8px;">AUTO</span>';
            } else if (transaction.automated === false) {
                automationBadge = '<span style="background: rgba(255, 141, 114, 0.2); color: var(--warning-color); padding: 3px 8px; border-radius: 4px; font-size: 0.7rem; margin-left: 8px;">MANUAL</span>';
            } else if (transaction.automated === null) {
                automationBadge = '<span style="background: rgba(253, 93, 147, 0.2); color: var(--danger-color); padding: 3px 8px; border-radius: 4px; font-size: 0.7rem; margin-left: 8px;">PENDING</span>';
            }

            li.className = `transaction-item ${typeClass}`;
            li.innerHTML = `
                <div class="transaction-info">
                    <div class="transaction-date">
                        <i class="far fa-calendar"></i> ${formatDate(transaction.date)}
                    </div>
                    <div class="transaction-description">
                        ${icon} ${transaction.description} ${automationBadge}
                    </div>
                </div>
                <div class="transaction-amount ${typeClass}">
                    ${amountSign}${formatCurrency(Math.abs(transaction.amount))}
                </div>
            `;

            listElement.appendChild(li);
        });
    } catch (error) {
        console.error('Error loading transactions:', error);
        const listElement = document.getElementById('transactionList');
        listElement.innerHTML = `
            <li class="loading">
                <p style="color: var(--danger-color);">Error loading transactions</p>
            </li>
        `;
    }
}

// Format date to readable format
function formatDate(dateString) {
    const date = new Date(dateString);
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return date.toLocaleDateString('en-US', options);
}

// Show notification (simple console log for now, can be enhanced)
function showNotification(message, type = 'info') {
    console.log(`[${type.toUpperCase()}] ${message}`);
}

// Toggle sidebar on mobile
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    sidebar.classList.toggle('active');
}

// Handle period button click
function handlePeriodChange(period) {
    currentPeriod = period;

    // Update button states
    document.querySelectorAll('.period-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.period === period) {
            btn.classList.add('active');
        }
    });

    // Reload overview data
    loadOverview();
}

// Handle chart period button click
function handleChartPeriodChange(period) {
    currentChartPeriod = period;

    // Update button states
    document.querySelectorAll('.chart-period-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.chartPeriod === period) {
            btn.classList.add('active');
        }
    });

    // Reload chart data
    loadAutomationTrend();
}

// Load filter options from API
async function loadFilterOptions() {
    try {
        const response = await fetch('/api/filter-options');
        const data = await response.json();

        // Populate bank account filter
        const bankAccountSelect = document.getElementById('bankAccountFilter');
        data.bank_accounts.forEach(account => {
            const option = document.createElement('option');
            option.value = account.value;
            option.textContent = account.label;
            bankAccountSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading filter options:', error);
    }
}

// Handle filter change
function handleFilterChange() {
    currentBankAccount = document.getElementById('bankAccountFilter').value;

    // Reload data with new filter
    loadOverview();
    loadAutomationTrend();
}

// Clear all filters
function clearAllFilters() {
    document.getElementById('bankAccountFilter').value = '';
    currentBankAccount = '';

    // Reload data without filters
    loadOverview();
    loadAutomationTrend();
}

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    console.log('CashWeb Dashboard initializing...');

    // Setup mobile menu toggle
    const mobileToggle = document.querySelector('.mobile-menu-toggle');
    if (mobileToggle) {
        mobileToggle.addEventListener('click', toggleSidebar);
    }

    // Setup period selector buttons
    document.querySelectorAll('.period-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            handlePeriodChange(btn.dataset.period);
        });
    });

    // Setup chart period buttons
    document.querySelectorAll('.chart-period-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            handleChartPeriodChange(btn.dataset.chartPeriod);
        });
    });

    // Setup filter event listeners
    document.getElementById('bankAccountFilter').addEventListener('change', handleFilterChange);
    document.getElementById('clearFiltersBtn').addEventListener('click', clearAllFilters);

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', (e) => {
        const sidebar = document.querySelector('.sidebar');
        const mobileToggle = document.querySelector('.mobile-menu-toggle');

        if (window.innerWidth <= 991 &&
            sidebar.classList.contains('active') &&
            !sidebar.contains(e.target) &&
            !mobileToggle.contains(e.target)) {
            sidebar.classList.remove('active');
        }
    });

    // Load initial data
    loadFilterOptions();
    loadOverview();
    loadAutomationTrend();
    loadTransactions();

    console.log('Dashboard loaded successfully');
});

// Auto-refresh data every 60 seconds
setInterval(() => {
    loadOverview();
    loadAutomationTrend();
    loadTransactions();
}, 60000);

// Handle window resize
let resizeTimer;
window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
        // Close sidebar on desktop view
        if (window.innerWidth > 991) {
            const sidebar = document.querySelector('.sidebar');
            sidebar.classList.remove('active');
        }
        // Resize chart
        if (automationChart) {
            automationChart.resize();
        }
    }, 250);
});
