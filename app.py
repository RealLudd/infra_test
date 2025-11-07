"""
CashWeb - Cash Management Web Application
A Flask application for tracking PACO/FRAN automation analytics with dual-source data:
- Historical data from consolidated Excel database
- Live data from network path for real-time status
"""
from flask import Flask, render_template, jsonify, request
from datetime import datetime, timedelta, date
import pandas as pd
import os
import re
import json
from currency_converter import convert_to_eur

app = Flask(__name__)

# Configuration
CONSOLIDATED_DB_PATH = "data/paco_consolidated.xlsx"
FRAN_CONSOLIDATED_DB_PATH = "data/fran_consolidated.xlsx"
PACO_NETWORK_PATH = r"\\emea\central\SSC_GROUP\BPA\30_Automations\90_CashOps\02_Posting Cash\03_Output\2025"
FRAN_NETWORK_PATH = r"\\emea\central\SSC_GROUP\BPA\30_Automations\90_CashOps\02_Posting Cash\03_Output\2025"
PACO_RAW_DATA_PATH = r"\\emea\central\SSC_GROUP\BPA\30_Automations\90_CashOps\02_Posting Cash\02_RD\02_P\2025"
FRAN_RAW_DATA_PATH = r"\\emea\central\SSC_GROUP\BPA\30_Automations\90_CashOps\02_Posting Cash\02_RD\02_F\2025"
CUSTOMER_EXCEPTIONS_PATH = "data/customer_exceptions.json"

# Global cache for historical data
historical_data_cache = None
historical_data_timestamp = None
fran_data_cache = None
fran_data_timestamp = None

