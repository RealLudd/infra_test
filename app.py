"""
CashWeb - Cash Management Web Application
A Flask application for tracking payment automation and cash flow analytics
"""
from flask import Flask, render_template, jsonify, request
from datetime import datetime, timedelta
from collections import defaultdict
import json
import random

app = Flask(__name__)

# Extended payment data model for automation tracking
# Fields:
# - id: unique identifier
# - date: payment date
# - customer_name: customer identifier
# - customer_id: SAP customer ID
# - amount: payment amount
# - status: auto_assigned, manual_assigned, unassigned
# - assignment_method: bank_match, reference_match, name_match, manual, none
# - processing_time: time to assign in minutes
# - error_reason: reason for failure (if applicable)
# - sap_posted: whether posted to SAP
# - remittance_received: whether remittance advice received
# - invoice_references: related invoices

def generate_sample_payments():
    """Generate realistic payment automation sample data"""
    payments = []
    customers = [
        "Acme Corp", "TechStart Inc", "Global Solutions", "Metro Retail",
        "Pacific Industries", "Sunrise Manufacturing", "Delta Services",
        "Omega Electronics", "Alpha Logistics", "Beta Distribution",
        "Gamma Enterprises", "Epsilon Trading", "Zeta Corporation",
        "Theta Systems", "Kappa Industries", "Lambda Group"
    ]

    assignment_methods = ["bank_match", "reference_match", "name_match", "manual", "none"]
    error_reasons = [
        None, None, None, None, None,  # Most payments succeed
        "No open items found", "Multiple customers matched",
        "Remittance missing", "Amount mismatch", "SAP posting failed"
    ]

    # Generate data for last 90 days
    base_date = datetime.now()
    payment_id = 1

    for days_ago in range(90, -1, -1):
        payment_date = base_date - timedelta(days=days_ago)
        date_str = payment_date.strftime('%Y-%m-%d')

        # Generate 5-15 payments per day
        daily_payments = random.randint(5, 15)

        for _ in range(daily_payments):
            customer = random.choice(customers)
            amount = round(random.uniform(500, 50000), 2)

            # 75% automation success rate
            is_automated = random.random() < 0.75

            if is_automated:
                status = "auto_assigned"
                method = random.choice(["bank_match", "reference_match", "name_match"])
                processing_time = round(random.uniform(0.1, 2.0), 2)  # seconds to minutes
                error = None
                sap_posted = True
                remittance = True
            else:
                # Manual or unassigned
                if random.random() < 0.6:
                    status = "manual_assigned"
                    method = "manual"
                    processing_time = round(random.uniform(5, 45), 2)  # minutes
                    error = random.choice([r for r in error_reasons if r is not None])
                    sap_posted = True
                    remittance = random.random() < 0.7
                else:
                    status = "unassigned"
                    method = "none"
                    processing_time = None
                    error = random.choice([r for r in error_reasons if r is not None])
                    sap_posted = False
                    remittance = random.random() < 0.5

            payment = {
                "id": payment_id,
                "date": date_str,
                "customer_name": customer,
                "customer_id": f"C{1000 + customers.index(customer)}",
                "amount": amount,
                "status": status,
                "assignment_method": method,
                "processing_time": processing_time,
                "error_reason": error,
                "sap_posted": sap_posted,
                "remittance_received": remittance,
                "invoice_references": f"INV-{payment_id:05d}" if sap_posted else None
            }
            payments.append(payment)
            payment_id += 1

    return payments

# Generate sample data
transactions = generate_sample_payments()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/overview')
def get_overview():
    """
    Daily/Weekly Overview API
    Returns KPIs for selected time period (today, week, month, quarter)
    """
    period = request.args.get('period', 'today')  # today, week, month, quarter

    now = datetime.now()
    if period == 'today':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == 'week':
        start_date = now - timedelta(days=7)
    elif period == 'month':
        start_date = now - timedelta(days=30)
    elif period == 'quarter':
        start_date = now - timedelta(days=90)
    else:
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Filter payments for period
    filtered_payments = [
        p for p in transactions
        if datetime.strptime(p['date'], '%Y-%m-%d') >= start_date
    ]

    total_payments = len(filtered_payments)
    total_value = sum(p['amount'] for p in filtered_payments)
    auto_assigned = [p for p in filtered_payments if p['status'] == 'auto_assigned']
    manual_assigned = [p for p in filtered_payments if p['status'] == 'manual_assigned']
    unassigned = [p for p in filtered_payments if p['status'] == 'unassigned']

    auto_percentage = (len(auto_assigned) / total_payments * 100) if total_payments > 0 else 0

    # Average processing times
    auto_times = [p['processing_time'] for p in auto_assigned if p['processing_time']]
    manual_times = [p['processing_time'] for p in manual_assigned if p['processing_time']]

    avg_auto_time = sum(auto_times) / len(auto_times) if auto_times else 0
    avg_manual_time = sum(manual_times) / len(manual_times) if manual_times else 0

    # Trend data for chart (daily breakdown)
    trend_data = {}
    for p in filtered_payments:
        date = p['date']
        if date not in trend_data:
            trend_data[date] = {'total': 0, 'auto': 0}
        trend_data[date]['total'] += 1
        if p['status'] == 'auto_assigned':
            trend_data[date]['auto'] += 1

    # Calculate automation % per day
    trend_chart = []
    for date in sorted(trend_data.keys()):
        data = trend_data[date]
        auto_pct = (data['auto'] / data['total'] * 100) if data['total'] > 0 else 0
        trend_chart.append({
            'date': date,
            'automation_rate': round(auto_pct, 1),
            'total_payments': data['total']
        })

    return jsonify({
        'period': period,
        'total_payments': total_payments,
        'total_value': round(total_value, 2),
        'automation_percentage': round(auto_percentage, 1),
        'auto_assigned_count': len(auto_assigned),
        'manual_assigned_count': len(manual_assigned),
        'unassigned_count': len(unassigned),
        'total_value_assigned': round(sum(p['amount'] for p in auto_assigned + manual_assigned), 2),
        'avg_auto_time_minutes': round(avg_auto_time, 2),
        'avg_manual_time_minutes': round(avg_manual_time, 2),
        'trend_chart': trend_chart
    })

