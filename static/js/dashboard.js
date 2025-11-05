/**
 * CashWeb Dashboard - Black Dashboard Theme
 * JavaScript functionality for the cash management dashboard
 */

// Format currency with USD formatting
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Load summary data from API
async function loadSummary() {
    try {
        const response = await fetch('/api/summary');
        const data = await response.json();

        // Update stat values with animation
        updateStatValue('totalIncome', formatCurrency(data.total_income));
        updateStatValue('totalExpenses', formatCurrency(data.total_expenses));
        updateStatValue('netCash', formatCurrency(data.net_cash));
        updateStatValue('transactionCount', data.transaction_count);
    } catch (error) {
        console.error('Error loading summary:', error);
        showNotification('Error loading summary data', 'error');
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

        transactions.forEach(transaction => {
            const li = document.createElement('li');
            const typeClass = transaction.type === 'income' ? 'income' : 'expense';
            const amountSign = transaction.type === 'income' ? '+' : '-';
            const icon = transaction.type === 'income' ? '📈' : '📉';

            li.className = `transaction-item ${typeClass}`;
            li.innerHTML = `
                <div class="transaction-info">
                    <div class="transaction-date">
                        <i class="far fa-calendar"></i> ${formatDate(transaction.date)}
                    </div>
                    <div class="transaction-description">
                        ${icon} ${transaction.description}
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

// Add event listener for mobile menu toggle
document.addEventListener('DOMContentLoaded', () => {
    const mobileToggle = document.querySelector('.mobile-menu-toggle');
    if (mobileToggle) {
        mobileToggle.addEventListener('click', toggleSidebar);
    }

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
});

// Initialize dashboard
window.addEventListener('DOMContentLoaded', () => {
    console.log('CashWeb Dashboard initializing...');

    // Load initial data
    loadSummary();
    loadTransactions();

    console.log('Dashboard loaded successfully');
});

// Auto-refresh data every 30 seconds
setInterval(() => {
    loadSummary();
    loadTransactions();
}, 30000);

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
    }, 250);
});