# Customer exceptions storage helpers
def load_customer_exceptions():
    """Load customer exceptions from JSON file"""
    if os.path.exists(CUSTOMER_EXCEPTIONS_PATH):
        try:
            with open(CUSTOMER_EXCEPTIONS_PATH, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading customer exceptions: {str(e)}")
            return []
    return []

def save_customer_exceptions(exceptions):
    """Save customer exceptions to JSON file"""
    try:
        os.makedirs(os.path.dirname(CUSTOMER_EXCEPTIONS_PATH), exist_ok=True)
        with open(CUSTOMER_EXCEPTIONS_PATH, 'w') as f:
            json.dump(exceptions, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving customer exceptions: {str(e)}")
        return False

def load_historical_data(force_reload=False):
    """
    Load PACO historical data from consolidated Excel database.
    Caches the data to avoid repeated file reads.
    """
    global historical_data_cache, historical_data_timestamp
    
    # Check if cache is valid (less than 5 minutes old)
    if not force_reload and historical_data_cache is not None:
        if historical_data_timestamp and (datetime.now() - historical_data_timestamp).seconds < 300:
            return historical_data_cache
    
    # Load data from Excel
    if os.path.exists(CONSOLIDATED_DB_PATH):
        try:
            df = pd.read_excel(CONSOLIDATED_DB_PATH, engine='openpyxl')
            df['date'] = pd.to_datetime(df['date']).dt.date
            historical_data_cache = df
            historical_data_timestamp = datetime.now()
            return df
        except Exception as e:
            print(f"Error loading PACO historical data: {str(e)}")
            return pd.DataFrame()
    else:
        print(f"PACO historical database not found: {CONSOLIDATED_DB_PATH}")
        return pd.DataFrame()

def load_fran_historical_data(force_reload=False):
    """
    Load FRAN historical data from consolidated Excel database.
    Caches the data to avoid repeated file reads.
    """
    global fran_data_cache, fran_data_timestamp
    
    # Check if cache is valid (less than 5 minutes old)
    if not force_reload and fran_data_cache is not None:
        if fran_data_timestamp and (datetime.now() - fran_data_timestamp).seconds < 300:
            return fran_data_cache
    
    # Load data from Excel
    if os.path.exists(FRAN_CONSOLIDATED_DB_PATH):
        try:
            df = pd.read_excel(FRAN_CONSOLIDATED_DB_PATH, engine='openpyxl')
            df['date'] = pd.to_datetime(df['date']).dt.date
            fran_data_cache = df
            fran_data_timestamp = datetime.now()
            return df
        except Exception as e:
            print(f"Error loading FRAN historical data: {str(e)}")
            return pd.DataFrame()
    else:
        print(f"FRAN historical database not found: {FRAN_CONSOLIDATED_DB_PATH}")
        return pd.DataFrame()

def parse_filename(filename):
    """
    Parse filename to extract company_code, housebank, and currency.
    Expected format: CCCC_HHHH_CUR.xlsx (e.g., 0010_1050D_EUR.xlsx)
    """
    name = filename.replace('.xlsx', '')
    parts = name.split('_')
    
    if len(parts) >= 3:
        company_code = parts[0]
        housebank = parts[1]
        currency = '_'.join(parts[2:])
        return company_code, housebank, currency
    
    return None, None, None

def count_invoices(docnumbers_str):
    """Count invoices from DocNumbers column (separated by ;)"""
    if pd.isna(docnumbers_str) or docnumbers_str == '':
        return 0
    invoices = [inv.strip() for inv in str(docnumbers_str).split(';') if inv.strip()]
    return len(invoices)

def process_live_excel_file(filepath):
    """
    Process a single Excel file and extract metrics for live data.
    Returns aggregated metrics and transaction details.
    """
    try:
        df = pd.read_excel(filepath, engine='openpyxl')
        df.columns = df.columns.str.strip()
        
        filename = os.path.basename(filepath)
        company_code, housebank, currency = parse_filename(filename)
        
        if not all([company_code, housebank, currency]):
            return None
        
        # Calculate metrics
        total_payments = len(df)
        total_received = df['Amount'].sum() if 'Amount' in df.columns else 0
        
        # Determine which DocNumbers column to use
        docnumbers_col = None
        if 'DocNumbers' in df.columns:
            docnumbers_col = 'DocNumbers'
        elif 'Docnumbers' in df.columns:
            docnumbers_col = 'Docnumbers'
        
        # Processed Automatically = Match == "Yes" AND has invoices (DocNumbers not empty)
        automated_count = 0
        if 'Match' in df.columns and docnumbers_col:
            automated_mask = (df['Match'].str.upper() == 'YES') & (df[docnumbers_col].notna()) & (df[docnumbers_col] != '')
            automated_count = len(df[automated_mask])
        
        assigned_to_account = len(df[df['Business_Partner'].notna()]) if 'Business_Partner' in df.columns else 0
        
        invoices_assigned = 0
        if docnumbers_col:
            invoices_assigned = df[docnumbers_col].apply(count_invoices).sum()
        
        # Value Assigned = Amount for rows where Match == "Yes" AND has invoices
        value_assigned = 0
        if 'Match' in df.columns and 'Amount' in df.columns and docnumbers_col:
            value_mask = (df['Match'].str.upper() == 'YES') & (df[docnumbers_col].notna()) & (df[docnumbers_col] != '')
            value_assigned = df[value_mask]['Amount'].sum()
        
        # Convert amounts to EUR
        total_received_eur = convert_to_eur(total_received, currency)
        value_assigned_eur = convert_to_eur(value_assigned, currency)
        
        # Get file timestamp
        file_timestamp = datetime.fromtimestamp(os.path.getmtime(filepath))
        start_of_day = datetime.combine(file_timestamp.date(), datetime.strptime('08:00', '%H:%M').time())
        processing_minutes = int((file_timestamp - start_of_day).total_seconds() / 60)
        
        # Extract recent transactions (last 5 for each file)
        transactions = []
        for idx, row in df.tail(5).iterrows():
            transactions.append({
                'payment_number': str(row.get('Payment_Number', '')),
                'business_partner': str(row.get('Business_Partner', '')),
                'amount': float(row.get('Amount', 0)),
                'match': str(row.get('Match', '')),
                'docnumbers': str(row.get('Docnumbers', '')),
                'payment_date': str(row.get('Payment Date', '')),
                'company_code': company_code,
                'housebank': housebank,
                'currency': currency
            })
        
        return {
            'company_code': company_code,
            'housebank': housebank,
            'currency': currency,
            'total_received': float(total_received),
            'total_received_eur': float(total_received_eur),
            'total_payments': int(total_payments),
            'automated_count': int(automated_count),
            'assigned_to_account': int(assigned_to_account),
            'invoices_assigned': int(invoices_assigned),
            'value_assigned': float(value_assigned),
            'value_assigned_eur': float(value_assigned_eur),
            'file_timestamp': file_timestamp,
            'processing_minutes': processing_minutes,
            'transactions': transactions
        }
        
    except Exception as e:
        with open('live_data_debug.txt', 'a') as f:
            f.write(f"  ERROR processing {os.path.basename(filepath)}: {str(e)}\n")
            import traceback
            f.write(traceback.format_exc())
        return None

def get_raw_data_counts(automation_type='PACO'):
    """
    Get raw data counts from today's raw data path (before processing starts).
    Returns list of bank account records with total payment counts.
    """
    raw_path = PACO_RAW_DATA_PATH if automation_type == 'PACO' else FRAN_RAW_DATA_PATH
    
    # Get today's date (raw data folder is created with today's date)
    today = date.today()
    today_str = today.strftime('%Y%m%d')
    month_str = today.strftime('%Y%m')
    
    # Build path to today's raw data folder
    raw_data_path = os.path.join(raw_path, month_str, today_str)
    
    print(f"[DEBUG] Looking for raw data in: {raw_data_path}")
    
    records = []
    
    if not os.path.exists(raw_data_path):
        print(f"[DEBUG] Raw data path does not exist: {raw_data_path}")
        return records
    
    # Look for subdirectories (e.g., 0010_1050D_EUR)
    try:
        for dirname in os.listdir(raw_data_path):
            dir_path = os.path.join(raw_data_path, dirname)
            if os.path.isdir(dir_path):
                # Parse directory name to extract company_code, housebank, currency
                company_code, housebank, currency = parse_filename(dirname)
                if not all([company_code, housebank, currency]):
                    continue
                
                # Keep company_code as is (with leading zeros like 0010)
                
                # Count Excel files in the directory (each file = 1 payment)
                # Raw data can be .xls or .xlsx format
                excel_files = [f for f in os.listdir(dir_path) 
                              if (f.endswith('.xls') or f.endswith('.xlsx')) and not f.startswith('~$')]
                total_payments = len(excel_files)
                
                if total_payments > 0:
                    records.append({
                        'company_code': company_code,
                        'housebank': housebank,
                        'currency': currency,
                        'total_payments': total_payments,
                        'total_received': 0,  # Unknown from raw data
                        'total_received_eur': 0,  # Unknown from raw data
                        'automated_count': 0,  # Not processed yet
                        'assigned_to_account': 0,  # Not processed yet
                        'invoices_assigned': 0,  # Not processed yet
                        'value_assigned': 0,  # Not processed yet
                        'value_assigned_eur': 0,  # Not processed yet
                        'processing_minutes': 0,  # Not processed yet
                        'is_raw': True,
                        'file_timestamp': datetime.now()
                    })
    except Exception as e:
        print(f"Error reading raw data: {str(e)}")
    
    return records

def get_live_data(automation_type='PACO'):
    """
    Read today's files from network path for real-time data.
    First checks processed output, then falls back to raw data if not available.
    Returns list of processed bank account records.
    
    Note: Looks at TODAY's folder (not yesterday's).
    """
    output_path = PACO_NETWORK_PATH if automation_type == 'PACO' else FRAN_NETWORK_PATH
    
    # Get today's date (live data folder uses today's date)
    today = date.today()
    today_str = today.strftime('%Y%m%d')
    month_str = today.strftime('%Y%m')
    
    # Build path to today's processed output folder
    output_folder = os.path.join(output_path, month_str, today_str)
    
    # Write debug to file
    with open('live_data_debug.txt', 'a') as f:
        f.write(f"\n[{datetime.now()}] Looking for processed output in: {output_folder}\n")
    
    records = []
    
    # First, try to get processed data
    if os.path.exists(output_folder):
        files = os.listdir(output_folder)
        excel_files = [f for f in files if f.endswith('.xlsx') and not f.startswith('~$')]
        with open('live_data_debug.txt', 'a') as f:
            f.write(f"Found {len(excel_files)} Excel files in output folder\n")
        
        # Process all Excel files in today's output folder
        for filename in excel_files:
            filepath = os.path.join(output_folder, filename)
            with open('live_data_debug.txt', 'a') as f:
                f.write(f"Processing output file: {filename}\n")
            record = process_live_excel_file(filepath)
            if record:
                records.append(record)
                with open('live_data_debug.txt', 'a') as f:
                    f.write(f"  SUCCESS: Processed {filename}\n")
            else:
                with open('live_data_debug.txt', 'a') as f:
                    f.write(f"  FAILED: Could not process {filename}\n")
    
    # If no processed files found, get raw data counts
    if not records:
        print(f"[DEBUG] No processed data found in {output_folder}, checking raw data...")
        records = get_raw_data_counts(automation_type)
        print(f"[DEBUG] Raw data returned {len(records)} records")
    else:
        print(f"[DEBUG] Found {len(records)} processed files")
    
    return records

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/overview')
def get_overview():
    """
    Get dashboard overview with automation metrics.
    
    Data Sources:
    - "Today" period: Only live data from today (real-time from network path)
    - "Week/Month/Quarter": Historical data from consolidated DB (updated daily)
    
    This endpoint does NOT auto-refresh - use for overview cards only.
    """
    period = request.args.get('period', 'today')
    bank_account = request.args.get('bank_account', '')
    region = request.args.get('region', '')
    company_code_filter = request.args.get('company_code', '')
    automation_type = request.args.get('automation_type', 'PACO')
    
    # Region to company codes mapping (frontend REGION_MAP)
    REGION_MAP = {
        'Iberia': ['0040', '0041'],
        'France': ['0043'],
        'NDX': ['0019', '0022', '0023', '0024'],
        'UK': ['0014'],
        'BNX': ['0012', '0018'],
        'GerAus': ['0010', '0033'],
        'PLN': ['0023']
    }
    
    # Parse bank account filter
    company_code, housebank, currency = '', '', ''
    if bank_account:
        parts = bank_account.split('|')
        if len(parts) == 3:
            company_code, housebank, currency = parts
    
    # Calculate date range
    # Note: "Today" shows current day's live data from network path
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    if period == 'today':
        # Today = only live data (no historical data)
        start_date = today
        end_date = today - timedelta(days=1)  # No historical data for "today"
    elif period == 'week':
        start_date = today - timedelta(days=7)
        end_date = yesterday  # Exclude today (it's live)
    elif period == 'month':
        start_date = today - timedelta(days=30)
        end_date = yesterday
    elif period == 'quarter':
        start_date = today - timedelta(days=90)
        end_date = yesterday
    else:
        start_date = today
        end_date = today - timedelta(days=1)
    
    # Initialize totals
    total_payments = 0
    total_received = 0
    automated_count = 0
    assigned_to_account = 0
    total_invoices_assigned = 0
    total_assigned_value = 0
    processing_times = []
    
    # Load historical data (if not today-only)
    if period != 'today':
        df = load_historical_data()
        if not df.empty:
            # Convert company_code to string for consistent filtering
            df['company_code'] = df['company_code'].apply(lambda x: str(x).zfill(4) if str(x).isdigit() else str(x))
            
            # Filter by date range
            mask = (df['date'] >= start_date) & (df['date'] <= end_date)
            
            # Apply bank account filter (most specific - overrides everything)
            if bank_account:
                mask &= (df['company_code'] == company_code) & \
                        (df['housebank'] == housebank) & \
                        (df['currency'] == currency)
            else:
                # Apply region filter (if set)
                if region and region in REGION_MAP:
                    mask &= df['company_code'].isin(REGION_MAP[region])
                # Apply company code filter (can combine with region)
                if company_code_filter:
                    mask &= (df['company_code'] == company_code_filter)
            
            filtered_df = df[mask]
            
            # Aggregate metrics (use EUR-converted amounts for totals)
            total_payments += filtered_df['total_payments'].sum()
            total_received += filtered_df['total_received_eur'].sum()  # EUR amounts
            automated_count += filtered_df['automated_count'].sum()
            assigned_to_account += filtered_df['assigned_to_account'].sum()
            total_invoices_assigned += filtered_df['invoices_assigned'].sum()
            total_assigned_value += filtered_df['value_assigned_eur'].sum()  # EUR amounts
            
            # Collect processing times from historical data
            if 'processing_minutes' in filtered_df.columns:
                processing_times.extend(filtered_df['processing_minutes'].dropna().tolist())
    
    # Add today's live data and collect processing times
    live_records = get_live_data(automation_type)
    
    for record in live_records:
        record_company_code = record['company_code']
        
        # Apply filters (most specific first)
        if bank_account:
            # Filter by specific bank account (overrides everything)
            if not (record_company_code == company_code and 
                    record['housebank'] == housebank and 
                    record['currency'] == currency):
                continue
        else:
            # Apply region filter (if set)
            if region and region in REGION_MAP:
                if record_company_code not in REGION_MAP[region]:
                    continue
            # Apply company code filter (can combine with region)
            if company_code_filter:
                if record_company_code != company_code_filter:
                    continue
        
        total_payments += record['total_payments']
        total_received += record['total_received_eur']  # EUR amounts
        automated_count += record['automated_count']
        assigned_to_account += record['assigned_to_account']
        total_invoices_assigned += record['invoices_assigned']
        total_assigned_value += record['value_assigned_eur']  # EUR amounts
        
        # Collect processing time for average calculation
        if 'processing_minutes' in record:
            processing_times.append(record['processing_minutes'])
    
    # Calculate percentages
    automation_percentage = (automated_count / total_payments * 100) if total_payments > 0 else 0
    assigned_percentage = (assigned_to_account / total_payments * 100) if total_payments > 0 else 0
    value_assigned_percentage = (total_assigned_value / total_received * 100) if total_received > 0 else 0
    
    manual_count = total_payments - automated_count
    unassigned_count = total_payments - assigned_to_account
    unassigned_value = total_received - total_assigned_value
    
    # Calculate average processing time from live data (8:00 AM to file generation)
    # This represents the actual automation processing time
    avg_auto_time_minutes = sum(processing_times) / len(processing_times) if processing_times else 0.0
    avg_manual_time_minutes = 45.0  # Manual processing estimate
    
    return jsonify({
        'period': period,
        'total_payments': int(total_payments),
        'total_received': float(total_received),
        'automation_percentage': round(automation_percentage, 1),
        'automated_count': int(automated_count),
        'manual_count': int(manual_count),
        'unassigned_count': int(unassigned_count),
        'unassigned_value': float(unassigned_value),
        'assigned_percentage': round(assigned_percentage, 1),
        'assigned_count': int(assigned_to_account),
        'total_invoices_assigned': int(total_invoices_assigned),
        'total_assigned_value': float(total_assigned_value),
        'value_assigned_percentage': round(value_assigned_percentage, 1),
        'avg_auto_time_minutes': avg_auto_time_minutes,
        'avg_manual_time_minutes': avg_manual_time_minutes,
    })

@app.route('/api/automation-trend')
def get_automation_trend():
    """
    Get automation trend data for charts.
    
    Data Source: Historical data from consolidated DB ONLY (updated daily)
    Does NOT include today's live data - shows completed days only.
    """
    period = request.args.get('period', 'week')
    bank_account = request.args.get('bank_account', '')
    region = request.args.get('region', '')
    company_code_filter = request.args.get('company_code', '')
    automation_type = request.args.get('automation_type', 'PACO')
    
    # Region to company codes mapping
    REGION_MAP = {
        'Iberia': ['0040', '0041'],
        'France': ['0043'],
        'NDX': ['0019', '0022', '0023', '0024'],
        'UK': ['0014'],
        'BNX': ['0012', '0018'],
        'GerAus': ['0010', '0033'],
        'PLN': ['0023']
    }
    
    # Parse bank account filter
    company_code, housebank, currency = '', '', ''
    if bank_account:
        parts = bank_account.split('|')
        if len(parts) == 3:
            company_code, housebank, currency = parts
    
    # Calculate date range
    # Note: Charts show historical data only (up to yesterday)
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    if period == 'week':
        days = 7
    elif period == 'month':
        days = 30
    elif period == 'quarter':
        days = 90
    else:
        days = 7
    
    start_date = yesterday - timedelta(days=days)
    end_date = yesterday  # Charts show up to yesterday
    
    # Load historical data
    df = load_historical_data()
    
    labels = []
    paco_percentages = []
    fran_percentages = []
    payment_counts = []
    
    if df.empty:
        # Return empty data structure
        return jsonify({
            'labels': labels,
            'paco_percentages': paco_percentages,
            'fran_percentages': fran_percentages,
            'payment_counts': payment_counts
        })
    
    # Convert company_code to string for consistent filtering
    df['company_code'] = df['company_code'].apply(lambda x: str(x).zfill(4) if str(x).isdigit() else str(x))
    
    # Filter by date range
    mask = (df['date'] >= start_date) & (df['date'] <= end_date)
    
    # Apply bank account filter (most specific - overrides everything)
    if bank_account:
        mask &= (df['company_code'] == company_code) & \
                (df['housebank'] == housebank) & \
                (df['currency'] == currency)
    else:
        # Apply region filter (if set)
        if region and region in REGION_MAP:
            mask &= df['company_code'].isin(REGION_MAP[region])
        # Apply company code filter (can combine with region)
        if company_code_filter:
            mask &= (df['company_code'] == company_code_filter)
    
    filtered_paco_df = df[mask]
    
    # Load and filter FRAN data
    fran_df = load_fran_historical_data()
    fran_filtered_df = pd.DataFrame()
    
    if not fran_df.empty:
        # Convert company_code to string for consistent filtering
        fran_df['company_code'] = fran_df['company_code'].apply(lambda x: str(x).zfill(4) if str(x).isdigit() else str(x))
        
        # Apply same filters to FRAN data
        fran_mask = (fran_df['date'] >= start_date) & (fran_df['date'] <= end_date)
        
        if bank_account:
            fran_mask &= (fran_df['company_code'] == company_code) & \
                        (fran_df['housebank'] == housebank) & \
                        (fran_df['currency'] == currency)
        else:
            if region and region in REGION_MAP:
                fran_mask &= fran_df['company_code'].isin(REGION_MAP[region])
            if company_code_filter:
                fran_mask &= (fran_df['company_code'] == company_code_filter)
        
        fran_filtered_df = fran_df[fran_mask]
    
    # Group PACO data by date
    paco_daily = filtered_paco_df.groupby('date').agg({
        'total_payments': 'sum',
        'automated_count': 'sum',
        'assigned_to_account': 'sum',
        'invoices_assigned': 'sum'
    }).reset_index()
    
    # Group FRAN data by date
    fran_daily = pd.DataFrame()
    if not fran_filtered_df.empty:
        fran_daily = fran_filtered_df.groupby('date').agg({
            'total_payments': 'sum',
            'automated_count': 'sum',
            'assigned_to_account': 'sum',
            'invoices_assigned': 'sum'
        }).reset_index()
    
    # Create a union of all dates from both systems
    all_dates = set()
    if not paco_daily.empty:
        all_dates.update(paco_daily['date'].tolist())
    if not fran_daily.empty:
        all_dates.update(fran_daily['date'].tolist())
    
    # Prepare data for all metrics
    paco_automated = []
    paco_customers = []
    paco_invoices = []
    paco_invoices_count = []  # Actual invoice counts for bar chart
    paco_payment_counts = []  # PACO payment counts
    fran_automated = []
    fran_customers = []
    fran_invoices = []
    fran_invoices_count = []  # Actual invoice counts for bar chart
    fran_payment_counts = []  # FRAN payment counts
    
    # Generate labels and data for each date
    for date_obj in sorted(all_dates):
        # Format label
        if period == 'week':
            label = date_obj.strftime('%a %m/%d')
        else:
            label = date_obj.strftime('%m/%d')
        labels.append(label)
        
        # Get PACO data for this date
        paco_row = paco_daily[paco_daily['date'] == date_obj]
        if not paco_row.empty:
            paco_total = paco_row['total_payments'].iloc[0]
            paco_auto = paco_row['automated_count'].iloc[0]
            paco_cust = paco_row['assigned_to_account'].iloc[0]
            paco_inv = paco_row['invoices_assigned'].iloc[0]
            
            paco_automated.append(round((paco_auto / paco_total * 100) if paco_total > 0 else 0, 1))
            paco_customers.append(round((paco_cust / paco_total * 100) if paco_total > 0 else 0, 1))
            paco_invoices.append(round((paco_inv / paco_total * 100) if paco_total > 0 else 0, 1))
            paco_invoices_count.append(int(paco_inv))
            paco_payment_counts.append(int(paco_total))
        else:
            paco_automated.append(0)
            paco_customers.append(0)
            paco_invoices.append(0)
            paco_invoices_count.append(0)
            paco_payment_counts.append(0)
        
        # Get FRAN data for this date
        fran_row = fran_daily[fran_daily['date'] == date_obj] if not fran_daily.empty else pd.DataFrame()
        if not fran_row.empty:
            fran_total = fran_row['total_payments'].iloc[0]
            fran_auto = fran_row['automated_count'].iloc[0]
            fran_cust = fran_row['assigned_to_account'].iloc[0]
            fran_inv = fran_row['invoices_assigned'].iloc[0]
            
            fran_automated.append(round((fran_auto / fran_total * 100) if fran_total > 0 else 0, 1))
            fran_customers.append(round((fran_cust / fran_total * 100) if fran_total > 0 else 0, 1))
            fran_invoices.append(round((fran_inv / fran_total * 100) if fran_total > 0 else 0, 1))
            fran_invoices_count.append(int(fran_inv))
            fran_payment_counts.append(int(fran_total))
        else:
            fran_automated.append(0)
            fran_customers.append(0)
            fran_invoices.append(0)
            fran_invoices_count.append(0)
            fran_payment_counts.append(0)
    
    # Note: payment_counts kept for backward compatibility but deprecated
    # Use paco_payment_counts and fran_payment_counts instead
    payment_counts = paco_payment_counts  # Use PACO as reference since they're the same payments
    
    return jsonify({
        'labels': labels,
        'paco_percentages': paco_automated,  # Legacy field for backward compatibility
        'fran_percentages': fran_automated,  # Legacy field for backward compatibility
        'paco_automated': paco_automated,
        'paco_customers': paco_customers,
        'paco_invoices': paco_invoices,
        'paco_invoices_count': paco_invoices_count,
        'paco_payment_counts': paco_payment_counts,
        'fran_automated': fran_automated,
        'fran_customers': fran_customers,
        'fran_invoices': fran_invoices,
        'fran_invoices_count': fran_invoices_count,
        'fran_payment_counts': fran_payment_counts,
        'payment_counts': payment_counts  # Deprecated - use paco_payment_counts/fran_payment_counts
    })

@app.route('/api/company-status')
def get_company_status():
    """
    Get real-time processing status for each bank account configuration.
    
    Data Source: TODAY's live data ONLY (from raw data or processed output)
    - Before 8:00 AM: Shows "Awaiting Today" with historical counts
    - 8:00 AM - Processing: Shows raw data counts (Not Started)
    - During Processing: Shows live progress from output files (In Process)
    - After Processing: Shows completion status (Done)
    
    Auto-refreshes every 5 minutes on dashboard.
    Always displays all known bank account configurations.
    """
    automation_type = request.args.get('automation_type', 'PACO')
    
    # Get all unique bank account configurations from historical data
    df = load_historical_data()
    bank_accounts = {}
    
    if not df.empty:
        # Get most recent data for each bank account from historical DB
        for _, row in df.sort_values('date', ascending=False).iterrows():
            # Keep company_code with leading zeros (e.g., 0010)
            company_code = str(row['company_code']).zfill(4) if str(row['company_code']).isdigit() else str(row['company_code'])
            housebank = str(row['housebank'])
            currency = str(row['currency'])
            key = (company_code, housebank, currency)
            if key not in bank_accounts:
                bank_accounts[key] = {
                    'company_code': company_code,
                    'housebank': housebank,
                    'currency': currency,
                    'total_payments': int(row['total_payments']),
                    'automated_count': int(row['automated_count']),
                    'date': row['date'],
                    'is_live': False
                }
    
    # Get live data from today and override historical data if available
    live_records = get_live_data(automation_type)
    for record in live_records:
        key = (record['company_code'], record['housebank'], record['currency'])
        is_raw = record.get('is_raw', False)
        bank_accounts[key] = {
            'company_code': record['company_code'],
            'housebank': record['housebank'],
            'currency': record['currency'],
            'total_payments': record['total_payments'],
            'automated_count': record['automated_count'],
            'assigned_to_account': record.get('assigned_to_account', 0),
            'invoices_assigned': record.get('invoices_assigned', 0),
            'total_received': record.get('total_received', 0),
            'total_received_eur': record.get('total_received_eur', 0),
            'value_assigned': record.get('value_assigned', 0),
            'value_assigned_eur': record.get('value_assigned_eur', 0),
            'file_timestamp': record['file_timestamp'],
            'is_live': True,
            'is_raw': is_raw
        }
    
    # Build status list
    bank_account_status_list = []
    
    for (cc, hb, cur), data in bank_accounts.items():
        company_code = data['company_code']
        housebank = data['housebank']
        currency = data['currency']
        total_payments = data['total_payments']
        automated_count = data['automated_count']
        assigned_to_account = data.get('assigned_to_account', 0)
        invoices_assigned = data.get('invoices_assigned', 0)
        total_received = data.get('total_received', 0)
        total_received_eur = data.get('total_received_eur', 0)
        value_assigned = data.get('value_assigned', 0)
        value_assigned_eur = data.get('value_assigned_eur', 0)
        is_live = data.get('is_live', False)
        is_raw = data.get('is_raw', False)
        
        # Calculate status - simplified: file exists = Done, otherwise Not Started
        if not is_live:
            # Historical data - show as "Awaiting Today"
            status = 'Awaiting Today'
            percentage = 0
            value_percentage = 0
            start_time = None
            end_time = None
        elif is_raw:
            # Raw data (not processed yet) - show as "Not Started"
            status = 'Not Started'
            percentage = 0
            value_percentage = 0
            start_time = datetime.combine(date.today(), datetime.strptime('08:00', '%H:%M').time())
            end_time = None
        else:
            # Processed data exists - show as "Done"
            status = 'Done'
            percentage = (automated_count / total_payments * 100) if total_payments > 0 else 0
            value_percentage = (value_assigned / total_received * 100) if total_received > 0 else 0
            
            # Get start and end times
            file_timestamp = data['file_timestamp']
            start_time = datetime.combine(file_timestamp.date(), datetime.strptime('08:00', '%H:%M').time())
            end_time = file_timestamp
        
        bank_account_status_list.append({
            'bank_account': f"{company_code}_{housebank}_{currency}",
            'company_code': company_code,
            'housebank': housebank,
            'currency': currency,
            'status': status,
            'matched_count': automated_count if is_live and not is_raw else 0,
            'matched_percentage': round(percentage, 1),
            'customers_assigned': assigned_to_account if is_live and not is_raw else 0,
            'invoices_assigned': invoices_assigned if is_live and not is_raw else 0,
            'total': total_payments if is_live else 0,  # Show 0 when "Awaiting Today"
            'total_received': round(total_received, 2) if is_live and not is_raw else 0,
            'total_received_eur': round(total_received_eur, 2) if is_live and not is_raw else 0,
            'value_assigned': round(value_assigned, 2) if is_live and not is_raw else 0,
            'value_assigned_eur': round(value_assigned_eur, 2) if is_live and not is_raw else 0,
            'value_assigned_percentage': round(value_percentage, 1),
            'start_time': start_time.isoformat() if start_time else None,
            'end_time': end_time.isoformat() if end_time else None,
            'is_live': is_live
        })
    
    # Sort by company code
    bank_account_status_list.sort(key=lambda x: (x['company_code'], x['housebank'], x['currency']))
    
    return jsonify({
        'company_statuses': bank_account_status_list
    })

@app.route('/api/recent-transactions')
def get_recent_transactions():
    """
    Get recent transactions from today's processing.
    
    Data Source: TODAY's live data ONLY (from processed output files)
    Shows last 10 transactions across all bank accounts.
    Auto-refreshes every 5 minutes on dashboard.
    """
    automation_type = request.args.get('automation_type', 'PACO')
    
    # Get live data
    live_records = get_live_data(automation_type)
    
    # Collect all transactions
    all_transactions = []
    for record in live_records:
        all_transactions.extend(record['transactions'])
    
    # Sort by most recent and limit to 10
    all_transactions = sorted(all_transactions, key=lambda x: x.get('payment_date', ''), reverse=True)[:10]
    
    return jsonify({
        'transactions': all_transactions
    })

@app.route('/api/filter-options')
def get_filter_options():
    """Get unique bank account configurations for filters"""
    bank_accounts = set()
    
    # Get from historical data
    df = load_historical_data()
    if not df.empty:
        for _, row in df.iterrows():
            # Keep company_code with leading zeros (e.g., 0010)
            company_code = str(row['company_code']).zfill(4) if str(row['company_code']).isdigit() else str(row['company_code'])
            bank_account = (company_code, str(row['housebank']), str(row['currency']))
            bank_accounts.add(bank_account)
    
    # Get from live data
    live_records = get_live_data('PACO')
    for record in live_records:
        bank_account = (record['company_code'], record['housebank'], record['currency'])
        bank_accounts.add(bank_account)
    
    # Format for display - sort by converting to strings
    bank_accounts_list = [
        {
            'value': f"{cc}|{hb}|{cur}",
            'label': f"{cc} - {hb} - {cur}"
        }
        for cc, hb, cur in sorted(bank_accounts, key=lambda x: (str(x[0]), str(x[1]), str(x[2])))
    ]
    
    return jsonify({
        'bank_accounts': bank_accounts_list
    })

@app.route('/api/customer-exceptions', methods=['GET'])
def get_customer_exceptions():
    """
    Get all customer exceptions with optional filters.
    Query params: company_code, housebank, currency, business_partner, partner_key, partner_ref
    """
    exceptions = load_customer_exceptions()

    # Apply filters
    company_code = request.args.get('company_code', '')
    housebank = request.args.get('housebank', '')
    currency = request.args.get('currency', '')
    business_partner = request.args.get('business_partner', '')
    partner_key = request.args.get('partner_key', '')
    partner_ref = request.args.get('partner_ref', '')

    filtered_exceptions = exceptions

    if company_code:
        filtered_exceptions = [e for e in filtered_exceptions if e.get('company_code', '').lower() == company_code.lower()]
    if housebank:
        filtered_exceptions = [e for e in filtered_exceptions if e.get('housebank', '').lower() == housebank.lower()]
    if currency:
        filtered_exceptions = [e for e in filtered_exceptions if e.get('currency', '').lower() == currency.lower()]
    if business_partner:
        filtered_exceptions = [e for e in filtered_exceptions if business_partner.lower() in e.get('business_partner', '').lower()]
    if partner_key:
        filtered_exceptions = [e for e in filtered_exceptions if partner_key.lower() in e.get('partner_key', '').lower()]
    if partner_ref:
        filtered_exceptions = [e for e in filtered_exceptions if partner_ref.lower() in e.get('partner_ref', '').lower()]

    return jsonify({
        'exceptions': filtered_exceptions,
        'total': len(filtered_exceptions)
    })

@app.route('/api/customer-exceptions', methods=['POST'])
def create_customer_exception():
    """Create a new customer exception"""
    data = request.get_json()

    # Validate required fields
    required_fields = ['company_code', 'housebank', 'currency', 'business_partner', 'exception_type']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'Missing required field: {field}'}), 400

    # Validate exception_type
    if data['exception_type'] not in ['included', 'excluded']:
        return jsonify({'error': 'Invalid exception_type. Must be "included" or "excluded"'}), 400

    exceptions = load_customer_exceptions()

    # Generate new ID
    max_id = max([e.get('id', 0) for e in exceptions], default=0)
    new_exception = {
        'id': max_id + 1,
        'company_code': data['company_code'],
        'housebank': data['housebank'],
        'currency': data['currency'],
        'business_partner': data['business_partner'],
        'partner_key': data.get('partner_key', ''),
        'partner_ref': data.get('partner_ref', ''),
        'exception_type': data['exception_type'],
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }

    exceptions.append(new_exception)

    if save_customer_exceptions(exceptions):
        return jsonify(new_exception), 201
    else:
        return jsonify({'error': 'Failed to save exception'}), 500

