from flask import Flask, render_template, jsonify, request
from datetime import datetime, timedelta
import random
from collections import defaultdict

app = Flask(__name__)

# Mock data generators for cash operations metrics

def get_date_range(period='today'):
    """Get date range based on period selection"""
    now = datetime.now()
    if period == 'today':
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif period == 'week':
        start = now - timedelta(days=now.weekday())
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif period == 'month':
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif period == 'quarter':
        quarter = (now.month - 1) // 3
        start = now.replace(month=quarter * 3 + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end = now
    else:
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now

    return start, end

def generate_overview_data(period='today'):
    """Generate daily/weekly overview metrics"""
    multipliers = {
        'today': 1,
        'week': 7,
        'month': 30,
        'quarter': 90
    }
    mult = multipliers.get(period, 1)

    total_payments = random.randint(50, 150) * mult
    auto_processed = int(total_payments * random.uniform(0.75, 0.92))
    manual_workload = total_payments - auto_processed

    return {
        'total_payments': total_payments,
        'total_value': round(random.uniform(500000, 2000000) * mult, 2),
        'auto_processed_pct': round((auto_processed / total_payments) * 100, 1),
        'auto_processed_count': auto_processed,
        'manual_workload': manual_workload,
        'total_value_assigned': round(random.uniform(450000, 1900000) * mult, 2),
        'avg_time_auto': round(random.uniform(2, 8), 1),
        'avg_time_manual': round(random.uniform(45, 180), 1)
    }

def generate_automation_trend(period='week'):
    """Generate automation trend data for charts"""
    days = {'today': 1, 'week': 7, 'month': 30, 'quarter': 90}.get(period, 7)
    labels = []
    data = []

    base_rate = 75
    now = datetime.now()

    for i in range(days):
        date = now - timedelta(days=days - i - 1)
        if period == 'today':
            labels.append(date.strftime('%H:00'))
        elif period == 'week':
            labels.append(date.strftime('%a'))
        elif period == 'month':
            labels.append(date.strftime('%b %d'))
        else:
            labels.append(date.strftime('%m/%d'))

        # Gradual improvement trend with some variance
        trend_improvement = (i / days) * 10
        variance = random.uniform(-3, 3)
        rate = min(95, base_rate + trend_improvement + variance)
        data.append(round(rate, 1))

    return {'labels': labels, 'data': data}

def generate_automation_efficiency():
    """Generate automation efficiency metrics"""
    total_payments = random.randint(1000, 2000)
    auto_assigned = int(total_payments * random.uniform(0.80, 0.92))

    # Match type breakdown
    bank_match = int(auto_assigned * 0.45)
    reference_match = int(auto_assigned * 0.35)
    name_match = int(auto_assigned * 0.15)
    other_match = auto_assigned - bank_match - reference_match - name_match

    # Reprocessing stats
    initial_failures = random.randint(50, 150)
    later_fixed = int(initial_failures * random.uniform(0.60, 0.85))

    avg_time_saved_per_payment = 3.2  # minutes
    time_saved_total = round((auto_assigned * avg_time_saved_per_payment) / 60, 1)  # hours
    cost_per_hour = 35  # euros
    cost_saved = round(time_saved_total * cost_per_hour, 2)

    return {
        'auto_success_rate': round((auto_assigned / total_payments) * 100, 1),
        'manual_interventions_saved': auto_assigned,
        'time_saved_hours': time_saved_total,
        'cost_saved': cost_saved,
        'match_breakdown': {
            'bank_account': bank_match,
            'reference': reference_match,
            'name': name_match,
            'other': other_match
        },
        'reprocessing': {
            'initial_failures': initial_failures,
            'later_fixed': later_fixed,
            'fix_rate': round((later_fixed / initial_failures) * 100, 1)
        }
    }

def generate_exceptions_data():
    """Generate exceptions and attention points data"""
    customers = [
        'Acme Corporation', 'Global Industries Ltd', 'TechVision GmbH',
        'Metro Services AG', 'Summit Trading Co', 'Pacific Imports',
        'Northern Solutions', 'Eastern Manufacturing'
    ]

    # Top 5 customers with recurring exceptions
    top_exceptions = []
    for i in range(5):
        customer = random.choice(customers)
        top_exceptions.append({
            'customer': customer,
            'count': random.randint(5, 25),
            'last_occurrence': (datetime.now() - timedelta(days=random.randint(0, 7))).strftime('%Y-%m-%d')
        })

    # High-value unassigned
    high_value_unassigned = []
    for i in range(3):
        high_value_unassigned.append({
            'customer': random.choice(customers),
            'amount': round(random.uniform(50000, 200000), 2),
            'days_pending': random.randint(1, 10)
        })

    # Delays
    delays = {
        'sap_posting_delayed': random.randint(0, 15),
        'remittance_ingestion_delayed': random.randint(0, 8)
    }

    # Error reasons breakdown
    error_reasons = {
        'no_open_items': random.randint(10, 40),
        'multiple_customers': random.randint(5, 25),
        'remittance_mismatch': random.randint(8, 30),
        'missing_reference': random.randint(12, 35),
        'other': random.randint(3, 15)
    }

    return {
        'top_exceptions': top_exceptions,
        'high_value_unassigned': high_value_unassigned,
        'delays': delays,
        'error_reasons': error_reasons
    }

def generate_remittance_insights():
    """Generate remittance processing insights"""
    total_remittances = random.randint(150, 400)
    successfully_parsed = int(total_remittances * random.uniform(0.85, 0.95))
    manual_review = total_remittances - successfully_parsed

    customers = [
        'Acme Corporation', 'Global Industries Ltd', 'TechVision GmbH',
        'Metro Services AG', 'Summit Trading Co'
    ]

    top_customers = []
    for customer in customers:
        top_customers.append({
            'customer': customer,
            'volume': random.randint(15, 80)
        })

    top_customers.sort(key=lambda x: x['volume'], reverse=True)

    return {
        'total_remittances': total_remittances,
        'successfully_parsed': successfully_parsed,
        'successfully_parsed_pct': round((successfully_parsed / total_remittances) * 100, 1),
        'manual_review': manual_review,
        'manual_review_pct': round((manual_review / total_remittances) * 100, 1),
        'avg_processing_time': round(random.uniform(5, 25), 1),
        'top_customers': top_customers[:5]
    }

def generate_month_end_summary():
    """Generate month-end CFO snapshot"""
    current_month_payments = random.randint(2000, 4000)
    previous_month_payments = random.randint(1800, 3800)

    current_value = round(random.uniform(5000000, 12000000), 2)
    previous_value = round(random.uniform(4500000, 11000000), 2)

    current_auto_rate = round(random.uniform(82, 92), 1)
    previous_auto_rate = round(random.uniform(75, 88), 1)

    avg_delay_current = round(random.uniform(15, 35), 1)
    avg_delay_previous = round(random.uniform(20, 45), 1)

    # Time saved calculation
    auto_processed = int(current_month_payments * (current_auto_rate / 100))
    time_saved_hours = round((auto_processed * 3.2) / 60, 1)
    fte_saved = round(time_saved_hours / 160, 2)  # 160 hours per month
    euro_saved = round(time_saved_hours * 35, 2)

    # Top performing rules
    rules = [
        {'name': 'Bank Account Match', 'success_rate': round(random.uniform(92, 98), 1)},
        {'name': 'Reference Number Match', 'success_rate': round(random.uniform(85, 94), 1)},
        {'name': 'Customer Name Match', 'success_rate': round(random.uniform(78, 88), 1)},
        {'name': 'Amount + Date Match', 'success_rate': round(random.uniform(75, 85), 1)}
    ]

    rules.sort(key=lambda x: x['success_rate'], reverse=True)

    return {
        'current_month': {
            'payments_count': current_month_payments,
            'payments_value': current_value,
            'auto_rate': current_auto_rate,
            'avg_delay': avg_delay_current
        },
        'previous_month': {
            'payments_count': previous_month_payments,
            'payments_value': previous_value,
            'auto_rate': previous_auto_rate,
            'avg_delay': avg_delay_previous
        },
        'improvements': {
            'auto_rate_change': round(current_auto_rate - previous_auto_rate, 1),
            'delay_improvement': round(avg_delay_previous - avg_delay_current, 1),
            'volume_change_pct': round(((current_month_payments - previous_month_payments) / previous_month_payments) * 100, 1)
        },
        'time_saved': {
            'hours': time_saved_hours,
            'fte': fte_saved,
            'euro_value': euro_saved
        },
        'top_rules': rules[:3]
    }


# API Routes

@app.route('/')
def index():
    """Render the main dashboard"""
    return render_template('dashboard.html')

@app.route('/api/overview')
def api_overview():
    """Get overview metrics for selected period"""
    period = request.args.get('period', 'today')
    data = generate_overview_data(period)
    return jsonify(data)

@app.route('/api/automation-trend')
def api_automation_trend():
    """Get automation trend data"""
    period = request.args.get('period', 'week')
    data = generate_automation_trend(period)
    return jsonify(data)

@app.route('/api/automation-efficiency')
def api_automation_efficiency():
    """Get automation efficiency metrics"""
    data = generate_automation_efficiency()
    return jsonify(data)

@app.route('/api/exceptions')
def api_exceptions():
    """Get exceptions and attention points"""
    data = generate_exceptions_data()
    return jsonify(data)

@app.route('/api/remittance-insights')
def api_remittance_insights():
    """Get remittance processing insights"""
    data = generate_remittance_insights()
    return jsonify(data)

@app.route('/api/month-end-summary')
def api_month_end_summary():
    """Get month-end summary for CFO"""
    data = generate_month_end_summary()
    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
