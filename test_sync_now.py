#!/usr/bin/env python
import os
import sys
import django
import requests

sys.path.append('d:\\AI-proto\\CRM\\drip')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from django.conf import settings

# Test Meta API connection
ACCESS_TOKEN = settings.META_ACCESS_TOKEN
PAGE_ID = settings.META_PAGE_ID

print("=== TESTING META API CONNECTION ===")
print(f"Page ID: {PAGE_ID}")
print(f"Access Token: {ACCESS_TOKEN[:20]}...")

try:
    # Test API connection
    forms_url = f'https://graph.facebook.com/v23.0/{PAGE_ID}/leadgen_forms'
    response = requests.get(forms_url, params={'access_token': ACCESS_TOKEN})
    
    print(f"API Response Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        forms = data.get('data', [])
        print(f"Found {len(forms)} forms")
        
        for form in forms[:3]:  # Show first 3 forms
            form_id = form['id']
            form_name = form.get('name', 'Unknown')
            print(f"  Form: {form_name} (ID: {form_id})")
            
            # Check recent leads for this form
            leads_url = f'https://graph.facebook.com/v23.0/{form_id}/leads'
            leads_response = requests.get(leads_url, params={
                'access_token': ACCESS_TOKEN,
                'fields': 'id,created_time,field_data',
                'limit': 5
            })
            
            if leads_response.status_code == 200:
                leads_data = leads_response.json()
                leads = leads_data.get('data', [])
                print(f"    Recent leads: {len(leads)}")
                
                for lead in leads[:2]:  # Show 2 most recent
                    created_time = lead.get('created_time', 'Unknown')
                    print(f"      Lead ID: {lead['id']} - {created_time}")
            else:
                print(f"    Error getting leads: {leads_response.status_code}")
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Connection failed: {str(e)}")

print("\n=== RECOMMENDATION ===")
print("1. Check if Meta campaigns are still running")
print("2. Verify access token hasn't expired") 
print("3. Run manual sync: POST /sync/")
print("4. Check Google Sheets sync if using Google leads")