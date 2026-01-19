#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import django
import sys
import requests
import json

# Add the project directory to the Python path
sys.path.append('d:\\AI-proto\\CRM\\drip')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import Lead

def test_webhook_integration():
    """Test the Google Sheets to CRM integration"""
    
    print("Testing Google Sheets to CRM integration...")
    
    # Count leads before
    before_count = Lead.objects.count()
    print(f"Leads before test: {before_count}")
    
    # Test data (simulating Google Apps Script)
    test_data = {
        'name': 'Integration Test User',
        'phone': '9999999917',
        'email': 'integration@test.com',
        'unit_size': '2 BHK',
        'project_name': 'AU Aspire Test Integration',
        'ip': '192.168.1.100',
        'timestamp': '16/12/2024 15:30:00'
    }
    
    try:
        # Send to webhook
        response = requests.post(
            'http://localhost:8000/google-sheets-webhook/',
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        # Count leads after
        after_count = Lead.objects.count()
        print(f"Leads after test: {after_count}")
        
        if after_count > before_count:
            print("SUCCESS: Lead created in CRM!")
            
            # Find the new lead
            new_lead = Lead.objects.filter(phone_number='9999999917').first()
            if new_lead:
                print(f"New Lead: {new_lead.full_name} - {new_lead.source} - {new_lead.created_time}")
        else:
            print("FAILED: No new lead created")
            
    except requests.exceptions.ConnectionError:
        print("ERROR: Django server not running on localhost:8000")
        print("Start your Django server with: python manage.py runserver")
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    test_webhook_integration()