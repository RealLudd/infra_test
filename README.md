# 💰 CashWeb - Payment Automation Analytics Dashboard

A comprehensive analytics platform for tracking payment automation, cash flow intelligence, and operational efficiency built with Flask, Chart.js, and modern web technologies.

## ✨ Features

### 🏠 Daily / Weekly Overview
- **At-a-glance KPIs** - Total payments, automation rates, workload metrics
- **Time Period Toggle** - View metrics for Today, Week, Month, or Quarter
- **Automation Trend Chart** - Visualize automation percentage over time
- **Processing Time Metrics** - Compare automated vs manual processing times
- **Value Tracking** - Monitor total payment values and assignment success

### 📊 Automation Efficiency & Impact
- **Success Rate Tracking** - Monitor automation performance and trends
- **Cost & Time Savings** - Quantify labor savings and efficiency gains
- **Rule Breakdown** - Pie chart showing distribution across match types (bank, reference, name)
- **Impact Visualization** - Bar charts demonstrating cost and time saved
- **Manual Interventions Saved** - Track how many payments were auto-processed

### 🚨 Exceptions & Attention Points
- **Recurring Problem Customers** - Top 5 customers with payment exceptions
- **High-Value Unassigned Payments** - Monitor payments >$10,000 needing attention
- **SAP Posting Delays** - Track integration issues and delays
- **Error Breakdown Chart** - Visualize common failure reasons
- **Exception Tracking** - Detailed tables with customer, value, and error information

### 📆 Month-End Summary (CFO Snapshot)
- **Monthly Metrics** - Total payments, values, and automation rates
- **Month-over-Month Comparisons** - Track improvements with percentage changes
- **Top Performing Rules** - Bar chart showing success rates by rule type
- **Time Saved Tracking** - Cumulative efficiency gains in hours
- **Automated Reports** - Ready-to-present executive metrics

### 🧩 Future Enhancements Roadmap
- 📈 Predictive forecasting for expected payments
- 🔍 Correlation analysis between remittance timing and automation success
- 💬 Feedback loops for cash operations teams
- 🤖 Machine learning integration for smart matching
- 📧 Automated alerts for exceptions and high-value issues

### 🎨 Additional Features
- 📱 **Responsive Design** - Works perfectly on desktop, tablet, and mobile
- 🚀 **RESTful API** - Comprehensive API endpoints for all analytics
- ⚡ **Auto-refresh** - Dashboard updates every 60 seconds
- 📊 **Interactive Charts** - Built with Chart.js for rich visualizations
- 🎨 **Modern UI** - Beautiful gradient design with smooth animations

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/RealLudd/infra_test.git
   cd infra_test
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Open in your browser:**
   ```
   http://localhost:5000
   ```

That's it! 🎉

## 🖥️ Running on Your Server

### Option A: Development Server (Quick Testing)

```bash
python app.py
```

The app will run on `http://0.0.0.0:5000`

### Option B: Production Server (Recommended)

For production deployment, use a WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Option C: Windows Service

To run as a Windows service, you can use NSSM (Non-Sucking Service Manager):

1. Download NSSM from https://nssm.cc/download
2. Install the service:
   ```cmd
   nssm install CashWeb "C:\Python39\python.exe" "C:\path\to\app.py"
   nssm start CashWeb
   ```

## 📡 API Endpoints

### GET `/`
Main analytics dashboard page with all visualizations

### GET `/api/overview?period={today|week|month|quarter}`
Get overview metrics for selected time period
```json
{
  "period": "week",
  "total_payments": 72,
  "total_value": 1941731.31,
  "automation_percentage": 77.8,
  "auto_assigned_count": 56,
  "manual_assigned_count": 10,
  "unassigned_count": 6,
  "total_value_assigned": 1737233.51,
  "avg_auto_time_minutes": 1.04,
  "avg_manual_time_minutes": 22.91,
  "trend_chart": [...]
}
```

### GET `/api/automation-efficiency?period={week|month|quarter}`
Get automation efficiency metrics and impact analysis
```json
{
  "automation_success_rate": 73.9,
  "manual_interventions_saved": 221,
  "time_saved_minutes": 4204.0,
  "time_saved_hours": 70.1,
  "cost_saved_euros": 2102.0,
  "rule_breakdown": {
    "bank_match": 76,
    "reference_match": 77,
    "name_match": 68,
    "manual": 48
  },
  "total_payments": 299,
  "period": "month"
}
```

### GET `/api/exceptions`
Get exception analysis and attention points
```json
{
  "top_problem_customers": [
    {
      "customer": "Acme Corp",
      "count": 12,
      "total_value": 145000.50,
      "errors": ["No open items found", "Amount mismatch"]
    }
  ],
  "high_value_unassigned": [...],
  "sap_posting_delays": [...],
  "error_breakdown": {
    "No open items found": 45,
    "Multiple customers matched": 23,
    ...
  },
  "total_exceptions": 89
}
```

