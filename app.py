"""
CashWeb - Cash Management Web Application
A simple Flask application for tracking cash flow and expenses
"""
from flask import Flask, render_template, jsonify, request
from datetime import datetime
import json

app = Flask(__name__)

# Sample data (in production, this would come from a database)
transactions = [
    {"id": 1, "date": "2025-11-01", "description": "Sales Revenue", "amount": 5000, "type": "income"},
    {"id": 2, "date": "2025-11-02", "description": "Office Supplies", "amount": -150, "type": "expense"},
    {"id": 3, "date": "2025-11-03", "description": "Client Payment", "amount": 3200, "type": "income"},
    {"id": 4, "date": "2025-11-04", "description": "Utilities", "amount": -230, "type": "expense"},
    {"id": 5, "date": "2025-11-05", "description": "Service Revenue", "amount": 1800, "type": "income"},
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

