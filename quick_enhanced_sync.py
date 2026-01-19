#!/usr/bin/env python
"""
Quick Enhanced Meta Sync - Minimal version for immediate testing
Syncs 2000+ forms every minute with clean console output
"""
import os
import sys
import django
import requests
import time
import threading
from datetime import datetime, timedelta

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import Lead
from django.conf import settings
from django.utils.dateparse import parse_datetime
from django.db import transaction

class QuickEnhancedSync:
    def __init__(self):
        self.access_token = getattr(settings, 'META_ACCESS_TOKEN', '')
        self.page_id = getattr(settings, 'META_PAGE_ID', '')
        self.running = False
        
    def start_sync(self):
        """Start minute-by-minute sync"""
        self.running = True
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Enhanced Meta sync started - syncing every minute")
        
        while self.running:
            try:
                start_time = time.time()
                result = self.sync_all_forms()
                
                if result['success']:
                    print(f"Synced {result['synced_leads']} leads from {result['forms_processed']} forms")
                else:
                    print(f"Sync failed: {result.get('error', 'Unknown error')}")
                
                # Wait for next minute
                elapsed = time.time() - start_time
                sleep_time = max(60 - elapsed, 5)
                time.sleep(sleep_time)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Sync error: {str(e)}")
                time.sleep(60)
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Sync stopped")
    
    def sync_all_forms(self):
        """Sync all forms efficiently"""
        try:
            print(f"[DEBUG] Starting sync - getting forms from API...")
            # Get all forms
            forms_url = f"https://graph.facebook.com/v18.0/{self.page_id}/leadgen_forms"
            params = {'access_token': self.access_token, 'limit': 100}
            
            all_forms = []
            while True:
                print(f"[DEBUG] Requesting forms from: {forms_url[:50]}...")
                response = requests.get(forms_url, params=params, timeout=30)
                print(f"[DEBUG] API Response: {response.status_code}")
                if response.status_code != 200:
                    print(f"[DEBUG] API Error Response: {response.text[:200]}")
                    return {'success': False, 'error': f'API Error: {response.status_code}'}
                
                data = response.json()
                forms = data.get('data', [])
                print(f"[DEBUG] Got {len(forms)} forms in this batch")
                all_forms.extend(forms)
                
                # Check for next page
                next_url = data.get('paging', {}).get('next')
                if not next_url:
                    break
                forms_url = next_url
                params = {}
            
            print(f"[DEBUG] Total forms found: {len(all_forms)}")
            
            total_synced = 0
            forms_processed = 0
            
            # Process forms in batches
            batch_size = 50
            print(f"[DEBUG] Processing {len(all_forms)} forms in batches of {batch_size}")
            for i in range(0, len(all_forms), batch_size):
                if not self.running:
                    break
                
                batch = all_forms[i:i + batch_size]
                print(f"[DEBUG] Processing batch {i//batch_size + 1}: {len(batch)} forms")
                batch_synced = self.process_batch(batch)
                print(f"[DEBUG] Batch {i//batch_size + 1} synced: {batch_synced} leads")
                total_synced += batch_synced
                forms_processed += len(batch)
                
                # Small delay between batches
                time.sleep(0.1)
            
            print(f"[DEBUG] Sync complete - {total_synced} leads from {forms_processed} forms")
            return {
                'success': True,
                'synced_leads': total_synced,
                'forms_processed': forms_processed,
                'total_forms': len(all_forms)
            }
            
        except Exception as e:
            print(f"[DEBUG] Exception in sync_all_forms: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def process_batch(self, forms_batch):
        """Process a batch of forms"""
        batch_synced = 0
        
        for idx, form in enumerate(forms_batch):
            if not self.running:
                break
            
            try:
                form_id = form['id']
                form_name = form.get('name', 'Unknown Form')
                print(f"[DEBUG] Processing form {idx+1}/{len(forms_batch)}: {form_name[:30]}...")
                
                # Get recent leads only (last 24 hours)
                since = int((datetime.now() - timedelta(hours=24)).timestamp())
                
                leads_url = f"https://graph.facebook.com/v18.0/{form_id}/leads"
                params = {
                    'access_token': self.access_token,
                    'fields': 'id,created_time,field_data',
                    'since': since,
                    'limit': 100
                }
                
                print(f"[DEBUG] Requesting leads from form: {form_id}")
                response = requests.get(leads_url, params=params, timeout=30)
                print(f"[DEBUG] Leads API response: {response.status_code}")
                if response.status_code != 200:
                    print(f"[DEBUG] Leads API error: {response.text[:100]}")
                    continue
                
                data = response.json()
                leads = data.get('data', [])
                print(f"[DEBUG] Found {len(leads)} leads in form {form_name[:20]}")
                
                form_leads_synced = 0
                for lead_data in leads:
                    if self.save_lead(lead_data, form_name):
                        form_leads_synced += 1
                        batch_synced += 1
                
                if form_leads_synced > 0:
                    print(f"[DEBUG] Synced {form_leads_synced} new leads from {form_name[:20]}")
                        
            except Exception as e:
                print(f"[DEBUG] Error processing form {form_id}: {str(e)}")
                continue
        
        return batch_synced
    
    def save_lead(self, lead_data, form_name):
        """Save lead to database"""
        try:
            lead_id = lead_data.get('id')
            
            # Check if exists
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
            
        except Exception:
            return False

def main():
    """Main function"""
    print("=" * 60)
    print("Quick Enhanced Meta Sync")
    print("Syncing 2000+ forms every minute")
    print("=" * 60)
    
    # Check config
    if not hasattr(settings, 'META_ACCESS_TOKEN') or not settings.META_ACCESS_TOKEN:
        print("ERROR: META_ACCESS_TOKEN not configured")
        return
        
    if not hasattr(settings, 'META_PAGE_ID') or not settings.META_PAGE_ID:
        print("ERROR: META_PAGE_ID not configured")
        return
    
    print(f"Meta Page ID: {settings.META_PAGE_ID}")
    print("Starting sync... Press Ctrl+C to stop")
    print()
    
    sync = QuickEnhancedSync()
    
    try:
        sync.start_sync()
    except KeyboardInterrupt:
        sync.running = False
        print("\nSync stopped successfully")

if __name__ == '__main__':
    main()