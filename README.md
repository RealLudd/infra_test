# 🚀 Analytics Dashboard - Infrastructure Test Project

A beautiful, interactive analytics dashboard built with Flask and Chart.js to demonstrate the **Cursor ↔ GitHub ↔ Claude Mobile** workflow.

## ✨ Features

- 📊 **Interactive Charts** - Real-time data visualization with Chart.js
- 💎 **Modern UI** - Sleek, responsive design with smooth animations
- 📱 **Mobile-Friendly** - Works perfectly on all devices
- ⚡ **Live Updates** - Stats refresh automatically every 5 seconds
- 🎨 **Beautiful Gradients** - Eye-catching visual design

## 🖼️ What You'll See

- **4 Stat Cards**: Total Users, Active Users, New Users, Premium Users
- **Sales vs Expenses Chart**: Interactive bar chart
- **System Performance**: Real-time CPU and Memory monitoring
- **Category Distribution**: Beautiful doughnut chart

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Dashboard

```bash
python app.py
```

### 3. Open in Browser

Go to: **http://localhost:5000**

That's it! 🎉

## 🌐 Demo to Colleagues

### Option A: Local Demo (Screen Share)
1. Run `python app.py`
2. Open http://localhost:5000
3. Share your screen on Teams/Zoom
4. Show off the beautiful dashboard! ✨

### Option B: Network Demo (Same Office)
1. Run `python app.py`
2. Find your IP address:
   - Windows: `ipconfig` (look for IPv4)
   - Mac/Linux: `ifconfig` or `ip addr`
3. Share with colleagues: `http://YOUR_IP:5000`
4. They can access it from their browsers!

## 🎯 Testing the Workflow

This project demonstrates the complete development workflow:

### 1️⃣ **In Cursor (Local Development)**
- Create and edit code
- Run and test locally
- Commit and push to GitHub

### 2️⃣ **On Claude Mobile/Web** (claude.ai)
- Connect to this GitHub repository
- Ask Claude to add features:
  - "Add a revenue chart"
  - "Add dark mode toggle"
  - "Add more statistics cards"
  - "Create a user table view"
- Review and accept changes
- Claude commits directly to GitHub

### 3️⃣ **Back in Cursor**
```bash
git pull
python app.py  # See the new features!
```

## 🧪 Running Tests

The original test suite is still included:

```bash
pytest -v
```

To run with coverage:

```bash
pytest -v --cov=. --cov-report=term-missing
```

## 🔧 Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **Charts**: Chart.js
- **Testing**: pytest
- **CI/CD**: GitHub Actions

## 📦 Project Structure

```
infra_test/
├── app.py                    # Flask application
├── templates/
│   └── dashboard.html        # Dashboard UI
├── test_app.py              # Unit tests
├── requirements.txt         # Python dependencies
├── .github/
│   └── workflows/
│       └── ci.yml           # CI/CD pipeline
└── README.md                # This file
```

## 🎨 Customization Ideas (Ask Claude!)

Try asking Claude on mobile to:
- ✅ "Add a dark mode toggle"
- ✅ "Create a user activity table"
- ✅ "Add a revenue projection chart"
- ✅ "Implement real-time notifications"
- ✅ "Add data export functionality"
- ✅ "Create an API documentation page"

## 🐛 Troubleshooting

**Port already in use?**
```bash
# Change port in app.py:
app.run(debug=True, host='0.0.0.0', port=8080)
```

**Flask not installed?**
```bash
pip install Flask
```

**Browser not opening automatically?**
Just manually open: http://localhost:5000

## 🎉 Success!

If you see a beautiful dashboard with animated charts and stats, you're all set! 

Now you can impress your colleagues and demonstrate the seamless **Cursor + GitHub + Claude** workflow! 🚀

---

**Built with ❤️ to test modern development workflows**
