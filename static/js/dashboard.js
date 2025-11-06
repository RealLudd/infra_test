/**
 * CashWeb Dashboard - Black Dashboard Theme
 * Enhanced JavaScript with automation analytics and charting
 */

// Global variables
let currentPeriod = 'week';
let currentChartPeriod = 'week';
let automationChart = null;
let currentBankAccount = '';  // Combined filter: "company_code|housebank|currency"
let currentRegion = '';  // Region filter
let currentCompanyCode = '';  // Company code filter
let allBankAccounts = [];  // Store all bank accounts for cascading filters

// Format currency with EUR formatting
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'EUR',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

// Format number with thousand separators (e.g., 6,563)
function formatNumber(number) {
    return new Intl.NumberFormat('en-US').format(number);
}

// Load overview data from API
async function loadOverview() {
    try {
        const params = new URLSearchParams({
            period: currentPeriod,
            bank_account: currentBankAccount,
            region: currentRegion,
            company_code: currentCompanyCode
        });
        const response = await fetch(`/api/overview?${params}`);
        const data = await response.json();

        // 1. Update Total Payments Received (Amount)
        updateStatValue('totalReceived', formatCurrency(data.total_received));

        // 2. Update Total Payments (Number)
        updateStatValue('totalPayments', formatNumber(data.total_payments));

        // 3. Update Processed Automatically
        updateStatValue('automationPercentage', `${data.automation_percentage}%`);
        document.getElementById('automationDetail').innerHTML =
            `<span>${formatNumber(data.automated_count)} / ${formatNumber(data.total_payments)} payments</span>`;

        // 4. Update Payments Posted to Customer Accounts
        updateStatValue('assignedAccountPercentage', `${data.assigned_percentage}%`);
        document.getElementById('assignedAccountDetail').innerHTML =
            `<span>${formatNumber(data.assigned_count)} / ${formatNumber(data.total_payments)} payments</span>`;

        // 5. Update Number of Invoices Cleared
        updateStatValue('totalInvoices', formatNumber(data.total_invoices_assigned));

        // 6. Update Invoices Amount Cleared (%)
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
            bank_account: currentBankAccount,
            region: currentRegion,
            company_code: currentCompanyCode
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
                            return `Total Payments: ${formatNumber(count)}`;
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
        console.log('Loading filter options...');
        const response = await fetch('/api/filter-options');
        const data = await response.json();
        
        console.log(`Loaded ${data.bank_accounts.length} bank accounts for filters`);
        
        // Store all bank accounts globally for cascading filters
        allBankAccounts = data.bank_accounts;
        
        // Populate filters
        updateFilterDropdowns();
    } catch (error) {
        console.error('Error loading filter options:', error);
    }
}

// Update filter dropdowns based on current selections (cascading filters)
function updateFilterDropdowns() {
    const regionFilter = document.getElementById('regionFilter')?.value || '';
    const companyCodeFilter = document.getElementById('companyCodeFilterOnly')?.value || '';
    
    // Filter bank accounts based on region or company code
    let filteredAccounts = allBankAccounts;
    let availableCompanyCodes = [];
    
    if (regionFilter && REGION_MAP[regionFilter]) {
        // Filter by region
        const regionCodes = REGION_MAP[regionFilter];
        filteredAccounts = allBankAccounts.filter(acc => {
            const code = acc.value.split('|')[0];
            return regionCodes.includes(code);
        });
        availableCompanyCodes = regionCodes;
    } else if (companyCodeFilter) {
        // Filter by company code
        filteredAccounts = allBankAccounts.filter(acc => {
            const code = acc.value.split('|')[0];
            return code === companyCodeFilter;
        });
        availableCompanyCodes = [companyCodeFilter];
    } else {
        // No filter - show all
        availableCompanyCodes = [...new Set(allBankAccounts.map(acc => acc.value.split('|')[0]))].sort();
    }
    
    // Update Company Code dropdown
    const companyCodeSelect = document.getElementById('companyCodeFilterOnly');
    if (companyCodeSelect) {
        const currentValue = companyCodeSelect.value;
        companyCodeSelect.innerHTML = '<option value="">All Company Codes</option>';
        
        availableCompanyCodes.sort().forEach(code => {
            const option = document.createElement('option');
            option.value = code;
            option.textContent = code;
            if (code === currentValue) {
                option.selected = true;
            }
            companyCodeSelect.appendChild(option);
        });
    }
    
    // Update Bank Account dropdown
    const bankAccountSelect = document.getElementById('bankAccountFilter');
    if (bankAccountSelect) {
        const currentValue = bankAccountSelect.value;
        bankAccountSelect.innerHTML = '<option value="">All Bank Accounts</option>';
        
        filteredAccounts.forEach(account => {
            const option = document.createElement('option');
            option.value = account.value;
            option.textContent = account.label;
            if (account.value === currentValue) {
                option.selected = true;
            }
            bankAccountSelect.appendChild(option);
        });
    }
    
    console.log(`Updated dropdowns - ${availableCompanyCodes.length} company codes, ${filteredAccounts.length} bank accounts`);
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
    currentRegion = '';
    currentCompanyCode = '';

    // Reset dropdowns to show all options
    updateFilterDropdowns();

    // Reload data without filters
    loadOverview();
    loadAutomationTrend();
    filterCompanyStatus();
}

