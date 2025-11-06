# 💰 CashWeb - Automated Payment Processing Dashboard

A modern, real-time web application for monitoring and managing automated payment processing with comprehensive analytics, built with Flask and vanilla JavaScript.

## ✨ Features

### 📊 **Real-Time Dashboard**
- Live monitoring of payment processing status
- Daily/Weekly/Monthly/Quarterly overview with dynamic metrics
- Real-time automation percentage tracking
- Processing time analytics

### 🎯 **Company Code Processing Status**
- Real-time status for each bank account configuration
- Visual progress indicators with "Matched" and "Value Assigned" percentages
- Individual card status: Not Started → Done
- Processing time tracking (8:00 AM start → completion)
- Displays total payments, customers assigned, and invoices matched

### 📈 **Advanced Filtering**
- **Cascading Filters**: Region selection automatically filters Company Code and Bank Account options
- **Region Filter**: Group by geographical regions (Iberia, France, NDX, UK, BNX, GerAus, PLN)
- **Company Code Filter**: Filter by specific company codes (0010-0044)
- **Bank Account Filter**: Drill down to specific bank account configurations
- Filters apply to overview metrics, charts, and card display

### 📉 **Automation Trend Charts**
- Interactive Chart.js visualizations
- 7/30/90-day trend analysis
- Automation percentage over time
- Payment count tracking

### 💱 **Multi-Currency Support**
- Automatic EUR conversion for all amounts
- Handles EUR, USD, GBP, CHF, PLN, NOK, CZK, and more
- Consolidated reporting in EUR

### 🔄 **Live Data Integration**
- Real-time data from network paths
- Automatic fallback to raw data when processing hasn't started
- Processes both `.xls` and `.xlsx` files
- Case-insensitive matching (handles "Yes"/"YES" variations)

### 📦 **Database Consolidation**
- Daily automated data collection
- Historical trend tracking in `paco_consolidated.xlsx`
- Duplicate detection and replacement

### 🎨 **Modern UI/UX**
- Beautiful dark theme with gradient accents
- Responsive design for all screen sizes
- Smooth animations and transitions
- Modern favicon with gradient euro symbol
- Real-time refresh button with visual feedback

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Access to network paths: `\\emea\central\SSC_GROUP\BPA\30_Automations\90_CashOps\02_Posting Cash\`
- pandas, openpyxl for Excel file processing

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
   Or double-click: `start_dashboard.bat`

4. **Open in your browser:**
   ```
   http://localhost:5000
   ```

That's it! 🎉

## 🖥️ Daily Operations

### Batch Files for Easy Management

#### `start_dashboard.bat`
Starts the Flask server and opens the dashboard in your browser.

```cmd
start_dashboard.bat
```

#### `update_dashboard.bat`
Opens the dashboard and shows instructions for refreshing data.
- Click the refresh icon (sync button) in the navbar to update Company Code Processing Status
- Or refresh the page to reload all data

```cmd
update_dashboard.bat
```

#### `consolidate_daily_data.bat`
Processes today's output files and updates the consolidated database.
- Reads Excel files from today's output folder
- Adds new records to `paco_consolidated.xlsx`
- Replaces existing records for the same date (prevents duplicates)

```cmd
consolidate_daily_data.bat
```

**Recommended Daily Workflow:**
1. Morning: Run `start_dashboard.bat` to start monitoring
2. During the day: Use the refresh button to check progress
3. End of day: Run `consolidate_daily_data.bat` to save results

## 📡 API Endpoints

### `GET /api/overview`
Get dashboard overview with automation metrics.

**Parameters:**
- `period`: today/week/month/quarter (default: today)
- `region`: Filter by region (e.g., "Iberia", "France")
- `company_code`: Filter by company code (e.g., "0010")
- `bank_account`: Filter by specific bank account (format: "0010|1050D|EUR")

**Response:**
```json
{
  "period": "today",
  "total_payments": 6563,
  "total_received": 485517721,
  "automation_percentage": 39.8,
  "assigned_percentage": 84.2,
  "total_invoices_assigned": 841,
  "value_assigned_percentage": 2.0,
  "avg_auto_time_minutes": 80.3
}
```

### `GET /api/company-status`
Get real-time processing status for each bank account configuration.

**Response:**
```json
{
  "company_statuses": [
    {
      "company_code": "0010",
      "housebank": "1050D",
      "currency": "EUR",
      "status": "Done",
      "matched_count": 30,
      "matched_percentage": 50.8,
      "customers_assigned": 48,
      "invoices_assigned": 30,
      "total": 59,
      "value_assigned_percentage": 5.1,
      "start_time": "2025-11-06T08:00:00",
      "end_time": "2025-11-06T08:13:24"
    }
  ]
}
```

### `GET /api/automation-trend`
Get automation trend data for charts (historical data only).

**Parameters:**
- `period`: week/month/quarter (default: week)
- `region`, `company_code`, `bank_account`: Same as overview

### `GET /api/recent-transactions`
Get recent transactions from today's processing (last 10).

### `GET /api/filter-options`
Get available bank account configurations for filter dropdowns.

### `GET /health`
Health check endpoint.

## 🧪 Running Tests

Run the test suite with pytest:

```bash
pytest test_app.py -v
```

With coverage report:

```bash
pytest test_app.py -v --cov=app --cov-report=term-missing
```

## 🔧 Tech Stack

- **Backend:** Flask (Python 3.9+)
- **Data Processing:** pandas, openpyxl
- **Frontend:** HTML5, CSS3, Vanilla JavaScript (ES6+)
- **Charts:** Chart.js 4.4.0
- **Icons:** Font Awesome 6.4.0
- **Fonts:** Google Fonts (Poppins)
- **Testing:** pytest

## 📦 Project Structure

```
infra_test/
├── app.py                          # Main Flask application
├── test_app.py                     # Unit tests
├── requirements.txt                # Python dependencies
├── start_dashboard.bat             # Start server and open browser
├── update_dashboard.bat            # Open dashboard (refresh data)
├── consolidate_daily_data.bat      # Daily data consolidation
├── consolidate_daily_data.py       # Data consolidation script
├── templates/
│   └── index.html                  # Main dashboard template
├── static/
│   ├── css/
│   │   └── black-dashboard.css     # Dashboard styling
│   ├── js/
│   │   └── dashboard.js            # Dashboard logic & interactivity
│   └── favicon.svg                 # Modern gradient favicon
├── DATA_SOURCES.md                 # Data source documentation
├── USAGE_GUIDE.md                  # User guide
├── QUICKSTART.md                   # Quick start guide
├── README.md                       # This file
└── .gitignore                      # Git ignore rules
```

## 📊 Data Sources

### Daily / Weekly Overview
- **"Today"**: Live data from today's processed output files
- **"Week/Month/Quarter"**: Historical data from `paco_consolidated.xlsx`

### Company Code Processing Status
- **Real-time monitoring** of today's processing
- Falls back to raw data if processing hasn't started
- Shows "Not Started", "Done" status based on file existence

### Recent Transactions
- Live data from today's processed output files only

### Automation % Over Time Chart
- Historical data only (excludes today for accuracy)

For detailed data flow, see `DATA_SOURCES.md`

## 🌐 Network Paths

### Configuration in `app.py`:

```python
# Database path
CONSOLIDATED_DB_PATH = r"\\emea\central\SSC_GROUP\BPA\30_Automations\90_CashOps\02_Posting Cash\99_Consolidated_data\paco_consolidated.xlsx"

