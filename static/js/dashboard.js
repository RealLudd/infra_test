/**
 * CashWeb Dashboard - Black Dashboard Theme
 * Enhanced JavaScript with automation analytics and charting
 */

// Global variables
let currentPeriod = 'week';
let currentChartPeriod = 'week';
let automationChart = null;
let currentBankAccount = '';  // Combined filter: "company_code|housebank|currency"

// Format currency with EUR formatting
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'EUR',
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

        // 1. Update Total Payments Received (Amount)
        updateStatValue('totalReceived', formatCurrency(data.total_received));

        // 2. Update Total Payments (Number)
        updateStatValue('totalPayments', data.total_payments.toString());

        // 3. Update Processed Automatically
        updateStatValue('automationPercentage', `${data.automation_percentage}%`);
        document.getElementById('automationDetail').innerHTML =
            `<span>${data.automated_count} / ${data.total_payments} payments</span>`;

        // 4. Update Payments Assigned to Customer Account
        updateStatValue('assignedAccountPercentage', `${data.assigned_percentage}%`);
        document.getElementById('assignedAccountDetail').innerHTML =
            `<span>${data.assigned_count} / ${data.total_payments} payments</span>`;

        // 5. Update Number of Invoices Assigned
        updateStatValue('totalInvoices', data.total_invoices_assigned.toString());

        // 6. Update Total Value Assigned (%)
        updateStatValue('valueAssignedPercentage', `${data.value_assigned_percentage}%`);
        document.getElementById('valueAssignedAmount').innerHTML =
            `<span>${formatCurrency(data.total_assigned_value)} of total</span>`;

        // 7. Update Average Time (Automation)
        updateStatValue('avgAutoTime', data.avg_auto_time_minutes > 0
            ? data.avg_auto_time_minutes.toFixed(1)
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

    // Create gradients for PACO and FRAN lines
    const pacoGradient = ctx.createLinearGradient(0, 0, 0, 400);
    pacoGradient.addColorStop(0, 'rgba(29, 140, 248, 0.3)');
    pacoGradient.addColorStop(1, 'rgba(29, 140, 248, 0.0)');

    const franGradient = ctx.createLinearGradient(0, 0, 0, 400);
    franGradient.addColorStop(0, 'rgba(225, 78, 202, 0.3)');
    franGradient.addColorStop(1, 'rgba(225, 78, 202, 0.0)');

    automationChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: 'PACO Automation %',
                    data: data.paco_percentages,
                    borderColor: '#1d8cf8',
                    backgroundColor: pacoGradient,
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#1d8cf8',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                },
                {
                    label: 'FRAN Automation %',
                    data: data.fran_percentages,
                    borderColor: '#e14eca',
                    backgroundColor: franGradient,
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#e14eca',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                }
            ]
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
                    displayColors: true,
                    callbacks: {
                        label: function(context) {
                            const systemName = context.dataset.label.split(' ')[0]; // Get PACO or FRAN
                            const percentage = context.parsed.y;
                            return `${systemName}: ${percentage}%`;
                        },
                        footer: function(tooltipItems) {
                            const index = tooltipItems[0].dataIndex;
                            const count = data.payment_counts[index];
                            return `Total Payments: ${count}`;
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

// Region mapping
const REGION_MAP = {
    'Iberia': ['0040', '0041'],
    'France': ['0043'],
    'NDX': ['0019', '0022', '0023', '0024'],
    'UK': ['0014'],
    'BNX': ['0012', '0018'],
    'GerAus': ['0010', '0033'],
    'PLN': ['0023']
};

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

        // Populate company code filter
        const companyCodes = [...new Set(data.bank_accounts.map(acc => acc.value.split('|')[0]))].sort();
        const companyCodeSelect = document.getElementById('companyCodeFilterOnly');
        companyCodes.forEach(code => {
            const option = document.createElement('option');
            option.value = code;
            option.textContent = code;
            companyCodeSelect.appendChild(option);
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
    document.getElementById('regionFilter').value = '';
    document.getElementById('companyCodeFilterOnly').value = '';
    currentBankAccount = '';

    // Reload data without filters
    loadOverview();
    loadAutomationTrend();
    filterCompanyStatus();
}

// Filter company status cards based on region or company code
function filterCompanyStatus() {
    const regionFilter = document.getElementById('regionFilter').value;
    const companyCodeFilter = document.getElementById('companyCodeFilterOnly').value;
    
    const cards = document.querySelectorAll('.company-status-card');
    
    cards.forEach(card => {
        const companyCode = card.querySelector('.company-code-main').textContent.trim();
        let show = true;
        
        // Apply region filter
        if (regionFilter && REGION_MAP[regionFilter]) {
            show = REGION_MAP[regionFilter].includes(companyCode);
        }
        
        // Apply company code filter
        if (companyCodeFilter && show) {
            show = companyCode === companyCodeFilter;
        }
        
        card.style.display = show ? '' : 'none';
    });
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
    document.getElementById('regionFilter').addEventListener('change', filterCompanyStatus);
    document.getElementById('companyCodeFilterOnly').addEventListener('change', filterCompanyStatus);
    document.getElementById('clearFiltersBtn').addEventListener('click', clearAllFilters);

    // Setup refresh data button
    const refreshBtn = document.getElementById('refreshDataBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => {
            const now = new Date().toLocaleTimeString();
            console.log(`🔄 Manual refresh triggered at ${now}`);
            
            // Add spinning animation to refresh icon
            const icon = refreshBtn.querySelector('i');
            icon.classList.add('fa-spin');
            
            // Disable button during refresh
            refreshBtn.disabled = true;
            
            // Reload live data sections
            Promise.all([
                loadCompanyStatus(),
                loadRecentTransactions()
            ]).then(() => {
                // Remove spinning animation
                icon.classList.remove('fa-spin');
                refreshBtn.disabled = false;
                console.log(`✅ Live data refreshed successfully at ${new Date().toLocaleTimeString()}`);
                
                // Show a brief success indicator
                refreshBtn.style.backgroundColor = 'rgba(0, 242, 195, 0.2)';
                setTimeout(() => {
                    refreshBtn.style.backgroundColor = '';
                }, 1000);
            }).catch(error => {
                icon.classList.remove('fa-spin');
                refreshBtn.disabled = false;
                console.error('❌ Error refreshing data:', error);
            });
        });
    }

    // Setup smooth scrolling for sidebar navigation links
    document.querySelectorAll('.sidebar a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);

            if (targetElement) {
                e.preventDefault();
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });

                // Close sidebar on mobile after clicking
                if (window.innerWidth <= 991) {
                    document.querySelector('.sidebar').classList.remove('active');
                }
            }
        });
    });

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
    loadCompanyStatus();
    loadRecentTransactions();

    console.log('Dashboard loaded successfully');
});

