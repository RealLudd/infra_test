# PACO Data Integration - CashWeb Dashboard

## Overview
The CashWeb dashboard now displays **real PACO automation data** from Excel files stored on the network. The system uses a **dual-source architecture** to provide both historical analytics and real-time processing status.

---

## Data Architecture

### 1. **Historical Data** (Consolidated Database)
- **File**: `data/paco_consolidated.xlsx`
- **Contains**: All 2025 data up to 2 days ago (4,093 records as of Nov 5, 2025)
- **Updated**: Once daily (recommended: 7:00 PM)
- **Used for**: 
  - Overview metrics (weekly, monthly, quarterly trends)
  - Automation trend charts
  - Historical analysis

### 2. **Live Data** (Network Path - Real-Time)
- **Source**: `\\emea\central\SSC_GROUP\BPA\30_Automations\90_CashOps\02_Posting Cash\03_Output\2025\`
- **Contains**: Yesterday's data (today's processing - bank payments received today are from yesterday)
- **Updated**: Every 5 minutes (frontend polling)
- **Used for**:
  - Company Code Processing Status (live progress)
  - Recent Transactions list
  - Today's overview metrics

---

## Important: Date Logic

**Key Concept**: Bank payments from **yesterday** are received and processed **today**.

- **"Today's data"** = Yesterday's date files (e.g., Nov 5 displays Nov 4 data)
- **Historical data** = Everything up to 2 days ago
- **Live monitoring** = Yesterday's files being processed throughout the day

### Example (November 5, 2025):
- **Dashboard displays**: November 4 files as "today's live data"
- **Historical DB contains**: Data up to November 3
- **Network path folder**: `2025\202511\20251104\`

---

## File Structure

### Network Path Structure:
```
\\emea\central\SSC_GROUP\BPA\30_Automations\90_CashOps\02_Posting Cash\03_Output\2025\
├── 202501\           # January 2025
│   ├── 20250102\
│   │   ├── 0010_1050D_EUR.xlsx
│   │   ├── 0011_1101I_CHF.xlsx
│   │   └── ...
│   └── 20250103\
├── 202502\           # February 2025
└── ...
```

### Excel File Naming Convention:
- **Format**: `CCCC_HHHH_CUR.xlsx`
  - `CCCC` = Company Code (e.g., 0010, 0040)
  - `HHHH` = Housebank (e.g., 1050D, 4350I)
  - `CUR` = Currency (e.g., EUR, GBP2, USD)
- **Example**: `0010_1050D_EUR.xlsx`

---

## Excel File Columns

The system reads the following columns from each Excel file:

| Column | Description | Used For |
|--------|-------------|----------|
| `Payment_Number` | Unique payment identifier | Total payment count |
| `Amount` | Payment amount | Total received, value assigned |
| `Business_Partner` | Customer ID | Assigned to account count |
| `Docnumbers` | Invoice numbers (separated by `;`) | Invoices assigned count |
| `Match` | "YES" if automated, "No" if manual | Automation percentage |
| `Payment Date` | Date of payment | Transaction display |

---

## Dashboard Metrics Calculation

### Overview Metrics:
1. **Total Received** = Sum of all `Amount` values
2. **Total Payments** = Count of `Payment_Number` rows
3. **Process Automatically** = Count where `Match` = "YES"
4. **Assigned to Account** = Count where `Business_Partner` is filled
5. **Invoices Assigned** = Count of invoices in `Docnumbers` (split by `;`)
6. **Value Assigned** = Sum of `Amount` where `Match` = "YES"

### Company Status:
- **Status**: "Not Started" / "In Process" / "Done"
- **Progress**: (Processed / Total) × 100%
- **Start Time**: 8:00 AM (process start)
- **End Time**: File modification timestamp (when status = "Done")

---

## Daily Workflow

### Morning (8:00 AM - 10:00 AM):
1. Bank payments from yesterday are received
2. Files are created in network path: `2025\YYYYMM\YYYYMMDD\`
3. Dashboard displays "Company Code Processing Status" with live progress
4. As matching completes, status updates from "Not Started" → "In Process" → "Done"

### Throughout the Day:
- Dashboard polls every 5 minutes for updates
- Recent transactions refresh automatically
- Company status cards update in real-time

### Evening (7:00 PM - Recommended):
1. Run `process_paco_data.py` to consolidate yesterday's data
2. Historical database is updated
3. Ready for next day's processing

---

## Scripts

### 1. `process_paco_data.py` - Data Consolidator
**Purpose**: Scan network path and build consolidated historical database

**Usage**:
```bash
cd C:\Users\SA_DE_RPA\CashWeb\infra_test
python process_paco_data.py
```

**What it does**:
- Scans all 2025 folders (excludes today and yesterday)
- Processes each Excel file
- Calculates daily aggregates per bank account
- Updates `data/paco_consolidated.xlsx`

**Schedule**: Run once daily (e.g., 7:00 PM via Windows Task Scheduler)

### 2. `app.py` - Flask Application
**Purpose**: Serve dashboard and API endpoints

**Usage**:
```bash
cd C:\Users\SA_DE_RPA\CashWeb\infra_test
python app.py
```

**Runs on**: http://localhost:5000

---

## API Endpoints

### `/api/overview`
**Query Parameters**: `period` (today, week, month, quarter), `bank_account`
**Returns**: Aggregated metrics

```json
{
  "total_payments": 1231,
  "total_received": 43279624.16,
  "automation_percentage": 0.0,
  "assigned_count": 1033,
  "assigned_percentage": 83.9
}
```

### `/api/company-status`
**Returns**: Live processing status for each bank account

```json
{
  "company_statuses": [
    {
      "bank_account": "0010_1050D_EUR",
      "company_code": "0010",
      "housebank": "1050D",
      "currency": "EUR",
      "status": "In Process",
      "processed": 45,
      "pending": 21,
      "total": 66,
      "percentage": 68.2,
      "start_time": "2025-11-05T08:00:00",
      "end_time": null
    }
  ]
}
```

### `/api/recent-transactions`
**Returns**: Last 10 transactions from today's live data

```json
{
  "transactions": [
    {
      "payment_number": "106",
      "business_partner": "750396",
      "amount": 2043.56,
      "match": "No",
      "payment_date": "20251104",
      "company_code": "0010",
      "housebank": "1050D",
      "currency": "EUR"
    }
  ]
}
```

### `/api/automation-trend`
**Query Parameters**: `period` (week, month, quarter), `bank_account`
**Returns**: Daily automation percentages for charts

```json
{
  "labels": ["Mon 10/29", "Tue 10/30", "Wed 10/31"],
  "paco_percentages": [0.0, 0.0, 0.0],
  "fran_percentages": [0, 0, 0],
  "payment_counts": [1336, 1191, 1816]
}
```

### `/api/filter-options`
**Returns**: Available bank account configurations for filters

---

## Frontend Updates (5-Minute Polling)

The dashboard automatically refreshes these sections every 5 minutes:

1. **Company Code Processing Status** - Live progress cards
2. **Recent Transactions** - Latest payment details

Other sections (Overview, Automation Trend) load once on page load.

---

## Future: FRAN Integration

When FRAN data becomes available:

1. Update `FRAN_NETWORK_PATH` in `app.py`
2. No code changes needed - system already supports both PACO and FRAN
3. Pass `automation_type=FRAN` parameter to API endpoints
4. Dashboard will display FRAN data alongside PACO

---

## Troubleshooting

### Dashboard shows no data:
1. Check network path is accessible: `\\emea\central\SSC_GROUP\BPA\30_Automations\90_CashOps\02_Posting Cash\03_Output\2025\`
2. Verify yesterday's folder exists: `2025\YYYYMM\YYYYMMDD\`
3. Check Flask server is running: http://localhost:5000/health

### Company Status is empty:
- This is normal if no files exist for yesterday's date
- Status will populate once files are created (usually around 8:00 AM)

### Historical data not updating:
- Run `process_paco_data.py` manually
- Check consolidated database exists: `data/paco_consolidated.xlsx`
- Verify network path has data up to 2 days ago

---

## Summary of Changes

### Files Created:
1. `process_paco_data.py` - Data processor for historical consolidation
2. `data/paco_consolidated.xlsx` - Consolidated historical database (4,093 records)
3. `PACO_DATA_INTEGRATION.md` - This documentation

### Files Updated:
1. `app.py` - Dual-source data loading (historical + live)
2. `requirements.txt` - Added `openpyxl==3.1.2`, `pandas==2.1.4`
3. `static/js/dashboard.js` - 5-minute polling for live data

### Key Features:
✅ Real PACO data from 4,093 Excel files (2025 data)
✅ Historical metrics from consolidated database
✅ Live processing status from network path (yesterday's data)
✅ Real-time company status cards (updated every 5 minutes)
✅ Recent transactions from actual payment files
✅ Automation trend charts with real data
✅ Ready for FRAN integration (no changes needed)

---

## Quick Start

1. **Start Dashboard**:
```bash
cd C:\Users\SA_DE_RPA\CashWeb\infra_test
python app.py
```

2. **Open Browser**: http://localhost:5000

3. **Daily Maintenance** (optional, for historical data):
```bash
python process_paco_data.py
```

---

**Last Updated**: November 5, 2025
**Data Records**: 4,093 payment files processed
**Status**: ✅ Fully operational with real PACO data