### GET `/api/month-end-summary`
Get month-end CFO snapshot with comparisons
```json
{
  "current_month": {
    "total_payments_count": 152,
    "total_payments_value": 3850420.75,
    "automation_rate": 75.5,
    "avg_assignment_delay_minutes": 8.2,
    "total_time_saved_hours": 125.3
  },
  "previous_month": {
    "total_payments_count": 145,
    "total_payments_value": 3420100.25,
    "automation_rate": 72.1
  },
  "changes": {
    "automation_rate_change": 3.4,
    "payment_count_change_pct": 4.8
  },
  "top_performing_rules": [...]
}
```

### GET `/api/transactions`
Get all payment transactions (limited to 100 for performance)
```json
[
  {
    "id": 1,
    "date": "2025-11-01",
    "customer_name": "Acme Corp",
    "customer_id": "C1000",
    "amount": 15000.00,
    "status": "auto_assigned",
    "assignment_method": "bank_match",
    "processing_time": 1.2,
    "error_reason": null,
    "sap_posted": true,
    "remittance_received": true,
    "invoice_references": "INV-00001"
  },
  ...
]
```

### POST `/api/transactions`
Add a new payment
```json
{
  "date": "2025-11-06",
  "customer_name": "Test Customer Inc",
  "customer_id": "C9999",
  "amount": 5000,
  "status": "auto_assigned",
  "assignment_method": "bank_match",
  "processing_time": 1.5,
  "sap_posted": true,
  "remittance_received": true
}
```

### GET `/health`
Health check endpoint
```json
{
  "status": "healthy",
  "timestamp": "2025-11-05T10:30:00",
  "service": "CashWeb"
}
```

## 🧪 Running Tests

Run the test suite with pytest:

```bash
pytest -v
```

With coverage report:

```bash
pytest -v --cov=. --cov-report=term-missing
```

## 🔧 Tech Stack

- **Backend:** Flask (Python) - RESTful API server
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Visualization:** Chart.js 4.4.0 - Interactive charts and graphs
- **Data Processing:** Python datetime, collections (defaultdict)
- **Testing:** pytest with comprehensive test coverage
- **CI/CD:** GitHub Actions - Automated testing on Python 3.9, 3.10, 3.11

## 📦 Project Structure

```
infra_test/
├── app.py                    # Flask application
├── test_app.py              # Unit tests
├── requirements.txt         # Python dependencies
├── templates/
│   └── index.html           # Dashboard UI
├── .github/
│   └── workflows/
│       └── ci.yml          # CI/CD pipeline
├── .gitignore              # Git ignore file
└── README.md               # This file
```

## 🌐 Deployment

### Local Network Access

To allow others on your network to access the dashboard:

1. Run the app: `python app.py`
2. Find your IP address:
   - Windows: `ipconfig`
   - Linux/Mac: `ifconfig` or `ip addr`
3. Share: `http://YOUR_IP:5000`

### Port Configuration

To change the port, edit `app.py`:

```python
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)  # Change port here
```

## 🔐 Security Notes

This is a development version. For production:

- Add authentication and authorization
- Use HTTPS (SSL/TLS)
- Implement rate limiting
- Use a proper database (PostgreSQL, MySQL, etc.)
- Add input validation and sanitization
- Set `debug=False` in production

## 🎯 Implemented Features ✅

- ✅ **Charts and graphs** - Comprehensive Chart.js integration with 6+ chart types
- ✅ **Payment automation tracking** - Full lifecycle from ingestion to SAP posting
- ✅ **Analytics dashboards** - Overview, Efficiency, Exceptions, Month-End Summary
- ✅ **Time period filtering** - Today, Week, Month, Quarter views
- ✅ **Exception monitoring** - High-value alerts, recurring issues, error tracking
- ✅ **Cost/Time savings analysis** - ROI metrics for automation initiatives
- ✅ **Comparative metrics** - Month-over-month performance tracking

## 🎯 Roadmap for Future Enhancements

- [ ] **Database integration** - PostgreSQL/MySQL for persistent storage
- [ ] **User authentication** - Role-based access control (Cash Ops, CFO, Admin)
- [ ] **Export functionality** - CSV/Excel/PDF reports for all dashboards
- [ ] **Predictive analytics** - ML-based payment forecasting
- [ ] **Correlation analysis** - Remittance timing vs automation success
- [ ] **Automated alerts** - Email/Slack notifications for exceptions
- [ ] **Feedback system** - Cash ops team input for rule improvement
- [ ] **Customer master data** - Enhanced customer profiles and history
- [ ] **Dark mode toggle** - User preference themes
- [ ] **Real-time SAP integration** - Live posting status updates
- [ ] **Drill-down capabilities** - Click-through from charts to transaction details

## 🐛 Troubleshooting

**Port already in use?**
```bash
# Find and kill the process using the port
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:5000 | xargs kill -9
```

**Flask not installed?**
```bash
pip install Flask
```

**Import errors?**
```bash
pip install -r requirements.txt --force-reinstall
```

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## 📞 Support

For support, please open an issue on GitHub.

---

**Built with ❤️ for modern cash management**
