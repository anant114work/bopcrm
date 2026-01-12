#!/usr/bin/env python
import os
import sys
import django
import requests
from datetime import datetime

sys.path.append('d:\\AI-proto\\CRM\\drip')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import Lead
from django.conf import settings
from django.utils.dateparse import parse_datetime

ACCESS_TOKEN = settings.META_ACCESS_TOKEN
PAGE_ID = settings.META_PAGE_ID

print("=== MANUAL SYNC STARTING ===")

# Get forms and sync leads
forms_url = f'https://graph.facebook.com/v23.0/{PAGE_ID}/leadgen_forms'
forms_response = requests.get(forms_url, params={'access_token': ACCESS_TOKEN})
forms_data = forms_response.json()

total_synced = 0
forms = forms_data.get('data', [])

for form in forms:
    form_id = form['id']
    form_name = form.get('name', 'Unknown Form')
    
    # Get leads for this form
    leads_url = f'https://graph.facebook.com/v23.0/{form_id}/leads'
    leads_response = requests.get(leads_url, params={
        'access_token': ACCESS_TOKEN,
        'fields': 'id,created_time,field_data'
    })
    leads_data = leads_response.json()
    
    if 'error' in leads_data:
        continue
    
    leads = leads_data.get('data', [])
    
    for lead_data in leads:
        # Check if lead already exists
        if Lead.objects.filter(lead_id=lead_data['id']).exists():
            continue
            
        field_data = lead_data.get('field_data', [])
        
        # Extract fields
        email = ''
        full_name = ''
        phone_number = ''
        city = ''
        budget = ''
        configuration = ''
        
        for field in field_data:
            name = field.get('name', '')
            value = field['values'][0] if field.get('values') else field.get('value', '')
            
            if name == 'email':
                email = value
            elif name == 'full_name':
                full_name = value
            elif name in ['phone_number', 'phone', 'mobile']:
                phone_number = value
            elif name == 'city':
                city = value
            elif 'budget' in name.lower():
                budget = value
            elif 'configuration' in name.lower():
                configuration = value
        
        # Create lead
        lead = Lead.objects.create(
            lead_id=lead_data['id'],
            created_time=parse_datetime(lead_data['created_time']),
            email=email,
            full_name=full_name,
            phone_number=phone_number,
            form_name=form_name,
            city=city,
            budget=budget,
            configuration=configuration
        )
        
        total_synced += 1
        print(f"Synced: {full_name} from {lead_data['created_time']}")

print(f"\n=== SYNC COMPLETE ===")
print(f"Synced {total_synced} new leads")
print(f"Total leads now: {Lead.objects.count()}")