// Filter company status cards and reload overview data
function filterCompanyStatus() {
    const regionFilter = document.getElementById('regionFilter')?.value || '';
    const companyCodeFilter = document.getElementById('companyCodeFilterOnly')?.value || '';
    
    // Update global filter state
    currentRegion = regionFilter;
    currentCompanyCode = companyCodeFilter;
    
    console.log(`Filtering - Region: "${regionFilter}", Company Code: "${companyCodeFilter}"`);
    
    // Reload overview and trend data with new filters
    loadOverview();
    loadAutomationTrend();
    
    const cards = document.querySelectorAll('.company-status-card');
    let visibleCount = 0;
    
    if (cards.length === 0) {
        console.log('No cards found to filter - cards not loaded yet?');
        return;
    }
    
    // Debug: show all company codes in cards
    const allCodes = Array.from(cards).map(c => c.getAttribute('data-company-code'));
    console.log(`All company codes in cards: [${allCodes.join(', ')}]`);
    
    if (regionFilter) {
        console.log(`Region "${regionFilter}" maps to codes: [${REGION_MAP[regionFilter]?.join(', ') || 'NOT FOUND'}]`);
    }
    
    cards.forEach(card => {
        // Get company code from data attribute (more reliable than parsing text)
        const companyCode = card.getAttribute('data-company-code');
        
        if (!companyCode) {
            console.warn('Card missing data-company-code attribute:', card);
            return;
        }
        
        let show = true;
        let hideReason = '';
        
        // Apply region filter
        if (regionFilter && REGION_MAP[regionFilter]) {
            show = REGION_MAP[regionFilter].includes(companyCode);
            if (!show) {
                hideReason = `not in region ${regionFilter} (expected: ${REGION_MAP[regionFilter].join(', ')})`;
            }
        }
        
        // Apply company code filter
        if (companyCodeFilter && show) {
            show = companyCode === companyCodeFilter;
            if (!show) {
                hideReason = `doesn't match filter "${companyCodeFilter}" (card has "${companyCode}")`;
            }
        }
        
        if (!show) {
            console.log(`  Hiding ${companyCode} - ${hideReason}`);
        }
        
        if (show) visibleCount++;
        card.style.display = show ? '' : 'none';
    });
    
    console.log(`Filter result: ${visibleCount} cards visible out of ${cards.length}`);
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
    document.getElementById('regionFilter').addEventListener('change', () => {
        updateFilterDropdowns();  // Update cascading dropdowns
        filterCompanyStatus();    // Apply filter
    });
    document.getElementById('companyCodeFilterOnly').addEventListener('change', () => {
        updateFilterDropdowns();  // Update cascading dropdowns
        filterCompanyStatus();    // Apply filter
    });
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

    // Navigation is handled by setupCustomerExceptionsNav() below

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

    // Setup navigation handlers
    setupCustomerExceptionsNav();
    setupCustomerExceptionsListeners();

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
            
            // Store company code as data attribute for filtering
            card.setAttribute('data-company-code', company.company_code);

            // Use real start/end times from API
            const startTime = company.start_time ? new Date(company.start_time) : null;
            const endTime = company.end_time ? new Date(company.end_time) : null;
            
            const formatTime = (date) => date ? date.toLocaleTimeString('en-US', {hour: '2-digit', minute: '2-digit'}) : '--:--';

            const matchedPercentage = company.matched_percentage || 0;
            const valuePercentage = company.value_assigned_percentage || 0;
            
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
                        <span>Processed Automatically</span>
                        <span><strong>${matchedPercentage}%</strong></span>
                    </div>
                    <div class="progress-bar-container">
                        <div class="progress-bar" style="width: ${matchedPercentage}%"></div>
                    </div>
                </div>
                <div class="company-progress" style="margin-top: 8px;">
                    <div class="progress-info">
                        <span>Invoices Amount Cleared</span>
                        <span><strong>${valuePercentage}%</strong></span>
                    </div>
                    <div class="progress-bar-container">
                        <div class="progress-bar" style="width: ${valuePercentage}%; background: linear-gradient(90deg, #fd5d93 0%, #ec250d 100%);"></div>
                    </div>
                </div>
                <div class="company-time-info">
                    <span><span class="time-label">Start:</span>${formatTime(startTime)}</span>
                    <span><span class="time-label">End:</span>${formatTime(endTime)}</span>
                </div>
                <div class="company-details">
                    <span><i class="fas fa-user-check"></i> Posted to Customer Accounts: ${company.customers_assigned || 0}</span>
                    <span><i class="fas fa-file-invoice"></i> Invoices Cleared: ${company.invoices_assigned || 0}</span>
                </div>
                <div class="company-details">
                    <span><i class="fas fa-list"></i> Total Payments Received: ${company.total}</span>
                </div>
                <div class="sap-login-hint">
                    <i class="fas fa-info-circle"></i> Ready for SAP login
                </div>
            `;

            grid.appendChild(card);
        });
        
        // Apply any active filters after cards are loaded
        filterCompanyStatus();
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

// ============================================
// CUSTOMER EXCEPTIONS FUNCTIONALITY
// ============================================

// Navigation handling for Customer Exceptions tab
function setupCustomerExceptionsNav() {
    const navLinks = document.querySelectorAll('.sidebar-menu a');

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            const navType = link.getAttribute('data-nav');

            if (navType === 'customer-exceptions') {
                e.preventDefault();

                // Update active state
                navLinks.forEach(l => l.classList.remove('active'));
                link.classList.add('active');

                // Hide dashboard sections, show customer exceptions
                document.querySelectorAll('.content > div:not(#customer-exceptions)').forEach(el => {
                    if (el.id !== 'customer-exceptions') {
                        el.style.display = 'none';
                    }
                });

                const exceptionsSection = document.getElementById('customer-exceptions');
                exceptionsSection.style.display = 'block';

                // Update navbar title
                document.querySelector('.navbar h2').innerHTML = '<i class="fas fa-user-shield"></i> Customer Exceptions';

                // Load customer exceptions data
                loadExceptionFilterOptions();
                loadCustomerExceptions();
            } else if (navType === 'dashboard') {
                e.preventDefault();

                // Update active state
                navLinks.forEach(l => l.classList.remove('active'));
                link.classList.add('active');

                // Show dashboard sections, hide customer exceptions
                document.querySelectorAll('.content > div:not(#customer-exceptions)').forEach(el => {
                    if (el.id !== 'customer-exceptions') {
                        el.style.display = 'block';
                    }
                });

                document.getElementById('customer-exceptions').style.display = 'none';

                // Update navbar title
                document.querySelector('.navbar h2').innerHTML = '<i class="fas fa-chart-line"></i> Dashboard Overview';
            } else if (navType === 'transactions') {
                e.preventDefault();

                // Update active state
                navLinks.forEach(l => l.classList.remove('active'));
                link.classList.add('active');

                // Show dashboard sections, hide customer exceptions
                document.querySelectorAll('.content > div:not(#customer-exceptions)').forEach(el => {
                    if (el.id !== 'customer-exceptions') {
                        el.style.display = 'block';
                    }
                });

                document.getElementById('customer-exceptions').style.display = 'none';

                // Update navbar title
                document.querySelector('.navbar h2').innerHTML = '<i class="fas fa-exchange-alt"></i> Transactions';

                // Scroll to transactions section
                const transactionsSection = document.getElementById('transactions');
                if (transactionsSection) {
                    transactionsSection.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }

                // Close sidebar on mobile
                if (window.innerWidth <= 991) {
                    document.querySelector('.sidebar').classList.remove('active');
                }
            }
        });
    });
}

// Load filter options for Customer Exceptions
async function loadExceptionFilterOptions() {
    try {
        const response = await fetch('/api/filter-options');
        const data = await response.json();

        // Populate bank account filter (same as dashboard)
        const bankAccountSelect = document.getElementById('exceptionBankAccount');
        bankAccountSelect.innerHTML = '<option value="">All Bank Accounts</option>';

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

// Load customer exceptions with optional filters
async function loadCustomerExceptions() {
    const bankAccount = document.getElementById('exceptionBankAccount').value;
    const businessPartner = document.getElementById('exceptionBusinessPartner').value;
    const partnerKey = document.getElementById('exceptionPartnerKey').value;
    const partnerRef = document.getElementById('exceptionPartnerRef').value;

    const params = new URLSearchParams();

    // Parse bank account value (format: "company_code|housebank|currency")
    if (bankAccount) {
        const [companyCode, houseBank, currency] = bankAccount.split('|');
        if (companyCode) params.append('company_code', companyCode);
        if (houseBank) params.append('housebank', houseBank);
        if (currency) params.append('currency', currency);
    }

    if (businessPartner) params.append('business_partner', businessPartner);
    if (partnerKey) params.append('partner_key', partnerKey);
    if (partnerRef) params.append('partner_ref', partnerRef);

    try {
        const response = await fetch(`/api/customer-exceptions?${params.toString()}`);
        const data = await response.json();

        renderExceptionsTable(data.exceptions);
    } catch (error) {
        console.error('Error loading customer exceptions:', error);
        document.getElementById('exceptionsTableBody').innerHTML = `
            <tr>
                <td colspan="8" style="text-align: center; padding: 40px; color: var(--danger-color);">
                    Error loading exceptions
                </td>
            </tr>
        `;
    }
}

// Render exceptions table
function renderExceptionsTable(exceptions) {
    const tbody = document.getElementById('exceptionsTableBody');

    if (exceptions.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" style="text-align: center; padding: 40px; color: var(--text-secondary);">
                    No exceptions found. Click "Add Exception" to create one.
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = '';

    exceptions.forEach(exception => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${exception.company_code || '-'}</td>
            <td>${exception.housebank || '-'}</td>
            <td>${exception.currency || '-'}</td>
            <td>${exception.business_partner || '-'}</td>
            <td>${exception.partner_key || '-'}</td>
            <td>${exception.partner_ref || '-'}</td>
            <td>
                <span class="exception-type-badge ${exception.exception_type}">
                    ${exception.exception_type === 'included' ? 'Included' : 'Excluded'}
                </span>
            </td>
            <td>
                <button class="action-btn" onclick="editException(${exception.id})">
                    <i class="fas fa-edit"></i> Edit
                </button>
                <button class="action-btn delete" onclick="deleteException(${exception.id})">
                    <i class="fas fa-trash"></i> Delete
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Open modal for adding exception
function openAddExceptionModal() {
    document.getElementById('exceptionModalTitle').innerHTML = '<i class="fas fa-user-shield"></i> Add Customer Exception';
    document.getElementById('exceptionId').value = '';
    document.getElementById('modalCompanyCode').value = '';
    document.getElementById('modalHouseBank').value = '';
    document.getElementById('modalCurrency').value = '';
    document.getElementById('modalBusinessPartner').value = '';
    document.getElementById('modalPartnerKey').value = '';
    document.getElementById('modalPartnerRef').value = '';
    document.getElementById('modalExceptionType').value = '';
    document.getElementById('exceptionModal').style.display = 'flex';
}

// Edit exception
async function editException(id) {
    try {
        // Get all exceptions and find the one to edit
        const response = await fetch('/api/customer-exceptions');
        const data = await response.json();
        const exception = data.exceptions.find(e => e.id === id);

        if (!exception) {
            alert('Exception not found');
            return;
        }

        // Populate modal with exception data
        document.getElementById('exceptionModalTitle').innerHTML = '<i class="fas fa-user-shield"></i> Edit Customer Exception';
        document.getElementById('exceptionId').value = exception.id;
        document.getElementById('modalCompanyCode').value = exception.company_code || '';
        document.getElementById('modalHouseBank').value = exception.housebank || '';
        document.getElementById('modalCurrency').value = exception.currency || '';
        document.getElementById('modalBusinessPartner').value = exception.business_partner || '';
        document.getElementById('modalPartnerKey').value = exception.partner_key || '';
        document.getElementById('modalPartnerRef').value = exception.partner_ref || '';
        document.getElementById('modalExceptionType').value = exception.exception_type || '';
        document.getElementById('exceptionModal').style.display = 'flex';
    } catch (error) {
        console.error('Error loading exception for edit:', error);
        alert('Error loading exception data');
    }
}

// Delete exception
async function deleteException(id) {
    if (!confirm('Are you sure you want to delete this exception?')) {
        return;
    }

    try {
        const response = await fetch(`/api/customer-exceptions/${id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            alert('Exception deleted successfully');
            loadCustomerExceptions();
        } else {
            const error = await response.json();
            alert(`Error deleting exception: ${error.error}`);
        }
    } catch (error) {
        console.error('Error deleting exception:', error);
        alert('Error deleting exception');
    }
}

