// Black Dashboard - CashWeb JavaScript

// Mobile menu toggle
document.addEventListener('DOMContentLoaded', function() {
    // Mobile sidebar toggle
    const mobileToggle = document.querySelector('.mobile-menu-toggle');
    const sidebar = document.querySelector('.sidebar');

    if (mobileToggle && sidebar) {
        mobileToggle.addEventListener('click', function() {
            sidebar.classList.toggle('active');
        });

        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', function(event) {
            const isClickInsideSidebar = sidebar.contains(event.target);
            const isClickOnToggle = mobileToggle.contains(event.target);

            if (!isClickInsideSidebar && !isClickOnToggle && sidebar.classList.contains('active')) {
                sidebar.classList.remove('active');
            }
        });
    }

    // Load dashboard data
    loadDashboardData();

    // Auto-refresh every 30 seconds
    setInterval(loadDashboardData, 30000);

    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });
});

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Load dashboard data
async function loadDashboardData() {
    try {
        await Promise.all([
            loadSummary(),
            loadTransactions()
        ]);
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

// Load summary statistics
async function loadSummary() {
    try {
        const response = await fetch('/api/summary');
        const data = await response.json();

        // Update income card
        const incomeElement = document.getElementById('total-income');
        if (incomeElement) {
            incomeElement.textContent = formatCurrency(data.total_income);
            animateValue(incomeElement, 0, data.total_income);
        }

        // Update expenses card
        const expensesElement = document.getElementById('total-expenses');
        if (expensesElement) {
            expensesElement.textContent = formatCurrency(data.total_expenses);
            animateValue(expensesElement, 0, data.total_expenses);
        }

        // Update net cash flow card
        const netFlowElement = document.getElementById('net-cash-flow');
        if (netFlowElement) {
            netFlowElement.textContent = formatCurrency(data.net_cash_flow);
            animateValue(netFlowElement, 0, data.net_cash_flow);
        }

        // Update transaction count card
        const countElement = document.getElementById('transaction-count');
        if (countElement) {
            countElement.textContent = data.transaction_count;
        }

    } catch (error) {
        console.error('Error loading summary:', error);
    }
}

// Load transactions
async function loadTransactions() {
    try {
        const response = await fetch('/api/transactions');
        const transactions = await response.json();

        const tableBody = document.getElementById('transactions-table-body');
        if (!tableBody) return;

        // Clear loading spinner
        tableBody.innerHTML = '';

        if (transactions.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center" style="padding: 30px; color: #9a9a9a;">
                        No transactions found
                    </td>
                </tr>
            `;
            return;
        }

        // Populate transactions
        transactions.forEach((transaction, index) => {
            const row = document.createElement('tr');
            row.style.animationDelay = `${index * 0.05}s`;
            row.classList.add('fade-in');

            const typeClass = transaction.type === 'income' ? 'success' : 'danger';
            const typeIcon = transaction.type === 'income' ? '↑' : '↓';

            row.innerHTML = `
                <td><strong>${transaction.id}</strong></td>
                <td>${escapeHtml(transaction.description)}</td>
                <td>
                    <span class="badge badge-${typeClass}">
                        ${typeIcon} ${transaction.type.toUpperCase()}
                    </span>
                </td>
                <td><strong>${formatCurrency(transaction.amount)}</strong></td>
                <td>${formatDate(transaction.date)}</td>
            `;

            tableBody.appendChild(row);
        });

    } catch (error) {
        console.error('Error loading transactions:', error);
        const tableBody = document.getElementById('transactions-table-body');
        if (tableBody) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center" style="padding: 30px; color: #fd5d93;">
                        Error loading transactions
                    </td>
                </tr>
            `;
        }
    }
}

// Animate number value
function animateValue(element, start, end, duration = 1000) {
    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;

    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            current = end;
            clearInterval(timer);
        }
        element.textContent = formatCurrency(current);
    }, 16);
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Show notification (for future use)
function showNotification(message, type = 'info') {
    console.log(`[${type.toUpperCase()}] ${message}`);
    // Could implement toast notifications here
}

// Export functions for external use
window.CashWebDashboard = {
    loadDashboardData,
    loadSummary,
    loadTransactions,
    formatCurrency,
    formatDate
};
