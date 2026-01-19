#!/usr/bin/env python
"""Test Meta API connection and fetch forms"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN')
PAGE_ID = os.getenv('META_PAGE_ID')

print("="*60)
print("META API CONNECTION TEST")
print("="*60)
print(f"Access Token: {ACCESS_TOKEN[:30]}..." if ACCESS_TOKEN else "Access Token: NOT SET")
print(f"Page ID: {PAGE_ID}")
print("="*60)

if not ACCESS_TOKEN or not PAGE_ID:
    print("ERROR: META_ACCESS_TOKEN or META_PAGE_ID not set in .env file")
    exit(1)

# Test 1: Get Page Info
print("\nTest 1: Fetching Page Info...")
page_url = f"https://graph.facebook.com/v21.0/{PAGE_ID}"
page_response = requests.get(page_url, params={
    'access_token': ACCESS_TOKEN,
    'fields': 'name,id'
})

if page_response.status_code == 200:
    page_data = page_response.json()
    print(f"SUCCESS - Page Name: {page_data.get('name')}")
    print(f"SUCCESS - Page ID: {page_data.get('id')}")
else:
    print(f"ERROR: {page_response.status_code}")
    print(f"Response: {page_response.text}")
    exit(1)

# Test 2: Get Lead Forms
print("\nTest 2: Fetching Lead Forms...")
forms_url = f"https://graph.facebook.com/v21.0/{PAGE_ID}/leadgen_forms"
forms_response = requests.get(forms_url, params={
    'access_token': ACCESS_TOKEN,
    'fields': 'id,name,status,leads_count'
})

if forms_response.status_code == 200:
    forms_data = forms_response.json()
    forms = forms_data.get('data', [])
    
    if forms:
        print(f"SUCCESS - Found {len(forms)} forms:")
        for form in forms:
            print(f"\n  Form: {form.get('name')}")
            print(f"     ID: {form.get('id')}")
            print(f"     Status: {form.get('status')}")
            print(f"     Leads: {form.get('leads_count', 'N/A')}")
    else:
        print("WARNING - No forms found. Make sure you have lead forms created in Facebook.")
else:
    print(f"ERROR: {forms_response.status_code}")
    print(f"Response: {forms_response.text}")
    exit(1)

# Test 3: Get Leads from First Form
if forms:
    print("\nTest 3: Fetching Leads from First Form...")
    first_form = forms[0]
    form_id = first_form['id']
    
    leads_url = f"https://graph.facebook.com/v21.0/{form_id}/leads"
    leads_response = requests.get(leads_url, params={
        'access_token': ACCESS_TOKEN,
        'fields': 'id,created_time,field_data'
    })
    
    if leads_response.status_code == 200:
        leads_data = leads_response.json()
        leads = leads_data.get('data', [])
        
        if leads:
            print(f"SUCCESS - Found {len(leads)} leads in '{first_form['name']}'")
            print(f"\nSample Lead:")
            sample_lead = leads[0]
            print(f"   Lead ID: {sample_lead.get('id')}")
            print(f"   Created: {sample_lead.get('created_time')}")
            print(f"   Fields:")
            for field in sample_lead.get('field_data', []):
                print(f"      - {field['name']}: {field['values'][0]}")
        else:
            print(f"WARNING - No leads found in form '{first_form['name']}'")
    else:
        print(f"ERROR: {leads_response.status_code}")
        print(f"Response: {leads_response.text}")

print("\n" + "="*60)
print("META API TEST COMPLETED")
print("="*60)
