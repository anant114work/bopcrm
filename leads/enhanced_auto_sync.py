import os
import sys
import django
import requests
import time
import threading
import csv
import io
import re
from datetime import datetime, timedelta
from django.utils.dateparse import parse_datetime
from django.utils import timezone

# Setup Django
sys.path.append('d:\\AI-proto\\CRM\\drip')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import Lead
from leads.integration_models import MetaConfig, GoogleSheetsConfig
from leads.sync_log_models import SyncLog

class EnhancedAutoSyncService:
    def __init__(self):
        self.running = False
        self.last_sync = {}
        
    def start(self):
        self.running = True
        print(f"[{datetime.now()}] Enhanced auto sync started - syncing every 1 minute")
        
        while self.running:
            try:
                total_synced = 0
                
                # Sync Meta leads
                meta_synced = self.sync_meta_leads()
                total_synced += meta_synced
                
                # Sync Google Sheets leads
                google_synced = self.sync_google_sheets_leads()
                total_synced += google_synced
                
                print(f"[{datetime.now()}] Sync cycle: {total_synced} new leads (Meta: {meta_synced}, Google: {google_synced})")
                
                time.sleep(60)  # 1 minute
            except Exception as e:
                print(f"[{datetime.now()}] Sync error: {e}")
                time.sleep(60)  # Wait 1 minute on error
    
    def sync_meta_leads(self):
        """Sync leads from all active Meta configurations"""
        total_synced = 0
        meta_configs = MetaConfig.objects.filter(is_active=True)
        
        print(f"[META SYNC] Processing {meta_configs.count()} Meta configurations...")
        
        for meta_config in meta_configs:
            try:
                print(f"[META SYNC] Processing config: {meta_config.name}")
                print(f"[META SYNC]   - Page ID: {meta_config.page_id}")
                print(f"[META SYNC]   - Token: {meta_config.access_token[:20]}...")
                
                synced = self._sync_single_meta_config(meta_config)
                total_synced += synced
                
                print(f"[META SYNC]   - Result: {synced} new leads from {meta_config.name}")
                
            except Exception as e:
                print(f"[META SYNC]   - ERROR in {meta_config.name}: {e}")
        
        print(f"[META SYNC] Total Meta leads synced: {total_synced}")
        return total_synced
    
    def _sync_single_meta_config(self, meta_config):
        """Sync leads from a single Meta configuration"""
        log = SyncLog.objects.create(
            sync_type='meta',
            config_name=meta_config.name,
            config_id=meta_config.id,
            status='success'
        )
        
        try:
            forms_url = f'https://graph.facebook.com/v23.0/{meta_config.page_id}/leadgen_forms'
            print(f"[META API] Fetching forms from: {forms_url}")
            
            forms_response = requests.get(forms_url, params={'access_token': meta_config.access_token})
            print(f"[META API] Forms response: {forms_response.status_code}")
            
            if forms_response.status_code != 200:
                print(f"[META API] ERROR: {forms_response.status_code} - {forms_response.text}")
                log.status = 'error'
                log.error_message = f'API Error: {forms_response.status_code}'
                log.completed_at = timezone.now()
                log.save()
                return 0
            
            forms_data = forms_response.json()
            total_synced = 0
            forms_found = len(forms_data.get('data', []))
            print(f"[META API] Found {forms_found} forms")
            
            for form in forms_data.get('data', []):
                form_id = form['id']
                form_name = form.get('name', 'Unknown Form')
                print(f"[META API] Processing form: {form_name} (ID: {form_id})")
                
                leads_url = f'https://graph.facebook.com/v23.0/{form_id}/leads'
                print(f"[META API] Fetching leads from: {leads_url}")
                
                # Get ALL leads with pagination
                all_leads = []
                next_url = leads_url
                page_count = 0
                
                while next_url and page_count < 10:  # Limit to 10 pages to avoid infinite loop
                    page_count += 1
                    leads_response = requests.get(next_url, params={
                        'access_token': meta_config.access_token,
                        'fields': 'id,created_time,field_data',
                        'limit': 100  # Get 100 leads per page
                    })
                    print(f"[META API] Page {page_count} response: {leads_response.status_code}")
                    
                    if leads_response.status_code != 200:
                        break
                        
                    page_data = leads_response.json()
                    page_leads = page_data.get('data', [])
                    all_leads.extend(page_leads)
                    
                    # Check for next page
                    paging = page_data.get('paging', {})
                    next_url = paging.get('next')
                    
                    print(f"[META API] Page {page_count}: {len(page_leads)} leads, Total: {len(all_leads)}")
                    
                    if not next_url:
                        break
                
                print(f"[META API] Total leads fetched: {len(all_leads)} from {page_count} pages")
                
                # Create a fake response object with all leads
                class FakeResponse:
                    def __init__(self, data):
                        self.status_code = 200
                        self._data = data
                    def json(self):
                        return {'data': self._data}
                
                leads_response = FakeResponse(all_leads)
                
                leads_data = leads_response.json()
                leads_found = len(leads_data.get('data', []))
                print(f"[META API] Processing {leads_found} total leads in form {form_name}")
                
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
                        form_name=form_name, city=city, budget=budget, configuration=configuration,
                        source='Meta'
                    )
                    total_synced += 1
            
            log.leads_synced = total_synced
            log.completed_at = timezone.now()
            log.save()
            return total_synced
        
        except Exception as e:
            log.status = 'error'
            log.error_message = str(e)
            log.completed_at = timezone.now()
            log.save()
            raise
    
    def sync_google_sheets_leads(self):
        """Sync leads from all active Google Sheets configurations"""
        total_synced = 0
        sheet_configs = GoogleSheetsConfig.objects.filter(is_active=True)
        
        print(f"[GOOGLE SYNC] Processing {sheet_configs.count()} Google Sheet configurations...")
        
        for sheet_config in sheet_configs:
            try:
                print(f"[GOOGLE SYNC] Processing sheet: {sheet_config.name}")
                print(f"[GOOGLE SYNC]   - URL: {sheet_config.sheet_url[:60]}...")
                
                synced = self._sync_single_google_sheet(sheet_config)
                total_synced += synced
                
                print(f"[GOOGLE SYNC]   - Result: {synced} new leads from {sheet_config.name}")
                
            except Exception as e:
                print(f"[GOOGLE SYNC]   - ERROR in {sheet_config.name}: {e}")
        
        print(f"[GOOGLE SYNC] Total Google leads synced: {total_synced}")
        return total_synced
    
    def _sync_single_google_sheet(self, sheet_config):
        """Sync leads from a single Google Sheet configuration"""
        log = SyncLog.objects.create(
            sync_type='google',
            config_name=sheet_config.name,
            config_id=sheet_config.id,
            status='success'
        )
        
        try:
            sheet_id = self._extract_sheet_id(sheet_config.sheet_url)
            if not sheet_id:
                log.status = 'error'
                log.error_message = 'Invalid sheet URL'
                log.completed_at = timezone.now()
                log.save()
                return 0
            
            csv_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0'
            response = requests.get(csv_url)
            
            if response.status_code != 200:
                log.status = 'error'
                log.error_message = f'Sheet access error: {response.status_code}'
                log.completed_at = timezone.now()
                log.save()
                return 0
            
            csv_data = csv.DictReader(io.StringIO(response.text))
            total_synced = 0
            
            for row in csv_data:
                # Get values with multiple possible column names
                name = row.get('name') or row.get('Name') or row.get('full_name') or ''
                phone = (row.get('number') or row.get('Phone') or row.get('phone_number') or '').strip()
                email = (row.get('email') or row.get('Email') or '').strip()
                timestamp = row.get('date-time') or row.get('Date & Time') or row.get('timestamp') or ''
                project = row.get('project name') or row.get('Project Name') or 'Unknown'
                
                # Skip header or empty rows
                if not name or name.lower() in ['name', 'full_name']:
                    continue
                
                # Generate unique ID based on phone + timestamp or email + timestamp
                if phone:
                    lead_id = f"google_{sheet_config.id}_{phone}_{timestamp}"
                elif email:
                    lead_id = f"google_{sheet_config.id}_{email}_{timestamp}"
                else:
                    continue  # Skip if no phone or email
                
                # Check if lead already exists
                if Lead.objects.filter(lead_id=lead_id).exists():
                    continue
                
                # Parse timestamp
                created_time = self._parse_google_timestamp(timestamp)
                
                Lead.objects.create(
                    lead_id=lead_id,
                    created_time=created_time,
                    email=email,
                    full_name=name,
                    phone_number=phone,
                    form_name=f"{sheet_config.name} - {project}",
                    city=row.get('city') or row.get('City') or '',
                    budget=row.get('budget') or row.get('Budget') or row.get('Unit Size') or '',
                    configuration=row.get('configuration') or row.get('Configuration') or '',
                    source='Google'
                )
                total_synced += 1
            
            # Update last synced time
            sheet_config.last_synced = timezone.now()
            sheet_config.save()
            
            log.leads_synced = total_synced
            log.completed_at = timezone.now()
            log.save()
            return total_synced
        
        except Exception as e:
            log.status = 'error'
            log.error_message = str(e)
            log.completed_at = timezone.now()
            log.save()
            raise
    
    def _extract_sheet_id(self, url):
        """Extract spreadsheet ID from Google Sheets URL"""
        match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', url)
        return match.group(1) if match else None
    
    def _parse_google_timestamp(self, timestamp_str):
        """Parse Google Sheets timestamp to Django datetime"""
        try:
            # Try different timestamp formats
            formats = [
                '%d/%m/%Y %H:%M:%S',  # 05/11/2025 16:32:03
                '%m/%d/%Y %H:%M:%S',
                '%Y-%m-%d %H:%M:%S',
                '%d/%m/%Y',
                '%m/%d/%Y',
                '%Y-%m-%d'
            ]
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(timestamp_str, fmt)
                    return timezone.make_aware(dt)
                except ValueError:
                    continue
            
            # If all formats fail, use current time
            return timezone.now()
        except:
            return timezone.now()
    
    def stop(self):
        self.running = False

# Global service instance
sync_service = None

def start_enhanced_sync():
    global sync_service
    if sync_service and sync_service.running:
        return False
    
    sync_service = EnhancedAutoSyncService()
    sync_thread = threading.Thread(target=sync_service.start, daemon=True)
    sync_thread.start()
    return True

def stop_enhanced_sync():
    global sync_service
    if sync_service:
        sync_service.stop()
        sync_service = None
        return True
    return False

def is_sync_running():
    global sync_service
    return sync_service and sync_service.running

if __name__ == '__main__':
    service = EnhancedAutoSyncService()
    try:
        service.start()
    except KeyboardInterrupt:
        print(f"\n[{datetime.now()}] Enhanced auto sync stopped")
        service.running = False