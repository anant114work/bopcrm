#!/usr/bin/env python
"""
Find correct Meta form names and sync recent leads
"""
import os
import sys
import django
import requests
from datetime import datetime, timedelta

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import Lead
from django.conf import settings
from django.utils.dateparse import parse_datetime
from django.db import transaction

def sync_recent_leads():
    """Find and sync leads from your current ad forms"""
    
    access_token = getattr(settings, 'META_ACCESS_TOKEN', '')
    page_id = getattr(settings, 'META_PAGE_ID', '')
    
    # Get all forms
    forms_url = f"https://graph.facebook.com/v18.0/{page_id}/leadgen_forms"
    params = {'access_token': access_token, 'limit': 100}
    
    all_forms = []
    while True:
        response = requests.get(forms_url, params=params, timeout=30)
        data = response.json()
        forms = data.get('data', [])
        all_forms.extend(forms)
        
        next_url = data.get('paging', {}).get('next')
        if not next_url:
            break
        forms_url = next_url
        params = {}
    
    print(f"Found {len(all_forms)} total forms")
    
    # Look for forms created/updated recently (last 7 days)
    recent_keywords = ['ebc', 'gaur', 'acp', 'vedatam', 'static', 'video']
    target_forms = []
    
    for form in all_forms:
        form_name = form.get('name', '').lower()
        if any(keyword in form_name for keyword in recent_keywords):
            target_forms.append(form)
    
    print(f"Found {len(target_forms)} matching forms")
    
    total_synced = 0
    
    # Sync leads from last 24 hours for these forms
    since = int((datetime.now() - timedelta(hours=24)).timestamp())
    
    for form in target_forms:
        form_id = form['id']
        form_name = form.get('name', 'Unknown Form')
        
        print(f"Checking: {form_name}")
        
        # Get leads
        leads_url = f"https://graph.facebook.com/v18.0/{form_id}/leads"
        params = {
            'access_token': access_token,
            'fields': 'id,created_time,field_data',
            'since': since,
            'limit': 100
        }
        
        response = requests.get(leads_url, params=params, timeout=30)
        if response.status_code != 200:
            continue
            
        data = response.json()
        leads = data.get('data', [])
        
        form_synced = 0
        for lead_data in leads:
            if save_lead(lead_data, form_name):
                form_synced += 1
                total_synced += 1
        
        if form_synced > 0:
            print(f"  -> Synced {form_synced} new leads")
    
    print(f"\nTotal synced: {total_synced} leads")

def save_lead(lead_data, form_name):
    """Save lead to database"""
    try:
        lead_id = lead_data.get('id')
        
        if Lead.objects.filter(lead_id=lead_id).exists():
            return False
        
        # Parse field data
        field_data = lead_data.get('field_data', [])
        lead_info = {}
        
        for field in field_data:
            field_name = field.get('name', '').lower()
            field_values = field.get('values', [])
            
            if field_values:
                value = field_values[0]
                
                if 'email' in field_name:
                    lead_info['email'] = value
                elif 'phone' in field_name or 'mobile' in field_name:
                    lead_info['phone_number'] = value
                elif 'full_name' in field_name or field_name == 'name':
                    lead_info['full_name'] = value
                elif 'city' in field_name:
                    lead_info['city'] = value
                elif 'budget' in field_name:
                    lead_info['budget'] = value
        
        # Parse created time
        created_time = lead_data.get('created_time')
        if created_time:
            created_time = datetime.fromisoformat(created_time.replace('Z', '+00:00'))
        else:
            from django.utils import timezone
            created_time = timezone.now()
        
        # Create lead
        with transaction.atomic():
            Lead.objects.create(
                lead_id=lead_id,
                form_name=form_name,
                full_name=lead_info.get('full_name', ''),
                email=lead_info.get('email', ''),
                phone_number=lead_info.get('phone_number', ''),
                city=lead_info.get('city', ''),
                budget=lead_info.get('budget', ''),
                created_time=created_time,
                stage='new'
            )
        
        return True
        
    except Exception as e:
        print(f"Error saving lead: {e}")
        return False

if __name__ == '__main__':
    sync_recent_leads()