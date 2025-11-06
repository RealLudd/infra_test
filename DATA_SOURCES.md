# CashWeb Dashboard - Data Sources

## Overview

The dashboard uses two types of data sources:
1. **Historical Database** - Consolidated daily records (updated after each day completes)
2. **Live Network Data** - Real-time data from today's processing

## Section-by-Section Breakdown

### 1. Daily / Weekly Overview (Top Cards)
**Endpoint:** `/api/overview`

| Period | Data Source | Updates |
|--------|------------|---------|
| **Today** | Live data only (raw data → processed output) | Manual refresh |
| Week | Historical DB (last 7 days, excluding today) | Once daily |
| Month | Historical DB (last 30 days, excluding today) | Once daily |
| Quarter | Historical DB (last 90 days, excluding today) | Once daily |

**Key Points:**
- When user clicks "Today": Shows real-time data from network paths
- When user clicks "Week/Month/Quarter": Shows historical data from consolidated DB
- Historical data must be added to DB daily after processing completes

---

### 2. Automation % Over Time (Chart)
**Endpoint:** `/api/automation-trend`

**Data Source:** Historical DB ONLY (excluding today)

**Updates:** Once daily (when new records added to DB)

**Key Points:**
- Chart never includes today's live data
- Shows trends from completed days only
- Requires daily updates to consolidated Excel database

---

### 3. Company Code Processing Status (Cards)
**Endpoint:** `/api/company-status`

**Data Source:** TODAY's live data ONLY

**Update Frequency:** Auto-refresh every 5 minutes

**Data Flow Timeline:**
```
Before 8:00 AM → Shows "Awaiting Today" (from historical DB for reference)
↓
8:00 AM → Raw data downloads
↓
Shows "Not Started" with actual counts from:
  \\...\02_RD\02_P\2025\YYYYMM\YYYYMMDD\{bank_account}\
  (Counts .xls files = total payments)
↓
~8:25 AM → Processing starts
↓
Shows "In Process" with progress from:
  \\...\03_Output\2025\YYYYMM\YYYYMMDD\{bank_account}.xlsx
  (Counts rows where Match = 'YES' = processed)
↓
Processing completes
↓
Shows "Done" (100%)
```

**Key Points:**
- Always monitors TODAY's data
- Starts with raw data counts (Pending = total files)
- Switches to processed output when available (Pending = not yet matched)
- Refreshes automatically every 5 minutes

---

### 4. Recent Transactions
**Endpoint:** `/api/recent-transactions`

**Data Source:** TODAY's live data (processed output files)

**Update Frequency:** Auto-refresh every 5 minutes

**Key Points:**
- Shows last 10 transactions from today's processed files
- Only available after processing starts (~8:25 AM)
- Refreshes automatically every 5 minutes

---

## Network Paths

### Raw Data (Input)
- **PACO:** `\\emea\central\SSC_GROUP\BPA\30_Automations\90_CashOps\02_Posting Cash\02_RD\02_P\2025\{YYYYMM}\{YYYYMMDD-1}\`
- **FRAN:** `\\emea\central\SSC_GROUP\BPA\30_Automations\90_CashOps\02_Posting Cash\02_RD\02_F\2025\{YYYYMM}\{YYYYMMDD-1}\`

Note: Raw data is from YESTERDAY (payments received today are from yesterday's transactions)

### Processed Output
- **PACO:** `\\emea\central\SSC_GROUP\BPA\30_Automations\90_CashOps\02_Posting Cash\03_Output\2025\{YYYYMM}\{YYYYMMDD}\`
- **FRAN:** `\\emea\central\SSC_GROUP\BPA\30_Automations\90_CashOps\02_Posting Cash\03_Output\2025\{YYYYMM}\{YYYYMMDD}\`

Note: Output is TODAY's date

---

## Daily Maintenance

### Required Action: Update Historical Database
After each day's processing completes, add records to:
```
infra_test/data/paco_consolidated.xlsx
```

**Required Columns:**
- date
- company_code
- housebank
- currency
- total_payments
- automated_count
- assigned_to_account
- invoices_assigned
- total_received_eur
- value_assigned_eur
- processing_minutes
- file_timestamp
- ... (and other metrics)

Use the consolidation script to automatically add today's data to historical DB.

---

## Auto-Refresh Schedule

| Section | Refresh Frequency | Method |
|---------|------------------|--------|
| Daily/Weekly Overview | Manual | User clicks period buttons |
| Automation Chart | Manual | User changes period |
| Company Status | 5 minutes | Automatic polling |
| Recent Transactions | 5 minutes | Automatic polling |

