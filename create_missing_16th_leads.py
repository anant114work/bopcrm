#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import django
import sys
import requests

# Add the project directory to the Python path
sys.path.append('d:\\AI-proto\\CRM\\drip')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

def create_missing_16th_leads():
    """Create the missing 16th December leads"""
    
    print("Creating missing 16th December leads...")
    
    # The 5 missing leads from Google Sheets
    missing_leads = [
        {
            'name': 'S K GUPTA',
            'phone': '8800550542',
            'email': 'shaileshg111@gmail.com',
            'timestamp': '16/12/2024 10:19:20'
        },
        {
            'name': 'Adesh',
            'phone': '9311520711',
            'email': '',
            'timestamp': '16/12/2024 12:53:33'
        },
        {
            'name': 'Brijesh gautam',
            'phone': '9810359853',
            'email': '',
            'timestamp': '16/12/2024 13:10:59'
        },
        {
            'name': 'Permod seth',
            'phone': '9810199279',
            'email': '',
            'timestamp': '16/12/2024 13:34:45'
        },
        {
            'name': 'Arun Kumar jain',
            'phone': '9310663373',
            'email': 'arunjain1951@gmail.com',
            'timestamp': '16/12/2024 13:57:38'
        }
    ]
    
    created_count = 0
    
    for lead_data in missing_leads:
        try:
            # Send to webhook to create lead properly
            webhook_data = {
                'name': lead_data['name'],
                'phone': lead_data['phone'],
                'email': lead_data['email'],
                'unit_size': '',
                'project_name': 'AU Aspire Leisure Valley',
                'ip': '192.168.1.1',
                'timestamp': lead_data['timestamp']
            }
            
            response = requests.post(
                'http://localhost:8000/google-sheets-webhook/',
                json=webhook_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success') and not result.get('duplicate'):
                    print(f"  CREATED: {lead_data['name']} ({lead_data['phone']}) - {lead_data['timestamp']}")
                    created_count += 1
                else:
                    print(f"  DUPLICATE: {lead_data['name']} ({lead_data['phone']}) - Already exists")
            else:
                print(f"  FAILED: {lead_data['name']} ({lead_data['phone']}) - Status: {response.status_code}")
                
        except Exception as e:
            print(f"  ERROR: {lead_data['name']} - {str(e)}")
    
    print(f"\nCreation complete: {created_count} leads created")

if __name__ == "__main__":
    create_missing_16th_leads()