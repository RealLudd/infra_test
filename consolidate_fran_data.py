"""
Consolidate Daily FRAN Data Script
Collects today's FRAN output files and adds them to the consolidated database.
Checks for existing records and replaces them if they already exist.
"""
import os
import pandas as pd
from datetime import datetime, date, timedelta
from currency_converter import convert_to_eur

# Configuration
CONSOLIDATED_DB_PATH = "data/fran_consolidated.xlsx"
FRAN_OUTPUT_PATH = r"\\emea\central\SSC_GROUP\BPA\30_Automations\90_CashOps\02_Posting Cash\03_Output\2025"

def parse_filename(filename):
    """Parse filename to extract company_code, housebank, and currency."""
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

def process_output_file(filepath, data_date):
    """Process a single FRAN output file and extract metrics."""
    try:
        print(f"  Processing: {os.path.basename(filepath)}")
        
        df = pd.read_excel(filepath, engine='openpyxl')
        df.columns = df.columns.str.strip()
        
        filename = os.path.basename(filepath)
        company_code, housebank, currency = parse_filename(filename)
        
        if not all([company_code, housebank, currency]):
            print(f"  WARNING: Could not parse filename: {filename}")
            return None
        
        # Normalize company code (remove leading zeros)
        company_code = str(int(company_code))
        
        # Determine which DocNumbers column to use
        docnumbers_col = None
        if 'DocNumbers' in df.columns:
            docnumbers_col = 'DocNumbers'
        elif 'Docnumbers' in df.columns:
            docnumbers_col = 'Docnumbers'
        
        # Calculate metrics
        total_payments = len(df)
        total_received = df['Amount'].sum() if 'Amount' in df.columns else 0
        
        # Automated count: Match == "Yes" (case insensitive) AND has invoices
        automated_count = 0
        if 'Match' in df.columns and docnumbers_col:
            automated_mask = (df['Match'].str.upper() == 'YES') & (df[docnumbers_col].notna()) & (df[docnumbers_col] != '')
            automated_count = len(df[automated_mask])
        
        assigned_to_account = len(df[df['Business_Partner'].notna()]) if 'Business_Partner' in df.columns else 0
        
        invoices_assigned = 0
        if docnumbers_col:
            invoices_assigned = df[docnumbers_col].apply(count_invoices).sum()
        
        # Value assigned: Amount for rows where Match == "Yes" AND has invoices
        value_assigned = 0
        if 'Match' in df.columns and 'Amount' in df.columns and docnumbers_col:
            value_mask = (df['Match'].str.upper() == 'YES') & (df[docnumbers_col].notna()) & (df[docnumbers_col] != '')
            value_assigned = df[value_mask]['Amount'].sum()
        
        # Convert amounts to EUR
        total_received_eur = convert_to_eur(total_received, currency)
        value_assigned_eur = convert_to_eur(value_assigned, currency)
        
        # Get file timestamp for processing time calculation
        file_timestamp = datetime.fromtimestamp(os.path.getmtime(filepath))
        start_of_day = datetime.combine(file_timestamp.date(), datetime.strptime('08:00', '%H:%M').time())
        processing_minutes = int((file_timestamp - start_of_day).total_seconds() / 60)
        
        # Data date comes from the parent function's target_date - 1 day
        # (Will be set by caller)
        
        record = {
            'date': data_date,
            'company_code': company_code,
            'housebank': housebank,
            'currency': currency,
            'total_payments': total_payments,
            'total_received': total_received,
            'total_received_eur': total_received_eur,
            'automated_count': automated_count,
            'assigned_to_account': assigned_to_account,
            'invoices_assigned': invoices_assigned,
            'value_assigned': value_assigned,
            'value_assigned_eur': value_assigned_eur,
            'file_timestamp': file_timestamp,
            'processing_minutes': processing_minutes
        }
        
        print(f"  OK: {company_code}_{housebank}_{currency}: {total_payments} payments, {automated_count} automated ({(automated_count/total_payments*100):.1f}%)")
        return record
        
    except Exception as e:
        print(f"  ERROR: Error processing {os.path.basename(filepath)}: {str(e)}")
        return None