// Load company code processing status
async function loadCompanyStatus() {
    try {
        // Add cache buster to ensure fresh data
        const cacheBuster = new Date().getTime();
        const response = await fetch(`/api/company-status?_=${cacheBuster}`);
        const data = await response.json();

        const timestamp = new Date().toLocaleTimeString();
        console.log(`Company status loaded: ${data.company_statuses.length} accounts at ${timestamp}`);

        // Update timestamp display
        const timestampElement = document.getElementById('companyStatusTimestamp');
        if (timestampElement) {
            timestampElement.textContent = timestamp;
        }

        const grid = document.getElementById('companyStatusGrid');
        grid.innerHTML = '';
        
        // Add a subtle flash effect to show refresh
        grid.style.opacity = '0.5';
        setTimeout(() => { grid.style.opacity = '1'; }, 100);

        data.company_statuses.forEach(company => {
            const statusClass = company.status.toLowerCase().replace(' ', '-');
            const card = document.createElement('div');
            card.className = `company-status-card ${statusClass}`;

            // Use real start/end times from API
            const startTime = company.start_time ? new Date(company.start_time) : null;
            const endTime = company.end_time ? new Date(company.end_time) : null;
            
            const formatTime = (date) => date ? date.toLocaleTimeString('en-US', {hour: '2-digit', minute: '2-digit'}) : '--:--';

            card.innerHTML = `
                <div class="company-status-header">
                    <div class="company-code-label">
                        <div class="company-code-main">
                            <i class="fas fa-building"></i>
                            ${company.company_code}
                        </div>
                        <div class="company-code-details">
                            ${company.housebank} • ${company.currency}
                        </div>
                    </div>
                    <span class="status-badge ${statusClass}">${company.status}</span>
                </div>
                <div class="company-progress">
                    <div class="progress-info">
                        <span>Progress</span>
                        <span><strong>${company.percentage}%</strong></span>
                    </div>
                    <div class="progress-bar-container">
                        <div class="progress-bar" style="width: ${company.percentage}%"></div>
                    </div>
                </div>
                <div class="company-time-info">
                    <span><span class="time-label">Start:</span>${formatTime(startTime)}</span>
                    <span><span class="time-label">End:</span>${formatTime(endTime)}</span>
                </div>
                <div class="company-details">
                    <span><i class="fas fa-check-circle"></i> Processed: ${company.processed}</span>
                    <span><i class="fas fa-clock"></i> Pending: ${company.pending}</span>
                </div>
                <div class="sap-login-hint">
                    <i class="fas fa-info-circle"></i> Ready for SAP login
                </div>
            `;

            grid.appendChild(card);
        });
    } catch (error) {
        console.error('Error loading company status:', error);
        showNotification('Error loading company status', 'error');
    }
}