@app.route('/api/customer-exceptions/<int:exception_id>', methods=['PUT'])
def update_customer_exception(exception_id):
    """Update an existing customer exception"""
    data = request.get_json()
    exceptions = load_customer_exceptions()

    # Find exception by ID
    exception_index = None
    for i, e in enumerate(exceptions):
        if e.get('id') == exception_id:
            exception_index = i
            break

    if exception_index is None:
        return jsonify({'error': 'Exception not found'}), 404

    # Validate exception_type if provided
    if 'exception_type' in data and data['exception_type'] not in ['included', 'excluded']:
        return jsonify({'error': 'Invalid exception_type. Must be "included" or "excluded"'}), 400

    # Update exception
    exception = exceptions[exception_index]
    exception['company_code'] = data.get('company_code', exception['company_code'])
    exception['housebank'] = data.get('housebank', exception['housebank'])
    exception['currency'] = data.get('currency', exception['currency'])
    exception['business_partner'] = data.get('business_partner', exception['business_partner'])
    exception['partner_key'] = data.get('partner_key', exception.get('partner_key', ''))
    exception['partner_ref'] = data.get('partner_ref', exception.get('partner_ref', ''))
    exception['exception_type'] = data.get('exception_type', exception['exception_type'])
    exception['updated_at'] = datetime.now().isoformat()

    exceptions[exception_index] = exception

    if save_customer_exceptions(exceptions):
        return jsonify(exception)
    else:
        return jsonify({'error': 'Failed to update exception'}), 500

