from flask import Flask, render_template, jsonify
import random
from datetime import datetime, timedelta

app = Flask(__name__)

def add(a, b):
    """Original add function for backwards compatibility"""
    return a + b

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/sales-data')
def get_sales_data():
    """API endpoint for sales chart data"""
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    sales = [random.randint(15000, 45000) for _ in range(6)]
    expenses = [random.randint(10000, 30000) for _ in range(6)]
    
    return jsonify({
        'labels': months,
        'sales': sales,
        'expenses': expenses
    })

@app.route('/api/user-stats')
def get_user_stats():
    """API endpoint for user statistics"""
    return jsonify({
        'total_users': random.randint(1000, 5000),
        'active_users': random.randint(500, 2000),
        'new_users': random.randint(50, 200),
        'premium_users': random.randint(100, 800)
    })

@app.route('/api/performance-data')
def get_performance_data():
    """API endpoint for performance metrics"""
    hours = ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00']
    cpu = [random.randint(20, 80) for _ in range(7)]
    memory = [random.randint(30, 70) for _ in range(7)]
    
    return jsonify({
        'labels': hours,
        'cpu': cpu,
        'memory': memory
    })

@app.route('/api/category-distribution')
def get_category_distribution():
    """API endpoint for category distribution pie chart"""
    return jsonify({
        'labels': ['Technology', 'Marketing', 'Sales', 'Operations', 'HR'],
        'data': [
            random.randint(15, 35),
            random.randint(15, 35),
            random.randint(15, 35),
            random.randint(10, 25),
            random.randint(5, 15)
        ]
    })

if __name__ == "__main__":
    print("\n" + "="*60)
    print("Dashboard Server Starting!")
    print("="*60)
    print("Open your browser and go to:")
    print("   => http://localhost:5000")
    print("\nTo share with colleagues on your network:")
    print("   => http://YOUR_IP_ADDRESS:5000")
    print("\nPress CTRL+C to stop the server")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
