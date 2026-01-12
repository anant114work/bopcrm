#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import django
import sys

# Add the project directory to the Python path
sys.path.append('d:\\AI-proto\\CRM\\drip')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import Lead

def find_16th_leads():
    """Find leads for 16th December with any year"""
    
    print("Searching for 16th December leads...")
    
    # Search for the specific names from Google Sheets
    names_to_find = ['S K GUPTA', 'Adesh', 'Brijesh gautam', 'Permod seth', 'Arun Kumar jain']
    phones_to_find = ['8800550542', '9311520711', '9810359853', '9810199279', '9310663373']
    
    print("\nSearching by names:")
    for name in names_to_find:
        leads = Lead.objects.filter(full_name__icontains=name)
        for lead in leads:
            print(f"  - {lead.full_name} ({lead.phone_number}) - {lead.created_time.strftime('%d/%m/%Y %H:%M')} - Source: {lead.source}")
    
    print("\nSearching by phone numbers:")
    for phone in phones_to_find:
        leads = Lead.objects.filter(phone_number__icontains=phone)
        for lead in leads:
            print(f"  - {lead.full_name} ({lead.phone_number}) - {lead.created_time.strftime('%d/%m/%Y %H:%M')} - Source: {lead.source}")
    
    # Check all leads created on 16th December (any year)
    dec_16_leads = Lead.objects.filter(
        created_time__month=12,
        created_time__day=16
    ).order_by('-created_time')
    
    print(f"\nAll leads created on December 16th (any year): {dec_16_leads.count()}")
    for lead in dec_16_leads:
        print(f"  - {lead.full_name} ({lead.phone_number}) - {lead.created_time.strftime('%d/%m/%Y %H:%M')} - Source: {lead.source}")

if __name__ == "__main__":
    find_16th_leads()