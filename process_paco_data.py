"""
PACO Data Processor
Consolidates historical PACO automation data from Excel files into a single database.
Processes all 2025 data except today's files.
"""
import os
import pandas as pd
from datetime import datetime, date, timedelta
from pathlib import Path
import re
from currency_converter import convert_to_eur

# Configuration
NETWORK_PATH = r"\\emea\central\SSC_GROUP\BPA\30_Automations\90_CashOps\02_Posting Cash\03_Output\2025"
LOCAL_DB_PATH = "data/paco_consolidated.xlsx"

def parse_filename(filename):
    """
    Parse filename to extract company_code, housebank, and currency.
    Expected format: CCCC_HHHH_CUR.xlsx (e.g., 0010_1050D_EUR.xlsx)
    """
    # Remove .xlsx extension
    name = filename.replace('.xlsx', '')
    
    # Split by underscore
    parts = name.split('_')
    
    if len(parts) >= 3:
        company_code = parts[0]
        housebank = parts[1]
        currency = '_'.join(parts[2:])  # In case currency has underscores
        return company_code, housebank, currency
    
    return None, None, None

def count_invoices(docnumbers_str):
    """
    Count invoices from DocNumbers column.
    Invoices are separated by semicolon (;)
    Excludes OUTGOING, INCOMING, and other non-invoice values
    """
    if pd.isna(docnumbers_str) or docnumbers_str == '':
        return 0
    
    # Skip OUTGOING, INCOMING and other non-numeric patterns
    docnumbers_str = str(docnumbers_str).strip()
    if docnumbers_str.upper() in ['OUTGOING', 'INCOMING', 'NAN', 'NONE']:
        return 0
    
    # Split by semicolon and count only numeric invoice numbers
    invoices = []
    for inv in docnumbers_str.split(';'):
        inv = inv.strip()
        # Only count if it looks like an invoice number (contains digits)
        if inv and any(c.isdigit() for c in inv):
            # Exclude if it's obviously not an invoice (too short or all letters)
            if len(inv) > 2 and not inv.isalpha():
                invoices.append(inv)
    
    return len(invoices)

def process_excel_file(filepath, processing_date):
    """
    Process a single Excel file and extract metrics.
    Returns a dictionary with aggregated data.
    """
    try:
        # Read Excel file
        df = pd.read_excel(filepath, engine='openpyxl')
        
        # Normalize column names (strip whitespace only, keep original casing for exact matches)
        df.columns = df.columns.str.strip() if hasattr(df.columns, 'str') else df.columns
        
        # Filter out non-string columns (some Excel files have float column names)
        valid_columns = [col for col in df.columns if isinstance(col, str)]
        
        # Parse filename to get bank account configuration
        filename = os.path.basename(filepath)
        company_code, housebank, currency = parse_filename(filename)
        
        if not all([company_code, housebank, currency]):
            print(f"Warning: Could not parse filename: {filename}")
            return None
        
        # Calculate metrics
        total_payments = len(df)
        
        # Total received (sum of Amount column)
        total_received = df['Amount'].sum() if 'Amount' in valid_columns else 0
        
        # Automated count (Match = "Yes" - case-sensitive!)
        automated_count = 0
        if 'Match' in valid_columns:
            # Use case-insensitive matching to handle both "Yes" and "YES"
            automated_count = len(df[df['Match'].str.strip().str.upper() == 'YES'])
        
        # Assigned to account (Business_Partner is filled)
        assigned_to_account = len(df[df['Business_Partner'].notna()]) if 'Business_Partner' in valid_columns else 0
        
        # Invoices assigned (count total invoices from DocNumbers)
        invoices_assigned = 0
        if 'DocNumbers' in valid_columns:
            invoices_assigned = df['DocNumbers'].apply(count_invoices).sum()
        
        # Value assigned (sum of amounts where Match = "Yes")
        value_assigned = 0
        if 'Match' in valid_columns and 'Amount' in valid_columns:
            # Use case-insensitive matching
            value_assigned = df[df['Match'].str.strip().str.upper() == 'YES']['Amount'].sum()
        
        # Get file timestamp
        file_timestamp = datetime.fromtimestamp(os.path.getmtime(filepath))
        
        # Calculate processing time (minutes since 8:00 AM)
        start_of_day = datetime.combine(file_timestamp.date(), datetime.strptime('08:00', '%H:%M').time())
        processing_minutes = int((file_timestamp - start_of_day).total_seconds() / 60)
        
        # Convert amounts to EUR for consistent reporting
        total_received_eur = convert_to_eur(total_received, currency)
        value_assigned_eur = convert_to_eur(value_assigned, currency)
        
        return {
            'date': processing_date,
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
            'processing_minutes': processing_minutes
        }
        
    except Exception as e:
        print(f"Error processing file {filepath}: {str(e)}")
        return None

