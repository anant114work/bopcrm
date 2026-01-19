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

from leads.models import Lead
from django.utils import timezone

def sync_16th_dec_leads():
    """Manually sync the missing 16th December leads"""
    
    print("Syncing missing 16th December leads...")
    
    # Missing leads from 16th Dec (from your Google Sheets data)
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
    
    synced_count = 0
    duplicate_count = 0
    
    for lead_data in missing_leads:
        try:
            phone = lead_data['phone']
            name = lead_data['name']
            
            # Check if lead already exists
            existing_lead = Lead.objects.filter(phone_number__icontains=phone[-4:]).first()
            if existing_lead:
                print(f"  DUPLICATE: {name} ({phone}) - Already exists")
                duplicate_count += 1
                continue
            
            # Send to webhook
            webhook_data = {
                'name': name,
                'phone': phone,
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
                print(f"  SYNCED: {name} ({phone}) - {lead_data['timestamp']}")
                synced_count += 1
            else:
                print(f"  FAILED: {name} ({phone}) - Status: {response.status_code}")
                
        except Exception as e:
            print(f"  ERROR: {name} - {str(e)}")
    
    print(f"\nSync complete:")
    print(f"  - Synced: {synced_count} leads")
    print(f"  - Duplicates: {duplicate_count} leads")

if __name__ == "__main__":
    sync_16th_dec_leads()