"""
CashWeb - Cash Management Web Application
A simple Flask application for tracking cash flow and expenses with automation analytics
"""
from flask import Flask, render_template, jsonify, request
from datetime import datetime, timedelta
import json
import random

app = Flask(__name__)

# Enhanced sample data with automation tracking
# Bank account configurations represent unique combinations of company_code + housebank + currency
# automation_system: PACO or FRAN (for automated transactions only)
# customer_id: customer identifier for assignment tracking
# invoices_assigned: number of invoices assigned from customer
transactions = [
    {"id": 1, "date": "2025-10-15", "description": "Remittance cleared for Customer 89732", "amount": 5000, "type": "income", "automated": True, "automation_system": "PACO", "assigned_minutes": 2, "company_code": "0014", "housebank": "1450I", "currency": "GBP2", "customer_id": "89732", "invoices_assigned": 3, "assigned_to_account": True},
    {"id": 2, "date": "2025-10-16", "description": "Remittance cleared for Customer 45891", "amount": 3200, "type": "income", "automated": True, "automation_system": "FRAN", "assigned_minutes": 1, "company_code": "0010", "housebank": "1050D", "currency": "EUR", "customer_id": "45891", "invoices_assigned": 2, "assigned_to_account": True},
    {"id": 3, "date": "2025-10-18", "description": "Remittance cleared for Customer 12456", "amount": 1800, "type": "income", "automated": False, "automation_system": None, "assigned_minutes": 45, "company_code": "0018", "housebank": "1850I", "currency": "EUR", "customer_id": "12456", "invoices_assigned": 1, "assigned_to_account": True},
    {"id": 4, "date": "2025-10-20", "description": "Remittance cleared for Customer 78234", "amount": 4500, "type": "income", "automated": True, "automation_system": "PACO", "assigned_minutes": 3, "company_code": "0015", "housebank": "CIT01", "currency": "OP272", "customer_id": "78234", "invoices_assigned": 4, "assigned_to_account": True},
    {"id": 5, "date": "2025-10-22", "description": "Remittance cleared for Customer 56789", "amount": 2700, "type": "income", "automated": False, "automation_system": None, "assigned_minutes": 62, "company_code": "0024", "housebank": "2439I", "currency": "NOK_2", "customer_id": "56789", "invoices_assigned": 2, "assigned_to_account": True},
    {"id": 6, "date": "2025-10-25", "description": "Remittance cleared for Customer 90123", "amount": 6200, "type": "income", "automated": True, "automation_system": "FRAN", "assigned_minutes": 2, "company_code": "0040", "housebank": "SAN01", "currency": "OP464", "customer_id": "90123", "invoices_assigned": 5, "assigned_to_account": True},
    {"id": 7, "date": "2025-10-28", "description": "Remittance cleared for Customer 34567", "amount": 3900, "type": "income", "automated": True, "automation_system": "PACO", "assigned_minutes": 1, "company_code": "0033", "housebank": "3350I", "currency": "EUR", "customer_id": "34567", "invoices_assigned": 2, "assigned_to_account": True},
    {"id": 8, "date": "2025-10-30", "description": "Remittance cleared for Customer 23890", "amount": 5500, "type": "income", "automated": False, "automation_system": None, "assigned_minutes": 38, "company_code": "0033", "housebank": "3350I", "currency": "USD", "customer_id": "23890", "invoices_assigned": 3, "assigned_to_account": True},
    {"id": 9, "date": "2025-11-01", "description": "Remittance cleared for Customer 67812", "amount": 4800, "type": "income", "automated": True, "automation_system": "FRAN", "assigned_minutes": 2, "company_code": "0012", "housebank": "570BE", "currency": "EUR", "customer_id": "67812", "invoices_assigned": 3, "assigned_to_account": True},
    {"id": 10, "date": "2025-11-02", "description": "Remittance cleared for Customer 98765", "amount": 7100, "type": "income", "automated": True, "automation_system": "PACO", "assigned_minutes": 1, "company_code": "0026", "housebank": "2602D", "currency": "PLN", "customer_id": "98765", "invoices_assigned": 6, "assigned_to_account": True},
    {"id": 11, "date": "2025-11-03", "description": "Remittance cleared for Customer 45678", "amount": 3300, "type": "income", "automated": False, "automation_system": None, "assigned_minutes": 52, "company_code": "0041", "housebank": "4150I", "currency": "EUR", "customer_id": "45678", "invoices_assigned": 2, "assigned_to_account": True},
    {"id": 12, "date": "2025-11-04", "description": "Remittance cleared for Customer 12389", "amount": 5900, "type": "income", "automated": True, "automation_system": "FRAN", "assigned_minutes": 3, "company_code": "0040", "housebank": "4050I", "currency": "EUR", "customer_id": "12389", "invoices_assigned": 4, "assigned_to_account": True},
    {"id": 13, "date": "2025-11-05", "description": "Remittance cleared for Customer 78901", "amount": 4200, "type": "income", "automated": True, "automation_system": "PACO", "assigned_minutes": 2, "company_code": "0042", "housebank": "4234D", "currency": "EUR", "customer_id": "78901", "invoices_assigned": 3, "assigned_to_account": True},
    {"id": 14, "date": "2025-11-05", "description": "Pending remittance for Customer 56123", "amount": 2800, "type": "income", "automated": None, "automation_system": None, "assigned_minutes": None, "company_code": "0044", "housebank": "4450I", "currency": "CZK", "customer_id": None, "invoices_assigned": 0, "assigned_to_account": False},
    {"id": 15, "date": "2025-11-05", "description": "Pending remittance for Customer 89456", "amount": 3600, "type": "income", "automated": None, "automation_system": None, "assigned_minutes": None, "company_code": "0043", "housebank": "4350I", "currency": "EUR", "customer_id": None, "invoices_assigned": 0, "assigned_to_account": False},
    {"id": 16, "date": "2025-11-01", "description": "Remittance cleared for Customer 23456", "amount": 5200, "type": "income", "automated": True, "automation_system": "FRAN", "assigned_minutes": 2, "company_code": "0041", "housebank": "4175I", "currency": "EUR", "customer_id": "23456", "invoices_assigned": 4, "assigned_to_account": True},
    {"id": 17, "date": "2025-11-02", "description": "Remittance cleared for Customer 34789", "amount": 4100, "type": "income", "automated": True, "automation_system": "PACO", "assigned_minutes": 1, "company_code": "0043", "housebank": "4335I", "currency": "EUR", "customer_id": "34789", "invoices_assigned": 3, "assigned_to_account": True},
    {"id": 18, "date": "2025-11-03", "description": "Remittance cleared for Customer 91234", "amount": 6300, "type": "income", "automated": False, "automation_system": None, "assigned_minutes": 48, "company_code": "0019", "housebank": "1939I", "currency": "EUR", "customer_id": "91234", "invoices_assigned": 5, "assigned_to_account": True},
    {"id": 19, "date": "2025-11-04", "description": "Remittance cleared for Customer 67890", "amount": 3800, "type": "income", "automated": True, "automation_system": "FRAN", "assigned_minutes": 2, "company_code": "0011", "housebank": "1101I", "currency": "CHF", "customer_id": "67890", "invoices_assigned": 2, "assigned_to_account": True},
    {"id": 20, "date": "2025-11-04", "description": "Remittance cleared for Customer 45123", "amount": 4900, "type": "income", "automated": True, "automation_system": "PACO", "assigned_minutes": 1, "company_code": "0022", "housebank": "2239X", "currency": "SEK", "customer_id": "45123", "invoices_assigned": 3, "assigned_to_account": True},
    {"id": 21, "date": "2025-11-05", "description": "Remittance cleared for Customer 78456", "amount": 5100, "type": "income", "automated": False, "automation_system": None, "assigned_minutes": 55, "company_code": "0011", "housebank": "1101D", "currency": "CHF", "customer_id": "78456", "invoices_assigned": 4, "assigned_to_account": True},
]

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/summary')
def get_summary():
    """Get cash flow summary"""
    total_income = sum(t['amount'] for t in transactions if t['type'] == 'income')
    total_expenses = abs(sum(t['amount'] for t in transactions if t['type'] == 'expense'))
    net_cash = total_income - total_expenses
    
    return jsonify({
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_cash': net_cash,
        'transaction_count': len(transactions)
    })

