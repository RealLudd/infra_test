# CashWeb Dashboard - Usage Guide

## Quick Start

### 1. Start the Dashboard
```batch
start_dashboard.bat
```
- Opens the dashboard in your browser at http://localhost:5000
- Server runs in a background window

### 2. Daily Data Consolidation (End of Day)
```batch
consolidate_daily_data.bat
```
- Run this **after** PACO processing completes each day
- Collects today's output files and adds them to the historical database
- Automatically replaces existing records for the same date

### 3. Update/Refresh Dashboard
```batch
update_dashboard.bat
```
- Checks if dashboard is running
- If not running, starts it
- If running, opens it in browser

---

## Batch Files Explained

### `start_dashboard.bat`
**Purpose:** Start the web dashboard server

**When to use:**
- First time running the dashboard
- After restarting your computer
- When the dashboard is not accessible

**What it does:**
- Checks if server is already running (port 5000)
- Starts Flask server in background window
- Opens http://localhost:5000 in your browser

---

### `consolidate_daily_data.bat`
**Purpose:** Add today's PACO data to historical database

**When to use:**
- **Daily at end of business day** (after PACO processing completes)
- When you want to update historical charts
- To backfill missing dates

**What it does:**
1. Locates today's output files:
   ```
   \\emea\central\SSC_GROUP\BPA\30_Automations\90_CashOps\02_Posting Cash\03_Output\2025\{YYYYMM}\{YYYYMMDD}\
   ```

2. Processes each bank account file:
   - Counts payments, matched items, invoices
   - Converts amounts to EUR
   - Calculates processing times

3. Updates `data/paco_consolidated.xlsx`:
   - Removes old records for this date (if any)
   - Adds new records
   - Saves updated database

**Output Example:**
```
========================================================
PACO Data Consolidation - 2025-11-06
========================================================

Found 16 files to process:

  Processing: 0010_1050D_EUR.xlsx
  ✓ 10_1050D_EUR: 59 payments, 45 automated (76.3%)
  
  Processing: 0012_570BE_EUR.xlsx
  ✓ 12_570BE_EUR: 137 payments, 98 automated (71.5%)
  
  ...

========================================================
✅ CONSOLIDATION COMPLETE
========================================================
   Records added: 16
   Records removed: 0
   Total records: 4090
   Database: data/paco_consolidated.xlsx
========================================================
```

**Advanced Usage - Consolidate Specific Date:**
```batch
python consolidate_daily_data.py 2025-11-05
```

---

### `update_dashboard.bat`
**Purpose:** Refresh or open the dashboard

**When to use:**
- Quick access to dashboard
- After consolidating new data
- To verify server is running

**What it does:**
- Checks if Flask server is running
- If running → Opens browser
- If not running → Starts server then opens browser

---

## Dashboard Sections & Data Sources

### Section 1 & 2: Overview Cards + Chart
**Data Source:** Historical Database (`data/paco_consolidated.xlsx`)

**Updates:**
- Manually update by clicking period buttons (Today/Week/Month/Quarter)
- "Today" button shows live data from network paths
- Other periods show historical data

**To refresh:** Run `consolidate_daily_data.bat` after each day completes

---