@app.route('/api/automation-efficiency')
def get_automation_efficiency():
    """
    Automation Efficiency & Impact API
    Returns automation success rates, time/cost savings, and rule breakdown
    """
    period = request.args.get('period', 'month')
    now = datetime.now()

    if period == 'week':
        start_date = now - timedelta(days=7)
    elif period == 'month':
        start_date = now - timedelta(days=30)
    elif period == 'quarter':
        start_date = now - timedelta(days=90)
    else:
        start_date = now - timedelta(days=30)

    filtered_payments = [
        p for p in transactions
        if datetime.strptime(p['date'], '%Y-%m-%d') >= start_date
    ]

    # Rule breakdown
    rule_breakdown = defaultdict(int)
    for p in filtered_payments:
        if p['assignment_method'] != 'none':
            rule_breakdown[p['assignment_method']] += 1

    # Success metrics
    total = len(filtered_payments)
    auto_assigned = len([p for p in filtered_payments if p['status'] == 'auto_assigned'])
    manual_interventions_saved = auto_assigned

    # Time saved calculation (assume manual takes 20 min avg, auto takes 1 min avg)
    auto_times = [p['processing_time'] for p in filtered_payments if p['status'] == 'auto_assigned' and p['processing_time']]
    actual_auto_time = sum(auto_times) if auto_times else 0
    would_be_manual_time = auto_assigned * 20  # 20 minutes per payment if done manually
    time_saved_minutes = would_be_manual_time - actual_auto_time

    # Cost saved (assume $30/hour labor cost)
    cost_saved = (time_saved_minutes / 60) * 30

    # Automation success rate
    automation_rate = (auto_assigned / total * 100) if total > 0 else 0

    return jsonify({
        'automation_success_rate': round(automation_rate, 1),
        'manual_interventions_saved': manual_interventions_saved,
        'time_saved_minutes': round(time_saved_minutes, 1),
        'time_saved_hours': round(time_saved_minutes / 60, 1),
        'cost_saved_euros': round(cost_saved, 2),
        'rule_breakdown': dict(rule_breakdown),
        'total_payments': total,
        'period': period
    })

@app.route('/api/exceptions')
def get_exceptions():
    """
    Exceptions / Attention Points API
    Returns recurring issues, high-value unassigned payments, and error analysis
    """
    # Top 5 customers with recurring payment exceptions
    customer_errors = defaultdict(lambda: {'count': 0, 'total_value': 0, 'errors': []})

    for p in transactions:
        if p['status'] in ['unassigned', 'manual_assigned'] and p['error_reason']:
            customer = p['customer_name']
            customer_errors[customer]['count'] += 1
            customer_errors[customer]['total_value'] += p['amount']
            if p['error_reason'] not in customer_errors[customer]['errors']:
                customer_errors[customer]['errors'].append(p['error_reason'])

    # Sort by count and get top 5
    top_customers = sorted(
        [{'customer': k, **v} for k, v in customer_errors.items()],
        key=lambda x: x['count'],
        reverse=True
    )[:5]

    # High-value unassigned payments (> $10,000)
    high_value_unassigned = [
        {
            'id': p['id'],
            'customer': p['customer_name'],
            'amount': p['amount'],
            'date': p['date'],
            'error_reason': p['error_reason']
        }
        for p in transactions
        if p['status'] == 'unassigned' and p['amount'] > 10000
    ]
    high_value_unassigned.sort(key=lambda x: x['amount'], reverse=True)

    # SAP posting delays (payments assigned but not posted)
    sap_delays = [
        {
            'id': p['id'],
            'customer': p['customer_name'],
            'amount': p['amount'],
            'date': p['date'],
            'status': p['status']
        }
        for p in transactions
        if p['status'] in ['auto_assigned', 'manual_assigned'] and not p['sap_posted']
    ]

    # Error reason breakdown
    error_breakdown = defaultdict(int)
    for p in transactions:
        if p['error_reason']:
            error_breakdown[p['error_reason']] += 1

    return jsonify({
        'top_problem_customers': top_customers,
        'high_value_unassigned': high_value_unassigned[:10],
        'sap_posting_delays': sap_delays[:10],
        'error_breakdown': dict(error_breakdown),
        'total_exceptions': len([p for p in transactions if p['status'] == 'unassigned'])
    })

