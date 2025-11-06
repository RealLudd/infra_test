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
from currency_converter import convert_to_eur

app = Flask(__name__)

# Configuration
CONSOLIDATED_DB_PATH = "data/paco_consolidated.xlsx"
PACO_NETWORK_PATH = r"\\emea\central\SSC_GROUP\BPA\30_Automations\90_CashOps\02_Posting Cash\03_Output\2025"
FRAN_NETWORK_PATH = r"\\emea\central\SSC_GROUP\BPA\30_Automations\90_CashOps\02_Posting Cash\03_Output\2025"  # Update when FRAN path is available
PACO_RAW_DATA_PATH = r"\\emea\central\SSC_GROUP\BPA\30_Automations\90_CashOps\02_Posting Cash\02_RD\02_P\2025"
FRAN_RAW_DATA_PATH = r"\\emea\central\SSC_GROUP\BPA\30_Automations\90_CashOps\02_Posting Cash\02_RD\02_F\2025"  # FRAN raw data path

# Global cache for historical data
historical_data_cache = None
historical_data_timestamp = None

def load_historical_data(force_reload=False):
    """
    Load historical data from consolidated Excel database.
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
            print(f"Error loading historical data: {str(e)}")
            return pd.DataFrame()
    else:
        print(f"Historical database not found: {CONSOLIDATED_DB_PATH}")
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
        automated_count = len(df[df['Match'] == 'YES']) if 'Match' in df.columns else 0
        assigned_to_account = len(df[df['Business_Partner'].notna()]) if 'Business_Partner' in df.columns else 0
        
        invoices_assigned = 0
        if 'Docnumbers' in df.columns:
            invoices_assigned = df['Docnumbers'].apply(count_invoices).sum()
        
        value_assigned = 0
        if 'Match' in df.columns and 'Amount' in df.columns:
            value_assigned = df[df['Match'] == 'YES']['Amount'].sum()
        
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
        print(f"Error processing live file {filepath}: {str(e)}")
        return None

def get_raw_data_counts(automation_type='PACO'):
    """
    Get raw data counts from today's raw data path (before processing starts).
    Returns list of bank account records with total payment counts.
    """
    raw_path = PACO_RAW_DATA_PATH if automation_type == 'PACO' else FRAN_RAW_DATA_PATH
    
    # Get yesterday's date (raw data is from yesterday, received today)
    yesterday = date.today() - timedelta(days=1)
    yesterday_str = yesterday.strftime('%Y%m%d')
    month_str = yesterday.strftime('%Y%m')
    
    # Build path to yesterday's raw data folder
    raw_data_path = os.path.join(raw_path, month_str, yesterday_str)
    
    records = []
    
    if not os.path.exists(raw_data_path):
        print(f"Raw data path does not exist: {raw_data_path}")
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
                
                # Normalize company_code to remove leading zeros (to match historical data format)
                company_code = str(int(company_code))
                
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
                        'automated_count': 0,  # Not processed yet
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
    """
    output_path = PACO_NETWORK_PATH if automation_type == 'PACO' else FRAN_NETWORK_PATH
    
    # Get today's date to monitor current processing
    today = date.today()
    today_str = today.strftime('%Y%m%d')
    month_str = today.strftime('%Y%m')
    
    # Build path to today's processed output folder
    output_folder = os.path.join(output_path, month_str, today_str)
    
    records = []
    
    # First, try to get processed data
    if os.path.exists(output_folder):
        # Process all Excel files in today's output folder
        for filename in os.listdir(output_folder):
            if filename.endswith('.xlsx') and not filename.startswith('~$'):
                filepath = os.path.join(output_folder, filename)
                record = process_live_excel_file(filepath)
                if record:
                    records.append(record)
    
    # If no processed files found, get raw data counts
    if not records:
        print(f"No processed data found in {output_folder}, checking raw data...")
        records = get_raw_data_counts(automation_type)
    
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
    automation_type = request.args.get('automation_type', 'PACO')
    
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
            # Filter by date range and bank account
            mask = (df['date'] >= start_date) & (df['date'] <= end_date)
            if bank_account:
                mask &= (df['company_code'] == company_code) & \
                        (df['housebank'] == housebank) & \
                        (df['currency'] == currency)
            
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
        # Filter by bank account if specified
        if bank_account:
            if not (record['company_code'] == company_code and 
                    record['housebank'] == housebank and 
                    record['currency'] == currency):
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
    automation_type = request.args.get('automation_type', 'PACO')
    
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
    
    # Filter by date range and bank account
    mask = (df['date'] >= start_date) & (df['date'] <= end_date)
    if bank_account:
        mask &= (df['company_code'] == company_code) & \
                (df['housebank'] == housebank) & \
                (df['currency'] == currency)
    
    filtered_df = df[mask]
    
    # Group by date
    daily_groups = filtered_df.groupby('date').agg({
        'total_payments': 'sum',
        'automated_count': 'sum'
    }).reset_index()
    
    # Generate labels and data
    for _, row in daily_groups.iterrows():
        date_obj = row['date']
        total = row['total_payments']
        automated = row['automated_count']
        
        # Format label
        if period == 'week':
            label = date_obj.strftime('%a %m/%d')
        else:
            label = date_obj.strftime('%m/%d')
        
        # Calculate automation percentage (all PACO for now)
        paco_pct = (automated / total * 100) if total > 0 else 0
        
        labels.append(label)
        paco_percentages.append(round(paco_pct, 1))
        fran_percentages.append(0)  # FRAN data not yet available
        payment_counts.append(int(total))
    
    return jsonify({
        'labels': labels,
        'paco_percentages': paco_percentages,
        'fran_percentages': fran_percentages,
        'payment_counts': payment_counts
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
            company_code = str(int(row['company_code']))  # Normalize to string without leading zeros
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
        is_live = data.get('is_live', False)
        is_raw = data.get('is_raw', False)
        
        # Calculate status
        pending = total_payments - automated_count
        processed = automated_count
        
        if not is_live:
            # Historical data - show as "Awaiting Today"
            status = 'Awaiting Today'
            percentage = 0
            start_time = None
            end_time = None
        elif is_raw:
            # Raw data (not processed yet) - show as "Not Started" with all pending
            status = 'Not Started'
            percentage = 0
            start_time = datetime.combine(date.today(), datetime.strptime('08:00', '%H:%M').time())
            end_time = None
            processed = 0
            pending = total_payments
        else:
            # Processed data - calculate real status
            if pending == 0 and total_payments > 0:
                status = 'Done'
            elif processed > 0 and pending > 0:
                status = 'In Process'
            elif processed == 0:
                status = 'Not Started'
            else:
                status = 'In Process'
            
            percentage = (processed / total_payments * 100) if total_payments > 0 else 0
            
            # Get start and end times
            file_timestamp = data['file_timestamp']
            start_time = datetime.combine(file_timestamp.date(), datetime.strptime('08:00', '%H:%M').time())
            end_time = file_timestamp if status == 'Done' else None
        
        bank_account_status_list.append({
            'bank_account': f"{company_code}_{housebank}_{currency}",
            'company_code': company_code,
            'housebank': housebank,
            'currency': currency,
            'status': status,
            'processed': processed if is_live else 0,
            'pending': pending if is_live else total_payments,
            'total': total_payments,
            'percentage': round(percentage, 1),
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
            bank_account = (row['company_code'], row['housebank'], row['currency'])
            bank_accounts.add(bank_account)
    
    # Get from live data
    live_records = get_live_data('PACO')
    for record in live_records:
        bank_account = (record['company_code'], record['housebank'], record['currency'])
        bank_accounts.add(bank_account)
    
    # Format for display
    bank_accounts_list = [
        {
            'value': f"{cc}|{hb}|{cur}",
            'label': f"{cc} - {hb} - {cur}"
        }
        for cc, hb, cur in sorted(bank_accounts)
    ]
    
    return jsonify({
        'bank_accounts': bank_accounts_list
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
