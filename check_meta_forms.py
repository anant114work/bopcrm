#!/usr/bin/env python
"""
Check Meta Forms - Compare API forms with database forms
"""
import os
import sys
import django
import requests

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import Lead
from django.conf import settings

def check_meta_forms():
    """Check all Meta forms and compare with database"""
    
    access_token = getattr(settings, 'META_ACCESS_TOKEN', '')
    page_id = getattr(settings, 'META_PAGE_ID', '')
    
    if not access_token or not page_id:
        print("ERROR: META_ACCESS_TOKEN or META_PAGE_ID not configured")
        return
    
    print("=" * 60)
    print("META FORMS ANALYSIS")
    print("=" * 60)
    
    # Get all forms from Meta API
    print("1. Fetching forms from Meta API...")
    forms_url = f"https://graph.facebook.com/v18.0/{page_id}/leadgen_forms"
    params = {'access_token': access_token, 'limit': 100}
    
    all_api_forms = []
    while True:
        response = requests.get(forms_url, params=params, timeout=30)
        if response.status_code != 200:
            print(f"API Error: {response.status_code} - {response.text}")
            return
        
        data = response.json()
        forms = data.get('data', [])
        all_api_forms.extend(forms)
        
        next_url = data.get('paging', {}).get('next')
        if not next_url:
            break
        forms_url = next_url
        params = {}
    
    print(f"   Found {len(all_api_forms)} forms in Meta API")
    
    # Get forms from database
    print("2. Checking forms in database...")
    db_forms = Lead.objects.values_list('form_name', flat=True).distinct().exclude(form_name='')
    db_forms_list = list(db_forms)
    print(f"   Found {len(db_forms_list)} unique form names in database")
    
    # Check for your specific forms
    print("\n3. Checking your advertised forms:")
    advertised_forms = [
        "EBC - Static",
        "Gaur ACP New - Video 3", 
        "EBC - Static 2",
        "Gaur ACP New - Video 1",
        "Gaur ACP New - Static",
        "Vedatam - Static"
    ]
    
    for form_name in advertised_forms:
        in_db = any(form_name.lower() in db_form.lower() for db_form in db_forms_list)
        status = "FOUND" if in_db else "MISSING"
        print(f"   {form_name}: {status}")
    
    # Show API form names that contain your keywords
    print("\n4. API forms matching your ads:")
    keywords = ['ebc', 'gaur', 'acp', 'vedatam', 'static', 'video']
    
    matching_forms = []
    for form in all_api_forms:
        form_name = form.get('name', '')
        if any(keyword.lower() in form_name.lower() for keyword in keywords):
            matching_forms.append(form_name)
            print(f"   API: {form_name}")
    
    print(f"\n   Found {len(matching_forms)} matching forms in API")
    
    # Check recent leads from these forms
    print("\n5. Recent leads from matching forms:")
    from datetime import datetime, timedelta
    yesterday = datetime.now() - timedelta(days=1)
    
    for keyword in ['gaur', 'ebc', 'vedatam']:
        recent_leads = Lead.objects.filter(
            form_name__icontains=keyword,
            created_time__gte=yesterday
        ).count()
        print(f"   {keyword.upper()} forms (last 24h): {recent_leads} leads")
    
    # Show all form names in database for reference
    print(f"\n6. All database form names ({len(db_forms_list)}):")
    for i, form_name in enumerate(sorted(db_forms_list)[:20]):  # Show first 20
        print(f"   {i+1}. {form_name}")
    if len(db_forms_list) > 20:
        print(f"   ... and {len(db_forms_list) - 20} more")

if __name__ == '__main__':
    check_meta_forms()