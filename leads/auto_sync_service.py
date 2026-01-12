import os
import sys
import django
import requests
import time
import threading
from datetime import datetime

# Setup Django
sys.path.append('d:\\AI-proto\\CRM\\drip')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import Lead
from django.conf import settings
from django.utils.dateparse import parse_datetime

class AutoSyncService:
    def __init__(self):
        self.running = False
        self.last_sync = 0
        
    def start(self):
        self.running = True
        print(f"[{datetime.now()}] Auto sync started - syncing every 5 minutes")
        
        while self.running:
            try:
                synced = self.sync_leads()
                if synced > 0:
                    print(f"[{datetime.now()}] Synced {synced} new leads")
                self.last_sync = time.time()
                time.sleep(300)  # 5 minutes
            except Exception as e:
                print(f"[{datetime.now()}] Sync error: {e}")
                time.sleep(60)  # Wait 1 minute on error
    
    def sync_leads(self):
        ACCESS_TOKEN = settings.META_ACCESS_TOKEN
        PAGE_ID = settings.META_PAGE_ID
        
        forms_url = f'https://graph.facebook.com/v23.0/{PAGE_ID}/leadgen_forms'
        forms_response = requests.get(forms_url, params={'access_token': ACCESS_TOKEN})
        
        if forms_response.status_code != 200:
            return 0
            
        forms_data = forms_response.json()
        total_synced = 0
        
        for form in forms_data.get('data', []):
            form_id = form['id']
            form_name = form.get('name', 'Unknown Form')
            
            leads_url = f'https://graph.facebook.com/v23.0/{form_id}/leads'
            leads_response = requests.get(leads_url, params={
                'access_token': ACCESS_TOKEN,
                'fields': 'id,created_time,field_data'
            })
            
            if leads_response.status_code != 200:
                continue
                
            leads_data = leads_response.json()
            
            for lead_data in leads_data.get('data', []):
                if Lead.objects.filter(lead_id=lead_data['id']).exists():
                    continue
                
                field_data = lead_data.get('field_data', [])
                email = full_name = phone_number = city = budget = configuration = ''
                
                for field in field_data:
                    name = field.get('name', '')
                    value = field['values'][0] if field.get('values') else field.get('value', '')
                    
                    if name == 'email': email = value
                    elif name == 'full_name': full_name = value
                    elif name in ['phone_number', 'phone', 'mobile']: phone_number = value
                    elif name == 'city': city = value
                    elif 'budget' in name.lower(): budget = value
                    elif 'configuration' in name.lower(): configuration = value
                
                Lead.objects.create(
                    lead_id=lead_data['id'],
                    created_time=parse_datetime(lead_data['created_time']),
                    email=email, full_name=full_name, phone_number=phone_number,
                    form_name=form_name, city=city, budget=budget, configuration=configuration
                )
                total_synced += 1
        
        return total_synced

if __name__ == '__main__':
    service = AutoSyncService()
    try:
        service.start()
    except KeyboardInterrupt:
        print(f"\n[{datetime.now()}] Auto sync stopped")
        service.running = False