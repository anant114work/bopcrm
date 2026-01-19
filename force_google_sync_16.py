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
from leads.google_sheets import get_google_sheet_data
from django.utils import timezone
from datetime import datetime
import pytz

def force_sync_google_sheets():
    """Force sync Google Sheets data for 16th Dec"""
    
    print("Force syncing Google Sheets data...")
    
    # Get the main Google Sheet ID (you can change this to your actual sheet)
    sheet_url = "https://docs.google.com/spreadsheets/d/1jFlAPGcgZlllJgNSFLL_qVKSlAOYf2iEp6vmAp9p26Q/edit"
    
    try:
        # Get data from Google Sheets
        leads_data = get_google_sheet_data(sheet_url)
        
        print(f"Found {len(leads_data)} leads in Google Sheets")
        
        # Filter for 16th December leads
        today_leads = []
        for lead_data in leads_data:
            timestamp = lead_data.get('timestamp', '')
            if '16/12' in timestamp or '16-12' in timestamp:
                today_leads.append(lead_data)
        
        print(f"Found {len(today_leads)} leads for 16th December")
        
        # Show the leads found
        for lead in today_leads:
            print(f"  - {lead.get('name')} ({lead.get('phone')}) - {lead.get('timestamp')}")
        
        # Sync each lead
        synced_count = 0
        duplicate_count = 0
        
        for lead_data in today_leads:
            try:
                name = lead_data.get('name', '').strip()
                phone = lead_data.get('phone', '').strip()
                email = lead_data.get('email', '').strip()
                
                if not name or not phone:
                    continue
                
                # Normalize phone number
                normalized_phone = phone.replace('+91', '').replace('+', '').replace(' ', '').replace('-', '')
                if len(normalized_phone) == 10:
                    normalized_phone = f"+91{normalized_phone}"
                elif len(normalized_phone) == 12 and normalized_phone.startswith('91'):
                    normalized_phone = f"+{normalized_phone}"
                
                # Check for duplicates
                phone_variants = [
                    phone,
                    normalized_phone,
                    normalized_phone.replace('+91', ''),
                    normalized_phone.replace('+', '')
                ]
                
                existing_lead = Lead.objects.filter(phone_number__in=phone_variants).first()
                if existing_lead:
                    print(f"  DUPLICATE: {name} ({phone}) - Already exists")
                    duplicate_count += 1
                    continue
                
                # Parse timestamp
                timestamp = lead_data.get('timestamp', '')
                created_time = timezone.now()
                
                if timestamp:
                    try:
                        if '/' in timestamp and ':' in timestamp:
                            dt = datetime.strptime(timestamp, '%d/%m/%Y %H:%M:%S')
                            ist = pytz.timezone('Asia/Kolkata')
                            created_time = ist.localize(dt)
                        elif '/' in timestamp:
                            dt = datetime.strptime(timestamp, '%d/%m/%Y')
                            ist = pytz.timezone('Asia/Kolkata')
                            created_time = ist.localize(dt)
                    except:
                        pass
                
                # Create lead
                lead_id = f"GS_FORCE_{timezone.now().strftime('%Y%m%d_%H%M%S')}_{phone[-4:]}"
                
                lead = Lead.objects.create(
                    lead_id=lead_id,
                    full_name=name,
                    phone_number=phone,
                    email=email,
                    configuration=lead_data.get('unit_size', ''),
                    form_name=f"Google Sheets - {lead_data.get('project_name', 'Force Sync')}",
                    source='Google Sheets',
                    created_time=created_time,
                    extra_fields={
                        'project_name': lead_data.get('project_name', ''),
                        'force_synced': True,
                        'original_timestamp': timestamp
                    }
                )
                
                print(f"  CREATED: {name} ({phone}) - ID: {lead_id}")
                synced_count += 1
                
            except Exception as e:
                print(f"  ERROR: Failed to create {lead_data.get('name')}: {str(e)}")
        
        print(f"\nForce sync complete:")
        print(f"  - Synced: {synced_count} leads")
        print(f"  - Duplicates: {duplicate_count} leads")
        
    except Exception as e:
        print(f"Error during force sync: {str(e)}")

if __name__ == "__main__":
    force_sync_google_sheets()