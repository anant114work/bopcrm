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
from django.utils import timezone
from datetime import datetime, timedelta

def check_leads_for_16():
    """Check leads for 16th December 2024"""
    
    # Check for today (16th)
    today = timezone.now().date()
    print(f"Checking leads for {today}")
    
    # Get leads created today
    today_leads = Lead.objects.filter(created_time__date=today)
    print(f"Total leads created today: {today_leads.count()}")
    
    # Check Google Sheets leads specifically
    google_leads_today = today_leads.filter(source='Google Sheets')
    print(f"Google Sheets leads today: {google_leads_today.count()}")
    
    # Check all Google Sheets leads
    all_google_leads = Lead.objects.filter(source='Google Sheets').order_by('-created_time')
    print(f"Total Google Sheets leads: {all_google_leads.count()}")
    
    # Show recent Google leads
    print("\nRecent Google Sheets leads:")
    for lead in all_google_leads[:10]:
        print(f"  - {lead.full_name} ({lead.phone_number}) - {lead.created_time.strftime('%d/%m/%Y %H:%M')}")
    
    # Check for leads with GS_ prefix
    gs_leads = Lead.objects.filter(lead_id__startswith='GS_').order_by('-created_time')
    print(f"\nLeads with GS_ prefix: {gs_leads.count()}")
    
    # Show recent GS leads
    print("\nRecent GS_ leads:")
    for lead in gs_leads[:10]:
        print(f"  - {lead.full_name} ({lead.phone_number}) - {lead.created_time.strftime('%d/%m/%Y %H:%M')} - ID: {lead.lead_id}")
    
    # Check for any leads created in December 16th (any year)
    dec_16_leads = Lead.objects.filter(
        created_time__month=12,
        created_time__day=16
    ).order_by('-created_time')
    print(f"\nAll leads created on December 16th (any year): {dec_16_leads.count()}")
    
    # Show December 16th leads
    print("\nDecember 16th leads:")
    for lead in dec_16_leads[:15]:
        print(f"  - {lead.full_name} ({lead.phone_number}) - {lead.created_time.strftime('%d/%m/%Y %H:%M')} - Source: {lead.source}")

if __name__ == "__main__":
    check_leads_for_16()