@app.route('/api/transactions')
def get_transactions():
    """Get all transactions"""
    return jsonify(transactions)

@app.route('/api/transactions', methods=['POST'])
def add_transaction():
    """Add a new transaction"""
    data = request.get_json()
    new_transaction = {
        'id': len(transactions) + 1,
        'date': data.get('date', datetime.now().strftime('%Y-%m-%d')),
        'description': data.get('description', ''),
        'amount': float(data.get('amount', 0)),
        'type': data.get('type', 'expense')
    }
    transactions.append(new_transaction)
    return jsonify(new_transaction), 201

@app.route('/api/filter-options')
def get_filter_options():
    """Get unique bank account configurations (company_code + housebank + currency combinations)"""
    # Get unique combinations of company_code, housebank, and currency
    bank_accounts = set()
    for t in transactions:
        if t.get('company_code') and t.get('housebank') and t.get('currency'):
            # Create a tuple representing the bank account configuration
            bank_account = (t['company_code'], t['housebank'], t['currency'])
            bank_accounts.add(bank_account)

    # Sort and format bank accounts for display
    bank_accounts_list = [
        {
            'value': f"{cc}|{hb}|{cur}",  # Use pipe separator for the filter value
            'label': f"{cc} - {hb} - {cur}"  # Human-readable label
        }
        for cc, hb, cur in sorted(bank_accounts)
    ]

    return jsonify({
        'bank_accounts': bank_accounts_list
    })