def scan_and_process(network_path, exclude_today=True):
    """
    Scan network path for all Excel files and process them.
    Returns a list of processed records.
    Note: Since bank payments from yesterday are received today, we exclude both today and yesterday.
    """
    records = []
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    print(f"Scanning network path: {network_path}")
    
    if not os.path.exists(network_path):
        print(f"Error: Network path does not exist: {network_path}")
        return records
    
    # Iterate through YYYYMM folders
    for month_folder in os.listdir(network_path):
        month_path = os.path.join(network_path, month_folder)
        
        if not os.path.isdir(month_path):
            continue
        
        # Check if folder matches YYYYMM format
        if not re.match(r'^\d{6}$', month_folder):
            continue
        
        print(f"Processing month: {month_folder}")
        
        # Iterate through YYYYMMDD folders
        for day_folder in os.listdir(month_path):
            day_path = os.path.join(month_path, day_folder)
            
            if not os.path.isdir(day_path):
                continue
            
            # Check if folder matches YYYYMMDD format
            if not re.match(r'^\d{8}$', day_folder):
                continue
            
            # Parse date from folder name
            try:
                processing_date = datetime.strptime(day_folder, '%Y%m%d').date()
            except ValueError:
                continue
            
            # Skip today and yesterday's data (yesterday is today's live data)
            if exclude_today and (processing_date == today or processing_date == yesterday):
                print(f"Skipping live data: {day_folder}")
                continue
            
            print(f"  Processing day: {day_folder}")
            
            # Process all Excel files in this day folder
            for filename in os.listdir(day_path):
                if filename.endswith('.xlsx') and not filename.startswith('~$'):
                    filepath = os.path.join(day_path, filename)
                    
                    record = process_excel_file(filepath, processing_date)
                    if record:
                        records.append(record)
                        print(f"    Processed: {filename}")
    
    return records

def update_consolidated_database(records, db_path):
    """
    Update consolidated database with new records.
    If database exists, merge with existing data.
    """
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Convert records to DataFrame
    new_df = pd.DataFrame(records)
    
    if new_df.empty:
        print("No records to update.")
        return
    
    # Check if database exists
    if os.path.exists(db_path):
        print(f"Loading existing database: {db_path}")
        existing_df = pd.read_excel(db_path, engine='openpyxl')
        
        # Convert date columns to date objects for comparison
        existing_df['date'] = pd.to_datetime(existing_df['date']).dt.date
        new_df['date'] = pd.to_datetime(new_df['date']).dt.date
        
        # Merge: Remove duplicates based on date + company_code + housebank + currency
        # Keep new records (they are more recent/updated)
        merged_df = pd.concat([existing_df, new_df], ignore_index=True)
        merged_df = merged_df.drop_duplicates(
            subset=['date', 'company_code', 'housebank', 'currency'],
            keep='last'
        )
        
        # Sort by date
        merged_df = merged_df.sort_values('date', ascending=False)
        
        print(f"Merged {len(new_df)} new records with {len(existing_df)} existing records")
        print(f"Total records after merge: {len(merged_df)}")
    else:
        print(f"Creating new database: {db_path}")
        merged_df = new_df.sort_values('date', ascending=False)
    
    # Save to Excel
    merged_df.to_excel(db_path, index=False, engine='openpyxl')
    print(f"Database saved: {db_path}")
    print(f"Total records: {len(merged_df)}")

def main():
    """Main execution function"""
    print("=" * 80)
    print("PACO Data Processor")
    print("=" * 80)
    print(f"Start time: {datetime.now()}")
    print()
    
    # Scan and process Excel files
    records = scan_and_process(NETWORK_PATH, exclude_today=True)
    
    print()
    print(f"Processed {len(records)} files")
    
    # Update consolidated database
    if records:
        update_consolidated_database(records, LOCAL_DB_PATH)
    else:
        print("No records to process. Database not updated.")
    
    print()
    print(f"End time: {datetime.now()}")
    print("=" * 80)

if __name__ == '__main__':
    main()