### Section 3 & 4: Company Status + Recent Transactions
**Data Source:** Live network paths (today's data)

**Updates:**
- Automatically every 5 minutes
- Monitors current processing in real-time
- Click the **refresh button** (sync icon) in navbar for immediate update

**Visual Indicators:**
- **Not Started**: File hasn't been generated yet (gray badge)
- **Done**: File has been generated and processed (green badge)
- **Matched %**: Percentage of payments with perfect match (Match = "Yes")
- **Value Assigned %**: Percentage of total amount that was matched

---

## Using Filters

### Cascading Filter System

The dashboard includes intelligent filters that work together:

#### **1. Region Filter**
Select a geographical region to focus on specific company codes:
- **Iberia**: 0040, 0041
- **France**: 0043
- **NDX**: 0019, 0022, 0023, 0024
- **UK**: 0014
- **BNX**: 0012, 0018
- **GerAus**: 0010, 0033
- **PLN**: 0023

**What happens:**
- Company Code dropdown shows only codes in that region
- Bank Account dropdown shows only accounts in that region
- Overview metrics and charts update to show only that region's data

#### **2. Company Code Filter**
Select a specific company code (e.g., 0010, 0041, 0043)

**Can be used:**
- **Alone**: Shows all data for that company code
- **With Region**: Narrows down within the region (e.g., select "Iberia" → then "0041")

#### **3. Bank Account Configuration Filter**
Most specific filter - select an exact account configuration (e.g., "0010 - 1050D - EUR")

**Effect:**
- Overrides Region and Company Code filters
- Shows data for that specific account only
- Updates all sections: Overview, Charts, Status Cards

#### **Clear Filters Button**
Resets all filters and displays complete data.

### Filter Examples

**Example 1: Focus on France**
1. Select **Region: "France (0043)"**
2. Company Code automatically shows only: 0043
3. Bank Account shows: 0043_4335I_EUR, 0043_4350I_EUR
4. Overview and charts now show only France data

**Example 2: Iberia → Spain (0041)**
1. Select **Region: "Iberia (0040, 0041)"**
2. Select **Company Code: "0041"**
3. Bank Account now shows only 0041 accounts
4. Data filtered to 0041 within Iberia

**Example 3: Specific Bank Account**
1. Select **Bank Account: "0010 - 1050D - EUR"**
2. Other filters are overridden
3. Shows only that exact account configuration

---

## Daily Workflow

### Morning (8:00 AM - 10:00 AM)
1. Open dashboard (if not running):
   ```batch
   start_dashboard.bat
   ```

2. Monitor live processing:
   - Company Code Processing Status shows real-time progress
   - Auto-refreshes every 5 minutes
   - No manual action required

### End of Day (After Processing Completes)
1. Run consolidation:
   ```batch
   consolidate_daily_data.bat
   ```

2. Verify in dashboard:
   - Click "Week" button to see updated historical data
   - Check that today's data appears in charts

### Troubleshooting

**Problem:** "Output folder does not exist"
- **Cause:** PACO processing hasn't completed yet
- **Solution:** Wait for processing to finish, then run again

**Problem:** Dashboard shows old data
- **Cause:** Haven't run consolidation or haven't refreshed
- **Solution:**
  1. Run `consolidate_daily_data.bat`
  2. Refresh browser (F5)
  3. Click period buttons to reload

**Problem:** Company status shows "Awaiting Today"
- **Cause:** Raw data hasn't downloaded yet (before 8:00 AM)
- **Solution:** Wait until 8:00 AM when raw data downloads

**Problem:** Port 5000 already in use
- **Cause:** Another Flask instance is running
- **Solution:**
  1. Find the Flask window and close it
  2. Or open Task Manager → End Python process
  3. Run `start_dashboard.bat` again

---

## File Locations

### Database
```
infra_test/data/paco_consolidated.xlsx
```
- Historical records from all processed days
- Updated daily by consolidation script

### Network Paths
**Raw Data (Input):**
```
\\emea\central\SSC_GROUP\BPA\30_Automations\90_CashOps\02_Posting Cash\02_RD\02_P\2025\{YYYYMM}\{YYYYMMDD-1}\
```

**Processed Output:**
```
\\emea\central\SSC_GROUP\BPA\30_Automations\90_CashOps\02_Posting Cash\03_Output\2025\{YYYYMM}\{YYYYMMDD}\
```

### Configuration
Edit `app.py` if paths change:
```python
CONSOLIDATED_DB_PATH = "data/paco_consolidated.xlsx"
PACO_NETWORK_PATH = r"\\emea\...\03_Output\2025"
PACO_RAW_DATA_PATH = r"\\emea\...\02_RD\02_P\2025"
```

---

## Support

For issues or questions, check:
- `DATA_SOURCES.md` - Detailed data source documentation
- `PACO_DATA_INTEGRATION.md` - Integration guide
- `README.md` - Technical documentation