@app.route('/api/overview')
def get_overview():
    """Get dashboard overview with automation metrics"""
    period = request.args.get('period', 'today')  # today, week, month, quarter
    bank_account = request.args.get('bank_account', '')  # Combined filter: "company_code|housebank|currency"

    # Parse bank account filter if provided
    company_code, housebank, currency = '', '', ''
    if bank_account:
        parts = bank_account.split('|')
        if len(parts) == 3:
            company_code, housebank, currency = parts

    # Calculate date range
    today = datetime.now().date()
    if period == 'today':
        start_date = today
    elif period == 'week':
        start_date = today - timedelta(days=7)
    elif period == 'month':
        start_date = today - timedelta(days=30)
    elif period == 'quarter':
        start_date = today - timedelta(days=90)
    else:
        start_date = today

    # Filter transactions by date range, type, and bank account configuration
    filtered = [
        t for t in transactions
        if datetime.strptime(t['date'], '%Y-%m-%d').date() >= start_date
        and t['type'] == 'income'
        and (not bank_account or (
            t.get('company_code', '') == company_code
            and t.get('housebank', '') == housebank
            and t.get('currency', '') == currency
        ))
    ]

    # Calculate metrics
    total_payments = len(filtered)
    total_received = sum(t['amount'] for t in filtered)

    # Automation metrics
    automated = [t for t in filtered if t.get('automated') == True]
    manual = [t for t in filtered if t.get('automated') == False]
    unassigned = [t for t in filtered if t.get('automated') is None]

    automation_percentage = (len(automated) / total_payments * 100) if total_payments > 0 else 0

    # Calculate average assignment time
    auto_times = [t['assigned_minutes'] for t in automated if t.get('assigned_minutes')]
    manual_times = [t['assigned_minutes'] for t in manual if t.get('assigned_minutes')]

    avg_auto_time = sum(auto_times) / len(auto_times) if auto_times else 0
    avg_manual_time = sum(manual_times) / len(manual_times) if manual_times else 0

    # Customer account assignment metrics
    assigned_to_account = [t for t in filtered if t.get('assigned_to_account') == True]
    assigned_percentage = (len(assigned_to_account) / total_payments * 100) if total_payments > 0 else 0

    # Invoice assignment metrics
    total_invoices_assigned = sum(t.get('invoices_assigned', 0) for t in filtered)

    # Value assignment metrics
    total_assigned_value = sum(t['amount'] for t in assigned_to_account)
    value_assigned_percentage = (total_assigned_value / total_received * 100) if total_received > 0 else 0
    unassigned_value = sum(t['amount'] for t in unassigned)

    return jsonify({
        'period': period,
        'total_payments': total_payments,
        'total_received': total_received,
        'automation_percentage': round(automation_percentage, 1),
        'automated_count': len(automated),
        'manual_count': len(manual),
        'unassigned_count': len(unassigned),
        'unassigned_value': unassigned_value,
        'assigned_percentage': round(assigned_percentage, 1),
        'assigned_count': len(assigned_to_account),
        'total_invoices_assigned': total_invoices_assigned,
        'total_assigned_value': total_assigned_value,
        'value_assigned_percentage': round(value_assigned_percentage, 1),
        'avg_auto_time_minutes': round(avg_auto_time, 1),
        'avg_manual_time_minutes': round(avg_manual_time, 1),
    })