# PACO paths
PACO_OUTPUT_PATH = r"\\emea\central\SSC_GROUP\BPA\30_Automations\90_CashOps\02_Posting Cash\03_Output"
PACO_RAW_DATA_PATH = r"\\emea\central\SSC_GROUP\BPA\30_Automations\90_CashOps\02_Posting Cash\02_RD\02_P"
```

## 🎯 Filter Behavior

### Region Filter
Selecting a region (e.g., "Iberia") automatically:
- Filters **Company Code** dropdown to show only codes in that region
- Filters **Bank Account** dropdown to show only accounts in that region
- Updates **Overview metrics** and **Charts** to show only that region's data

### Company Code Filter
Can be used **independently** or **combined with Region**:
- **Alone**: Shows data for that company code
- **With Region**: Narrows down within the region (e.g., "Iberia" → "0041" shows only 0041)

### Bank Account Filter
Most specific filter - overrides Region and Company Code:
- Shows data for that exact bank account configuration only

### Clear Filters Button
Resets all filters and shows complete data.

## 🔐 Security Notes

This is configured for internal network use. For broader deployment:

- Add authentication and authorization
- Use HTTPS (SSL/TLS)
- Implement rate limiting
- Add comprehensive input validation
- Set `debug=False` in production
- Use environment variables for sensitive paths

## 🐛 Troubleshooting

**Dashboard shows zeros/spinners?**
- Check network path access
- Ensure date folders exist (YYYYMM/YYYYMMDD format)
- Verify Excel files are not corrupted

**Filters not working?**
- Hard refresh browser (Ctrl+F5)
- Check browser console for errors
- Verify filter options are loading

**Port already in use?**
```bash
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**Can't access network paths?**
- Verify VPN connection
- Check permissions on network share
- Ensure paths exist and are accessible

## 📝 Recent Updates

### v2.0 (November 2025)
- ✅ Complete dashboard redesign with dark theme
- ✅ Real-time company code processing status cards
- ✅ Cascading filter system (Region → Company Code → Bank Account)
- ✅ Multi-currency support with EUR conversion
- ✅ Value assigned % tracking (amount-based automation)
- ✅ Improved data source logic (raw data fallback)
- ✅ Modern favicon and enhanced UI/UX
- ✅ Batch files for daily operations
- ✅ Case-insensitive matching for Excel columns
- ✅ Combined filter support (Region + Company Code)

## 📄 License

This project is internal to the organization.

## 🤝 Contributing

For feature requests or bug reports, please contact the development team.

---

**Built with ❤️ for automated payment processing excellence**
