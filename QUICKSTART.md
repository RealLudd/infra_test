# 🚀 CashWeb Quick Start Guide

## ✅ Your Web Application is Ready!

**Project Location:** `C:\Users\SA_DE_RPA\CashWeb\infra_test`

**Server Status:** ✅ **RUNNING** on http://localhost:5000

---

## 📂 Project Files (Cleaned Up)

```
infra_test/
├── app.py                    # Flask web application
├── test_app.py              # Unit tests (all passing ✅)
├── requirements.txt         # Python dependencies
├── templates/
│   └── index.html           # Dashboard UI
├── .github/
│   └── workflows/
│       └── ci.yml          # GitHub Actions CI/CD
├── .gitignore              # Git ignore rules
├── README.md               # Full documentation
└── QUICKSTART.md           # This file
```

**✨ All non-web-related test files have been removed!**

---

## 🌐 Access Your Dashboard

### On This Computer:
```
http://localhost:5000
```

### From Other Computers on Your Network:
1. Find your IP address: `ipconfig` (look for IPv4)
2. Share: `http://YOUR_IP:5000`

---

## 🎯 What You Have Now

### Dashboard Features:
- 💰 **Total Income:** $10,000
- 💳 **Total Expenses:** $380
- 📊 **Net Cash Flow:** $9,620
- 📝 **5 Sample Transactions**
- 🔄 **Auto-refresh every 30 seconds**

### API Endpoints:
- `GET /` - Main dashboard
- `GET /api/summary` - Cash flow summary
- `GET /api/transactions` - All transactions
- `POST /api/transactions` - Add new transaction
- `GET /health` - Health check

---

## 🛠️ Common Commands

### Start the Server:
```bash
cd C:\Users\SA_DE_RPA\CashWeb\infra_test
python app.py
```

### Run Tests:
```bash
python -m pytest -v
```

### Install Dependencies:
```bash
python -m pip install -r requirements.txt
```

### Stop the Server:
Press `Ctrl + C` in the terminal

---

## 🚀 Running as a Service

### Option 1: PowerShell Background
```powershell
Start-Process python -ArgumentList "app.py" -WorkingDirectory "C:\Users\SA_DE_RPA\CashWeb\infra_test" -WindowStyle Hidden
```

### Option 2: NSSM (Windows Service)
1. Download NSSM: https://nssm.cc/download
2. Install service:
   ```cmd
   nssm install CashWeb "C:\Program Files (x86)\Microsoft Visual Studio\Shared\Python39_64\python.exe" "C:\Users\SA_DE_RPA\CashWeb\infra_test\app.py"
   nssm start CashWeb
   ```

### Option 3: Task Scheduler
1. Open Task Scheduler (`taskschd.msc`)
2. Create Basic Task
3. Set to run: `python.exe`
4. Arguments: `"C:\Users\SA_DE_RPA\CashWeb\infra_test\app.py"`
5. Set to run at startup

---

## 📱 Test the API

### Get Summary:
```powershell
Invoke-RestMethod -Uri http://localhost:5000/api/summary
```

### Get Transactions:
```powershell
Invoke-RestMethod -Uri http://localhost:5000/api/transactions
```

### Add Transaction:
```powershell
$body = @{
    date = "2025-11-06"
    description = "New Sale"
    amount = 2000
    type = "income"
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:5000/api/transactions -Method Post -Body $body -ContentType "application/json"
```

---

## 🎨 Customize Your Dashboard

Edit `app.py` to:
- Add more transactions
- Change port number
- Connect to a database
- Add authentication

Edit `templates/index.html` to:
- Change colors and styling
- Add charts and graphs
- Modify the layout

---

## 📊 Next Steps

1. **Open the Dashboard:** http://localhost:5000
2. **Explore the API:** Check out the endpoints
3. **Customize:** Modify the code to fit your needs
4. **Deploy:** Set up as a Windows service for production
5. **Database:** Add SQLite or PostgreSQL for persistent storage

---

## 🔧 Troubleshooting

### Server Not Starting?
```bash
# Check if port 5000 is already in use
netstat -ano | findstr :5000

# Kill the process if needed
taskkill /PID <PID> /F
```

### Import Errors?
```bash
python -m pip install -r requirements.txt --force-reinstall
```

### Can't Access from Network?
- Check Windows Firewall settings
- Make sure the app is running on `0.0.0.0` not `127.0.0.1`

---

## ✅ System Status

- ✅ Repository cloned from GitHub
- ✅ Test files removed
- ✅ Web application created
- ✅ Dependencies installed
- ✅ All tests passing (5/5)
- ✅ Server running on http://localhost:5000
- ✅ API endpoints working
- ✅ Dashboard accessible

---

**Your CashWeb application is ready to use! 🎉**

For full documentation, see [README.md](README.md)