@app.route('/api/customer-exceptions/<int:exception_id>', methods=['DELETE'])
def delete_customer_exception(exception_id):
    """Delete a customer exception"""
    exceptions = load_customer_exceptions()

    # Find and remove exception
    exception_index = None
    for i, e in enumerate(exceptions):
        if e.get('id') == exception_id:
            exception_index = i
            break

    if exception_index is None:
        return jsonify({'error': 'Exception not found'}), 404

    deleted_exception = exceptions.pop(exception_index)

    if save_customer_exceptions(exceptions):
        return jsonify({'message': 'Exception deleted', 'exception': deleted_exception})
    else:
        return jsonify({'error': 'Failed to delete exception'}), 500

@app.route('/api/customer-exceptions/filter-options')
def get_exception_filter_options():
    """Get unique values for filter dropdowns"""
    exceptions = load_customer_exceptions()

    # Get unique values from historical data and live data
    df = load_historical_data()
    live_records = get_live_data('PACO')

    company_codes = set()
    housebanks = set()
    currencies = set()

    # From historical data
    if not df.empty:
        df['company_code'] = df['company_code'].apply(lambda x: str(x).zfill(4) if str(x).isdigit() else str(x))
        company_codes.update(df['company_code'].unique().tolist())
        housebanks.update(df['housebank'].unique().tolist())
        currencies.update(df['currency'].unique().tolist())

    # From live data
    for record in live_records:
        company_codes.add(record['company_code'])
        housebanks.add(record['housebank'])
        currencies.add(record['currency'])

    # From existing exceptions
    for exc in exceptions:
        if exc.get('company_code'):
            company_codes.add(exc['company_code'])
        if exc.get('housebank'):
            housebanks.add(exc['housebank'])
        if exc.get('currency'):
            currencies.add(exc['currency'])

    return jsonify({
        'company_codes': sorted(list(company_codes)),
        'housebanks': sorted(list(housebanks)),
        'currencies': sorted(list(currencies))
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'CashWeb',
        'data_sources': {
            'historical_db': os.path.exists(CONSOLIDATED_DB_PATH),
            'paco_network': os.path.exists(PACO_NETWORK_PATH)
        }
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
