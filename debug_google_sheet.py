#!/usr/bin/env python
import os
import sys
import django
import requests
import csv
import io
import re

# Setup Django
sys.path.append('d:\\AI-proto\\CRM\\drip')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.integration_models import GoogleSheetsConfig

def debug_google_sheet():
    print("Debugging Google Sheets...")
    
    configs = GoogleSheetsConfig.objects.filter(is_active=True)
    
    for config in configs:
        print(f"\nTesting: {config.name}")
        print(f"URL: {config.sheet_url}")
        
        # Extract sheet ID
        match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', config.sheet_url)
        if not match:
            print("ERROR: Invalid sheet URL")
            continue
            
        sheet_id = match.group(1)
        print(f"Sheet ID: {sheet_id}")
        
        # Try CSV export
        csv_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0'
        print(f"CSV URL: {csv_url}")
        
        try:
            response = requests.get(csv_url)
            print(f"Response Status: {response.status_code}")
            
            if response.status_code == 200:
                # Handle encoding properly
                response.encoding = 'utf-8'
                print("First 500 characters of response:")
                try:
                    print(repr(response.text[:500]))
                except:
                    print("[Content contains special characters]")
                    print(f"Content length: {len(response.text)}")
                print("\n" + "="*50)
                
                # Parse CSV with proper encoding
                csv_data = csv.DictReader(io.StringIO(response.text, newline=''))
                rows = list(csv_data)
                print(f"Total rows: {len(rows)}")
                
                if rows:
                    print("Column headers:", list(rows[0].keys()))
                    print("First 3 rows:")
                    for i, row in enumerate(rows[:3]):
                        print(f"Row {i+1}: {dict(row)}")
                else:
                    print("No data rows found")
            else:
                print(f"Failed to access sheet: {response.status_code}")
                print(response.text[:200])
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    debug_google_sheet()