@app.route('/api/automation-trend')
def get_automation_trend():
    """Get automation trend data for charts"""
    period = request.args.get('period', 'week')  # week, month, quarter
    bank_account = request.args.get('bank_account', '')  # Combined filter: "company_code|housebank|currency"

    # Parse bank account filter if provided
    company_code, housebank, currency = '', '', ''
    if bank_account:
        parts = bank_account.split('|')
        if len(parts) == 3:
            company_code, housebank, currency = parts

    # Calculate date range
    today = datetime.now().date()
    if period == 'week':
        days = 7
        start_date = today - timedelta(days=days)
    elif period == 'month':
        days = 30
        start_date = today - timedelta(days=days)
    elif period == 'quarter':
        days = 90
        start_date = today - timedelta(days=days)
    else:
        days = 7
        start_date = today - timedelta(days=days)

    # Group transactions by date - track PACO and FRAN separately
    date_groups = {}
    current_date = start_date
    while current_date <= today:
        date_str = current_date.strftime('%Y-%m-%d')
        date_groups[date_str] = {'paco': 0, 'fran': 0, 'manual': 0, 'total': 0}
        current_date += timedelta(days=1)

    # Count transactions per day with filtering
    for t in transactions:
        if (t['type'] == 'income' and t.get('automated') is not None
            and (not bank_account or (
                t.get('company_code', '') == company_code
                and t.get('housebank', '') == housebank
                and t.get('currency', '') == currency
            ))):
            t_date = t['date']
            if t_date in date_groups:
                date_groups[t_date]['total'] += 1
                if t.get('automated'):
                    automation_system = t.get('automation_system', '')
                    if automation_system == 'PACO':
                        date_groups[t_date]['paco'] += 1
                    elif automation_system == 'FRAN':
                        date_groups[t_date]['fran'] += 1
                else:
                    date_groups[t_date]['manual'] += 1

    # Calculate automation percentages per day for PACO and FRAN
    labels = []
    paco_percentages = []
    fran_percentages = []
    payment_counts = []

    for date_str in sorted(date_groups.keys()):
        data = date_groups[date_str]
        total = data['total']
        paco_pct = (data['paco'] / total * 100) if total > 0 else 0
        fran_pct = (data['fran'] / total * 100) if total > 0 else 0

        # Format label based on period
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        if period == 'week':
            label = date_obj.strftime('%a %m/%d')
        elif period == 'month':
            label = date_obj.strftime('%m/%d')
        else:
            label = date_obj.strftime('%m/%d')

        labels.append(label)
        paco_percentages.append(round(paco_pct, 1))
        fran_percentages.append(round(fran_pct, 1))
        payment_counts.append(total)

    return jsonify({
        'labels': labels,
        'paco_percentages': paco_percentages,
        'fran_percentages': fran_percentages,
        'payment_counts': payment_counts
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'CashWeb'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

