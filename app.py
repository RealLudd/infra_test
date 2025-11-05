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
transactions = [
    {"id": 1, "date": "2025-10-15", "description": "Client Payment A", "amount": 5000, "type": "income", "automated": True, "assigned_minutes": 2, "company_code": "0014", "housebank": "1450I", "currency": "GBP2"},
    {"id": 2, "date": "2025-10-16", "description": "Client Payment B", "amount": 3200, "type": "income", "automated": True, "assigned_minutes": 1, "company_code": "0010", "housebank": "1050D", "currency": "EUR"},
    {"id": 3, "date": "2025-10-18", "description": "Client Payment C", "amount": 1800, "type": "income", "automated": False, "assigned_minutes": 45, "company_code": "0018", "housebank": "1850I", "currency": "EUR"},
    {"id": 4, "date": "2025-10-20", "description": "Client Payment D", "amount": 4500, "type": "income", "automated": True, "assigned_minutes": 3, "company_code": "0015", "housebank": "CIT01", "currency": "OP272"},
    {"id": 5, "date": "2025-10-22", "description": "Client Payment E", "amount": 2700, "type": "income", "automated": False, "assigned_minutes": 62, "company_code": "0024", "housebank": "2439I", "currency": "NOK_2"},
    {"id": 6, "date": "2025-10-25", "description": "Client Payment F", "amount": 6200, "type": "income", "automated": True, "assigned_minutes": 2, "company_code": "0040", "housebank": "SAN01", "currency": "OP464"},
    {"id": 7, "date": "2025-10-28", "description": "Client Payment G", "amount": 3900, "type": "income", "automated": True, "assigned_minutes": 1, "company_code": "0033", "housebank": "3350I", "currency": "EUR"},
    {"id": 8, "date": "2025-10-30", "description": "Client Payment H", "amount": 5500, "type": "income", "automated": False, "assigned_minutes": 38, "company_code": "0033", "housebank": "3350I", "currency": "USD"},
    {"id": 9, "date": "2025-11-01", "description": "Client Payment I", "amount": 4800, "type": "income", "automated": True, "assigned_minutes": 2, "company_code": "0012", "housebank": "570BE", "currency": "EUR"},
    {"id": 10, "date": "2025-11-02", "description": "Client Payment J", "amount": 7100, "type": "income", "automated": True, "assigned_minutes": 1, "company_code": "0026", "housebank": "2602D", "currency": "PLN"},
    {"id": 11, "date": "2025-11-03", "description": "Client Payment K", "amount": 3300, "type": "income", "automated": False, "assigned_minutes": 52, "company_code": "0041", "housebank": "4150I", "currency": "EUR"},
    {"id": 12, "date": "2025-11-04", "description": "Client Payment L", "amount": 5900, "type": "income", "automated": True, "assigned_minutes": 3, "company_code": "0040", "housebank": "4050I", "currency": "EUR"},
    {"id": 13, "date": "2025-11-05", "description": "Client Payment M", "amount": 4200, "type": "income", "automated": True, "assigned_minutes": 2, "company_code": "0042", "housebank": "4234D", "currency": "EUR"},
    {"id": 14, "date": "2025-11-05", "description": "Client Payment N", "amount": 2800, "type": "income", "automated": None, "assigned_minutes": None, "company_code": "0044", "housebank": "4450I", "currency": "CZK"},
    {"id": 15, "date": "2025-11-05", "description": "Client Payment O", "amount": 3600, "type": "income", "automated": None, "assigned_minutes": None, "company_code": "0043", "housebank": "4350I", "currency": "EUR"},
    {"id": 16, "date": "2025-11-01", "description": "Client Payment P", "amount": 5200, "type": "income", "automated": True, "assigned_minutes": 2, "company_code": "0041", "housebank": "4175I", "currency": "EUR"},
    {"id": 17, "date": "2025-11-02", "description": "Client Payment Q", "amount": 4100, "type": "income", "automated": True, "assigned_minutes": 1, "company_code": "0043", "housebank": "4335I", "currency": "EUR"},
    {"id": 18, "date": "2025-11-03", "description": "Client Payment R", "amount": 6300, "type": "income", "automated": False, "assigned_minutes": 48, "company_code": "0019", "housebank": "1939I", "currency": "EUR"},
    {"id": 19, "date": "2025-11-04", "description": "Client Payment S", "amount": 3800, "type": "income", "automated": True, "assigned_minutes": 2, "company_code": "0011", "housebank": "1101I", "currency": "CHF"},
    {"id": 20, "date": "2025-11-04", "description": "Client Payment T", "amount": 4900, "type": "income", "automated": True, "assigned_minutes": 1, "company_code": "0022", "housebank": "2239X", "currency": "SEK"},
    {"id": 21, "date": "2025-11-05", "description": "Client Payment U", "amount": 5100, "type": "income", "automated": False, "assigned_minutes": 55, "company_code": "0011", "housebank": "1101D", "currency": "CHF"},
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

    # Calculate values
    total_assigned_value = sum(t['amount'] for t in filtered if t.get('automated') is not None)
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
        'total_assigned_value': total_assigned_value,
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

    # Group transactions by date
    date_groups = {}
    current_date = start_date
    while current_date <= today:
        date_str = current_date.strftime('%Y-%m-%d')
        date_groups[date_str] = {'automated': 0, 'manual': 0, 'total': 0}
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
                    date_groups[t_date]['automated'] += 1
                else:
                    date_groups[t_date]['manual'] += 1

    # Calculate automation percentage per day
    labels = []
    automation_percentages = []
    payment_counts = []

    for date_str in sorted(date_groups.keys()):
        data = date_groups[date_str]
        total = data['total']
        auto_pct = (data['automated'] / total * 100) if total > 0 else 0

        # Format label based on period
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        if period == 'week':
            label = date_obj.strftime('%a %m/%d')
        elif period == 'month':
            label = date_obj.strftime('%m/%d')
        else:
            label = date_obj.strftime('%m/%d')

        labels.append(label)
        automation_percentages.append(round(auto_pct, 1))
        payment_counts.append(total)

    return jsonify({
        'labels': labels,
        'automation_percentages': automation_percentages,
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

