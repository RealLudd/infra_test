# 💰 CashWeb - Cash Management Dashboard

A modern, responsive web application for tracking cash flow and managing expenses built with Flask and vanilla JavaScript.

## ✨ Features

- 📊 **Real-time Dashboard** - View income, expenses, and net cash flow at a glance
- 💳 **Transaction Management** - Track all your cash transactions in one place
- 📱 **Responsive Design** - Works perfectly on desktop, tablet, and mobile
- 🚀 **RESTful API** - Clean API endpoints for integration
- ⚡ **Auto-refresh** - Dashboard updates every 30 seconds
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
Main dashboard page

### GET `/api/summary`
Get cash flow summary
```json
{
  "total_income": 10000,
  "total_expenses": 380,
  "net_cash": 9620,
  "transaction_count": 5
}
```

### GET `/api/transactions`
Get all transactions
```json
[
  {
    "id": 1,
    "date": "2025-11-01",
    "description": "Sales Revenue",
    "amount": 5000,
    "type": "income"
  },
  ...
]
```

### POST `/api/transactions`
Add a new transaction
```json
{
  "date": "2025-11-06",
  "description": "New Sale",
  "amount": 1500,
  "type": "income"
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

- **Backend:** Flask (Python)
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Testing:** pytest
- **CI/CD:** GitHub Actions

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

## 🎯 Future Enhancements

- [ ] Database integration (SQLite/PostgreSQL)
- [ ] User authentication and multi-user support
- [ ] Export transactions to CSV/Excel
- [ ] Charts and graphs (Chart.js integration)
- [ ] Budget planning and forecasting
- [ ] Receipt upload and storage
- [ ] Recurring transaction support
- [ ] Category tagging and filtering
- [ ] Dark mode toggle

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
