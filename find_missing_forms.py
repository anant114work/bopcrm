#!/usr/bin/env python
"""
Find the 2 missing forms and map them
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

def find_missing_forms():
    """Find EBC - Static 2 and Gaur ACP New - Static"""
    
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
    
    print("Looking for missing forms...")
    
    # Look for EBC forms
    ebc_forms = []
    gaur_static_forms = []
    
    for form in all_forms:
        form_name = form.get('name', '')
        form_id = form['id']
        
        # Check for EBC forms
        if 'ebc' in form_name.lower():
            ebc_forms.append((form_name, form_id))
        
        # Check for Gaur forms with "static" or similar
        if 'gaur' in form_name.lower() and ('static' in form_name.lower() or 'acp' in form_name.lower()):
            gaur_static_forms.append((form_name, form_id))
    
    print(f"\nAll EBC forms found ({len(ebc_forms)}):")
    for name, form_id in ebc_forms:
        print(f"  {name} (ID: {form_id})")
    
    print(f"\nAll Gaur ACP/Static forms found ({len(gaur_static_forms)}):")
    for name, form_id in gaur_static_forms:
        print(f"  {name} (ID: {form_id})")
    
    # Map the most likely candidates
    mappings = []
    
    # For EBC - Static 2, look for another EBC form
    if len(ebc_forms) > 1:
        for name, form_id in ebc_forms:
            if name != 'EBC - Static':  # Not the one we already mapped
                mappings.append((name, 'EBC - Static 2'))
                break
    
    # For Gaur ACP New - Static, look for unmapped Gaur forms
    mapped_gaur = ['Gaur ACP New - Video 3', 'Gaur ACP New - Video 1']
    for name, form_id in gaur_static_forms:
        if not any(mapped in name for mapped in mapped_gaur):
            mappings.append((name, 'Gaur ACP New - Static'))
            break
    
    print(f"\nProposed mappings:")
    for old_name, new_name in mappings:
        print(f"  '{old_name}' -> '{new_name}'")
    
    # Apply mappings
    total_updated = 0
    for old_name, new_name in mappings:
        leads = Lead.objects.filter(form_name=old_name)
        count = leads.count()
        
        if count > 0:
            updated = leads.update(form_name=new_name)
            print(f"\nUpdated {updated} leads: '{old_name}' -> '{new_name}'")
            total_updated += updated
        else:
            print(f"\nNo existing leads for '{old_name}' - will map future leads")
    
    print(f"\nTotal updated: {total_updated}")

if __name__ == '__main__':
    find_missing_forms()