// Save exception (create or update)
async function saveException() {
    const id = document.getElementById('exceptionId').value;
    const companyCode = document.getElementById('modalCompanyCode').value.trim();
    const houseBank = document.getElementById('modalHouseBank').value.trim();
    const currency = document.getElementById('modalCurrency').value.trim();
    const businessPartner = document.getElementById('modalBusinessPartner').value.trim();
    const partnerKey = document.getElementById('modalPartnerKey').value.trim();
    const partnerRef = document.getElementById('modalPartnerRef').value.trim();
    const exceptionType = document.getElementById('modalExceptionType').value;

    // Validate required fields
    if (!companyCode || !houseBank || !currency || !businessPartner || !exceptionType) {
        alert('Please fill in all required fields (marked with *)');
        return;
    }

    const exceptionData = {
        company_code: companyCode,
        housebank: houseBank,
        currency: currency,
        business_partner: businessPartner,
        partner_key: partnerKey,
        partner_ref: partnerRef,
        exception_type: exceptionType
    };

    try {
        let response;
        if (id) {
            // Update existing exception
            response = await fetch(`/api/customer-exceptions/${id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(exceptionData)
            });
        } else {
            // Create new exception
            response = await fetch('/api/customer-exceptions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(exceptionData)
            });
        }

        if (response.ok) {
            alert(id ? 'Exception updated successfully' : 'Exception created successfully');
            closeExceptionModal();
            loadCustomerExceptions();
        } else {
            const error = await response.json();
            alert(`Error saving exception: ${error.error}`);
        }
    } catch (error) {
        console.error('Error saving exception:', error);
        alert('Error saving exception');
    }
}

// Close exception modal
function closeExceptionModal() {
    document.getElementById('exceptionModal').style.display = 'none';
}

// Setup customer exceptions event listeners
function setupCustomerExceptionsListeners() {
    // Add exception button
    document.getElementById('addExceptionBtn').addEventListener('click', openAddExceptionModal);

    // Apply filters button
    document.getElementById('applyExceptionFiltersBtn').addEventListener('click', loadCustomerExceptions);

    // Clear filters button
    document.getElementById('clearExceptionFiltersBtn').addEventListener('click', () => {
        document.getElementById('exceptionBankAccount').value = '';
        document.getElementById('exceptionBusinessPartner').value = '';
        document.getElementById('exceptionPartnerKey').value = '';
        document.getElementById('exceptionPartnerRef').value = '';
        loadCustomerExceptions();
    });

    // Save exception button
    document.getElementById('saveExceptionBtn').addEventListener('click', saveException);

    // Cancel modal button
    document.getElementById('cancelExceptionModal').addEventListener('click', closeExceptionModal);

    // Close modal button
    document.getElementById('closeExceptionModal').addEventListener('click', closeExceptionModal);

    // Close modal on backdrop click
    document.getElementById('exceptionModal').addEventListener('click', (e) => {
        if (e.target.id === 'exceptionModal') {
            closeExceptionModal();
        }
    });
}

// Customer Exceptions functionality is initialized in DOMContentLoaded above