// Load recent transactions from today's live data
async function loadRecentTransactions() {
    try {
        // Add cache buster to ensure fresh data
        const cacheBuster = new Date().getTime();
        const response = await fetch(`/api/recent-transactions?_=${cacheBuster}`);
        const data = await response.json();
        
        console.log(`Recent transactions loaded: ${data.transactions.length} transactions at ${new Date().toLocaleTimeString()}`);

        const listElement = document.getElementById('transactionList');
        listElement.innerHTML = '';

        if (data.transactions.length === 0) {
            listElement.innerHTML = `
                <li class="loading">
                    <p>No transactions found</p>
                </li>
            `;
            return;
        }

        data.transactions.forEach(transaction => {
            const li = document.createElement('li');
            const isMatch = transaction.match === 'YES';
            const typeClass = isMatch ? 'income' : 'expense';
            const icon = isMatch ? '✓' : '⏳';

            // Determine automation badge
            let automationBadge = '';
            if (transaction.match === 'YES') {
                automationBadge = '<span style="background: rgba(0, 242, 195, 0.2); color: var(--success-color); padding: 3px 8px; border-radius: 4px; font-size: 0.7rem; margin-left: 8px;">AUTO</span>';
            } else {
                automationBadge = '<span style="background: rgba(255, 141, 114, 0.2); color: var(--warning-color); padding: 3px 8px; border-radius: 4px; font-size: 0.7rem; margin-left: 8px;">PENDING</span>';
            }

            const bankAccount = `${transaction.company_code}-${transaction.housebank}-${transaction.currency}`;
            const description = `Payment ${transaction.payment_number} - ${bankAccount}${transaction.business_partner ? ' - ' + transaction.business_partner : ''}`;

            li.className = `transaction-item ${typeClass}`;
            li.innerHTML = `
                <div class="transaction-info">
                    <div class="transaction-date">
                        <i class="far fa-calendar"></i> ${transaction.payment_date}
                    </div>
                    <div class="transaction-description">
                        ${icon} ${description} ${automationBadge}
                    </div>
                </div>
                <div class="transaction-amount ${typeClass}">
                    ${formatCurrency(Math.abs(transaction.amount))}
                </div>
            `;

            listElement.appendChild(li);
        });
    } catch (error) {
        console.error('Error loading recent transactions:', error);
        const listElement = document.getElementById('transactionList');
        listElement.innerHTML = `
            <li class="loading">
                <p style="color: var(--danger-color);">Error loading transactions</p>
            </li>
        `;
    }
}

// Live data polling (every 5 minutes for company status and recent transactions)
setInterval(() => {
    console.log('Polling live data (5-minute interval)...');
    loadCompanyStatus();
    loadRecentTransactions();
}, 300000); // 5 minutes = 300,000 milliseconds

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
