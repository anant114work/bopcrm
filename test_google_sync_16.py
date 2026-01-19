#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import django
import sys
import requests
import json
from datetime import datetime

# Add the project directory to the Python path
sys.path.append('d:\\AI-proto\\CRM\\drip')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import Lead
from django.utils import timezone

def test_google_sheets_webhook():
    """Test the Google Sheets webhook with sample data for 16th Dec"""
    
    print("Testing Google Sheets webhook...")
    
    # Test data for 16th December
    test_data = {
        'name': 'Test Lead 16th Dec',
        'phone': '9999999916',
        'email': 'test16@example.com',
        'unit_size': '3 BHK',
        'project_name': 'AU Aspire Test',
        'ip': '192.168.1.1',
        'timestamp': '16/12/2024 10:30:00'
    }
    
    try:
        # Test the webhook endpoint
        webhook_url = 'http://localhost:8000/google-sheets-webhook/'
        
        print(f"Sending test data to: {webhook_url}")
        print(f"Test data: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(
            webhook_url,
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook test successful!")
            
            # Check if lead was created
            lead = Lead.objects.filter(phone_number='9999999916').first()
            if lead:
                print(f"✅ Lead created: {lead.full_name} - {lead.created_time}")
            else:
                print("❌ Lead not found in database")
        else:
            print(f"❌ Webhook test failed: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - Django server not running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def check_google_sheets_config():
    """Check Google Sheets configuration"""
    
    print("\nChecking Google Sheets configuration...")
    
    from leads.models import GoogleSheet
    
    sheets = GoogleSheet.objects.all()
    print(f"Configured Google Sheets: {sheets.count()}")
    
    for sheet in sheets:
        print(f"  - {sheet.name}: {sheet.sheet_url}")

def manual_create_test_lead():
    """Manually create a test Google Sheets lead for 16th Dec"""
    
    print("\nManually creating test Google Sheets lead...")
    
    try:
        # Create a test lead with today's date
        lead = Lead.objects.create(
            lead_id=f"GS_TEST_{timezone.now().strftime('%Y%m%d_%H%M%S')}_9916",
            full_name="Manual Test Lead 16th Dec",
            phone_number="+919999999916",
            email="manual16@example.com",
            configuration="2 BHK",
            form_name="Google Sheets - Manual Test",
            source='Google Sheets',
            created_time=timezone.now(),
            extra_fields={
                'project_name': 'Manual Test Project',
                'test_lead': True
            }
        )
        
        print(f"✅ Manual test lead created: {lead.full_name} - ID: {lead.lead_id}")
        return lead
        
    except Exception as e:
        print(f"❌ Error creating manual lead: {str(e)}")
        return None

if __name__ == "__main__":
    print("=== Google Sheets Sync Diagnosis for 16th Dec ===\n")
    
    # Check configuration
    check_google_sheets_config()
    
    # Test webhook
    test_google_sheets_webhook()
    
    # Create manual test lead
    manual_create_test_lead()
    
    print("\n=== Diagnosis Complete ===")