def consolidate_today_data(target_date=None):
    """
    Consolidate today's FRAN data into the database.
    If target_date is provided, consolidate that date instead.
    """
    if target_date is None:
        target_date = date.today()
    
    target_str = target_date.strftime('%Y%m%d')
    month_str = target_date.strftime('%Y%m')
    
    print(f"\n{'='*60}")
    print(f"FRAN Data Consolidation - {target_date.strftime('%Y-%m-%d')}")
    print(f"{'='*60}\n")
    
    # Build path to today's output folder (FRAN subfolder)
    output_folder = os.path.join(FRAN_OUTPUT_PATH, month_str, target_str, "FRAN")
    
    if not os.path.exists(output_folder):
        print(f"ERROR: FRAN output folder does not exist:")
        print(f"   {output_folder}")
        print(f"\nPlease ensure the FRAN automation has completed for {target_date.strftime('%Y-%m-%d')}.")
        return False
    
    print(f"Reading from: {output_folder}\n")
    
    # Process all Excel files
    new_records = []
    excel_files = [f for f in os.listdir(output_folder) 
                   if f.endswith('.xlsx') and not f.startswith('~$')]
    
    if not excel_files:
        print(f"ERROR: No Excel files found in the FRAN output folder.")
        return False
    
    print(f"Found {len(excel_files)} FRAN files to process:\n")
    
    # Calculate data date (yesterday's payments processed today)
    data_date = target_date - timedelta(days=1)
    
    for filename in excel_files:
        filepath = os.path.join(output_folder, filename)
        record = process_output_file(filepath, data_date)
        if record:
            new_records.append(record)
    
    if not new_records:
        print(f"\nERROR: No records were successfully processed.")
        return False
    
    print(f"\n{'='*60}")
    print(f"Processed {len(new_records)} FRAN bank accounts successfully")
    print(f"{'='*60}\n")
    
    # Load existing database
    print(f"Loading FRAN consolidated database: {CONSOLIDATED_DB_PATH}")
    
    if os.path.exists(CONSOLIDATED_DB_PATH):
        existing_df = pd.read_excel(CONSOLIDATED_DB_PATH, engine='openpyxl')
        existing_df['date'] = pd.to_datetime(existing_df['date']).dt.date
        print(f"   Current records: {len(existing_df)}")
        
        # Remove existing records for this date (to replace them)
        # data_date was already calculated above
        records_before = len(existing_df)
        existing_df = existing_df[existing_df['date'] != data_date]
        records_removed = records_before - len(existing_df)
        
        if records_removed > 0:
            print(f"   WARNING: Removed {records_removed} existing FRAN records for {data_date.strftime('%Y-%m-%d')} (will be replaced)")
    else:
        print(f"   Creating new FRAN database file")
        existing_df = pd.DataFrame()
        records_removed = 0
    
    # Add new records
    new_df = pd.DataFrame(new_records)
    combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    combined_df = combined_df.sort_values(['date', 'company_code', 'housebank', 'currency'])
    
    # Save to Excel
    print(f"\nSaving to database...")
    combined_df.to_excel(CONSOLIDATED_DB_PATH, index=False, engine='openpyxl')
    
    print(f"\n{'='*60}")
    print(f"SUCCESS: FRAN CONSOLIDATION COMPLETE")
    print(f"{'='*60}")
    print(f"   Records added: {len(new_records)}")
    print(f"   Records removed: {records_removed}")
    print(f"   Total records: {len(combined_df)}")
    print(f"   Database: {CONSOLIDATED_DB_PATH}")
    print(f"{'='*60}\n")
    
    return True

if __name__ == '__main__':
    import sys
    
    # Check if a specific date was provided
    if len(sys.argv) > 1:
        try:
            target_date = datetime.strptime(sys.argv[1], '%Y-%m-%d').date()
            print(f"Using target date: {target_date.strftime('%Y-%m-%d')}")
        except ValueError:
            print(f"Invalid date format. Use YYYY-MM-DD")
            sys.exit(1)
    else:
        target_date = date.today()
    
    success = consolidate_today_data(target_date)
    
    if success:
        print("Press any key to exit...")
        input()
        sys.exit(0)
    else:
        print("\nConsolidation failed. Press any key to exit...")
        input()
        sys.exit(1)