@app.route('/api/month-end-summary')
def get_month_end_summary():
    """
    Month-End Summary (CFO Snapshot) API
    Returns monthly metrics with comparisons to previous month
    """
    now = datetime.now()

    # Current month
    current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    current_month_payments = [
        p for p in transactions
        if datetime.strptime(p['date'], '%Y-%m-%d') >= current_month_start
    ]

    # Previous month
    if now.month == 1:
        prev_month_start = now.replace(year=now.year-1, month=12, day=1)
    else:
        prev_month_start = now.replace(month=now.month-1, day=1)
    prev_month_end = current_month_start - timedelta(days=1)

    prev_month_payments = [
        p for p in transactions
        if prev_month_start <= datetime.strptime(p['date'], '%Y-%m-%d') <= prev_month_end
    ]

    def calc_metrics(payments):
        total_count = len(payments)
        total_value = sum(p['amount'] for p in payments)
        auto_count = len([p for p in payments if p['status'] == 'auto_assigned'])
        auto_rate = (auto_count / total_count * 100) if total_count > 0 else 0

        # Average assignment delay
        delays = [p['processing_time'] for p in payments if p['processing_time']]
        avg_delay = sum(delays) / len(delays) if delays else 0

        # Time saved
        auto_times = [p['processing_time'] for p in payments if p['status'] == 'auto_assigned' and p['processing_time']]
        actual_time = sum(auto_times) if auto_times else 0
        would_be_time = auto_count * 20
        time_saved = would_be_time - actual_time

        return {
            'count': total_count,
            'value': total_value,
            'automation_rate': auto_rate,
            'avg_delay': avg_delay,
            'time_saved_hours': time_saved / 60
        }

    current = calc_metrics(current_month_payments)
    previous = calc_metrics(prev_month_payments)

    # Calculate changes
    automation_change = current['automation_rate'] - previous['automation_rate']
    count_change = ((current['count'] - previous['count']) / previous['count'] * 100) if previous['count'] > 0 else 0

    # Top performing rules
    rule_performance = defaultdict(lambda: {'total': 0, 'success': 0})
    for p in current_month_payments:
        if p['assignment_method'] != 'none':
            rule_performance[p['assignment_method']]['total'] += 1
            if p['status'] == 'auto_assigned':
                rule_performance[p['assignment_method']]['success'] += 1

    top_rules = [
        {
            'rule': rule,
            'success_rate': (data['success'] / data['total'] * 100) if data['total'] > 0 else 0,
            'count': data['total']
        }
        for rule, data in rule_performance.items()
    ]
    top_rules.sort(key=lambda x: x['success_rate'], reverse=True)

    return jsonify({
        'current_month': {
            'total_payments_count': current['count'],
            'total_payments_value': round(current['value'], 2),
            'automation_rate': round(current['automation_rate'], 1),
            'avg_assignment_delay_minutes': round(current['avg_delay'], 2),
            'total_time_saved_hours': round(current['time_saved_hours'], 1)
        },
        'previous_month': {
            'total_payments_count': previous['count'],
            'total_payments_value': round(previous['value'], 2),
            'automation_rate': round(previous['automation_rate'], 1)
        },
        'changes': {
            'automation_rate_change': round(automation_change, 1),
            'payment_count_change_pct': round(count_change, 1)
        },
        'top_performing_rules': top_rules
    })

@app.route('/api/transactions')
def get_transactions():
    """Get all transactions (for backwards compatibility)"""
    return jsonify(transactions[:100])  # Limit to 100 for performance

@app.route('/api/transactions', methods=['POST'])
def add_transaction():
    """Add a new payment"""
    data = request.get_json()
    new_payment = {
        'id': len(transactions) + 1,
        'date': data.get('date', datetime.now().strftime('%Y-%m-%d')),
        'customer_name': data.get('customer_name', 'Unknown'),
        'customer_id': data.get('customer_id', 'C0000'),
        'amount': float(data.get('amount', 0)),
        'status': data.get('status', 'unassigned'),
        'assignment_method': data.get('assignment_method', 'none'),
        'processing_time': data.get('processing_time'),
        'error_reason': data.get('error_reason'),
        'sap_posted': data.get('sap_posted', False),
        'remittance_received': data.get('remittance_received', False),
        'invoice_references': data.get('invoice_references')
    }
    transactions.append(new_payment)
    return jsonify(new_payment), 201

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

