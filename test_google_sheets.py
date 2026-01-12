#!/usr/bin/env python3
"""
Test Google Sheets integration
"""
import sys
import os
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.google_sheets import get_google_sheet_data

def test_google_sheets():
    print("Testing Google Sheets integration...")
    
    try:
        leads = get_google_sheet_data()
        print(f"Found {len(leads)} leads in Google Sheet:")
        
        for i, lead in enumerate(leads[:5]):  # Show first 5 leads
            print(f"{i+1}. {lead.get('name', 'N/A')} - {lead.get('phone', 'N/A')} - {lead.get('email', 'N/A')}")
        
        if len(leads) > 5:
            print(f"... and {len(leads) - 5} more leads")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_google_sheets()