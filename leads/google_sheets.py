import requests
import json
import re

# Default Google Sheets configuration
DEFAULT_SPREADSHEET_ID = '1tBO3sEET72uIJbdK2hixCCq4IicAv0eJxScWrnHzqMM'
DEFAULT_SHEET_NAME = 'Sheet1'

def extract_sheet_id(url):
    """Extract spreadsheet ID from Google Sheets URL"""
    match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', url)
    return match.group(1) if match else None

def get_google_sheet_data(sheet_url=None, sheet_name=None):
    """Get data from Google Sheets using CSV export"""
    try:
        # Get sheet configuration
        if sheet_url:
            spreadsheet_id = extract_sheet_id(sheet_url)
            if not spreadsheet_id:
                raise ValueError('Invalid Google Sheets URL')
        else:
            spreadsheet_id = DEFAULT_SPREADSHEET_ID
            
        # Use Google Sheets CSV export URL
        csv_url = f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv&gid=0'
        response = requests.get(csv_url)
        
        if response.status_code == 200:
            import csv
            import io
            
            # Parse CSV data
            csv_data = csv.DictReader(io.StringIO(response.text))
            leads = []
            
            for row in csv_data:
                # Skip header or empty rows
                if not row.get('Name') or row.get('Name') == 'Name':
                    continue
                    
                leads.append({
                    'name': row.get('Name', ''),
                    'phone': row.get('Phone', ''),
                    'email': row.get('Email', ''),
                    'unit_size': row.get('Unit Size', ''),
                    'timestamp': row.get('Date & Time', ''),
                    'project_name': row.get('Project Name', 'SPJ VEDATAM, SEC 14, GURGAON')
                })
            
            return leads
        else:
            print(f"Failed to fetch Google Sheet: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"Error fetching Google Sheet data: {e}")
        return []

def add_lead_to_sheet(lead):
    """DISABLED: No longer exports data to external sheets"""
    # Export functionality disabled for security
    return True

def sync_all_leads_to_sheet(leads):
    """DISABLED: No longer exports data to external sheets"""
    # Export functionality disabled for security
    return 0