"""
Enhanced Meta (Facebook) Lead Ads synchronization for 2000+ forms
Optimized for high-volume form syncing with proper logging and error handling
"""
import requests
import socket
import time
import threading
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from django.db import transaction
from .models import Lead
from .sync_log_models import SyncLog
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Force IPv4 to avoid DNS resolution issues
old_getaddrinfo = socket.getaddrinfo
def new_getaddrinfo(*args, **kwargs):
    responses = old_getaddrinfo(*args, **kwargs)
    return [response for response in responses if response[0] == socket.AF_INET]
socket.getaddrinfo = new_getaddrinfo

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedMetaSync:
    def __init__(self):
        self.access_token = getattr(settings, 'META_ACCESS_TOKEN', '')
        self.page_id = getattr(settings, 'META_PAGE_ID', '')
        self.running = False
        self.sync_thread = None
        self.last_sync_time = None
        self.total_forms_count = 0
        self.batch_size = 50  # Process forms in batches
        
        # Setup session with retry logic
        self.session = requests.Session()
        retry = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('https://', adapter)
        
    def start_auto_sync(self):
        """Start automatic syncing every minute"""
        if self.running:
            return {"status": "already_running"}
            
        self.running = True
        self.sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
        self.sync_thread.start()
        
        return {"status": "started", "message": "Auto sync started - running every minute"}
    
    def stop_auto_sync(self):
        """Stop automatic syncing"""
        self.running = False
        if self.sync_thread:
            self.sync_thread.join(timeout=5)
        return {"status": "stopped"}
    
    def _sync_loop(self):
        """Main sync loop - runs every minute"""
        logger.info("Enhanced Meta sync started - syncing every minute")
        
        while self.running:
            try:
                start_time = time.time()
                result = self.sync_all_forms()
                
                # Log success with minimal output
                if result['success']:
                    logger.info(f"✓ Synced {result['synced_leads']} leads from {result['forms_processed']} forms")
                else:
                    logger.error(f"✗ Sync failed: {result.get('error', 'Unknown error')}")
                
                # Wait for next minute
                elapsed = time.time() - start_time
                sleep_time = max(60 - elapsed, 5)  # At least 5 seconds between syncs
                time.sleep(sleep_time)
                
            except Exception as e:
                logger.error(f"✗ Sync loop error: {str(e)}")
                time.sleep(60)  # Wait 1 minute on error
    
    def sync_all_forms(self):
        """Sync leads from all forms efficiently"""
        try:
            # Get all forms first
            forms = self._get_all_forms()
            if not forms:
                return {
                    'success': False,
                    'error': 'No forms found or API error',
                    'synced_leads': 0,
                    'forms_processed': 0
                }
            
            self.total_forms_count = len(forms)
            total_synced = 0
            forms_processed = 0
            
            # Process forms in batches for efficiency
            for i in range(0, len(forms), self.batch_size):
                if not self.running:  # Check if we should stop
                    break
                    
                batch = forms[i:i + self.batch_size]
                batch_synced = self._process_form_batch(batch)
                total_synced += batch_synced
                forms_processed += len(batch)
                
                # Small delay between batches to avoid rate limiting
                time.sleep(0.1)
            
            # Log sync result
            self._log_sync_result(total_synced, forms_processed, self.total_forms_count)
            
            return {
                'success': True,
                'synced_leads': total_synced,
                'forms_processed': forms_processed,
                'total_forms': self.total_forms_count
            }
            
        except Exception as e:
            logger.error(f"Sync error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'synced_leads': 0,
                'forms_processed': 0
            }
    
    def _get_all_forms(self):
        """Get all forms from Meta API with pagination"""
        all_forms = []
        url = f"https://graph.facebook.com/v18.0/{self.page_id}/leadgen_forms"
        
        params = {
            'access_token': self.access_token,
            'fields': 'id,name',
            'limit': 100  # Max per request
        }
        
        while url:
            try:
                response = self.session.get(url, params=params, timeout=30)
                
                if response.status_code != 200:
                    logger.error(f"Forms API error: {response.status_code} - {response.text}")
                    break
                
                data = response.json()
                forms = data.get('data', [])
                all_forms.extend(forms)
                
                # Get next page URL
                url = data.get('paging', {}).get('next')
                params = {}  # Next URL already contains all params
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error getting forms: {str(e)}")
                break
        
        return all_forms
    
    def _process_form_batch(self, forms_batch):
        """Process a batch of forms and sync their leads"""
        batch_synced = 0
        
        for form in forms_batch:
            if not self.running:
                break
                
            try:
                form_id = form['id']
                form_name = form.get('name', 'Unknown Form')
                
                # Get leads for this form (only recent ones to avoid duplicates)
                leads = self._get_form_leads(form_id, form_name)
                
                # Save leads to database
                for lead_data in leads:
                    if self._save_lead(lead_data, form_name):
                        batch_synced += 1
                        
            except Exception as e:
                logger.error(f"Error processing form {form.get('id', 'unknown')}: {str(e)}")
                continue
        
        return batch_synced
    
    def _get_form_leads(self, form_id, form_name):
        """Get leads for a specific form (last 24 hours only)"""
        url = f"https://graph.facebook.com/v18.0/{form_id}/leads"
        
        # Only get leads from last 24 hours to avoid processing old data
        since = int((datetime.now() - timedelta(hours=24)).timestamp())
        
        params = {
            'access_token': self.access_token,
            'fields': 'id,created_time,field_data',
            'since': since,
            'limit': 100
        }
        
        leads = []
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                leads = data.get('data', [])
            else:
                logger.warning(f"Leads API error for form {form_id}: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"Request error for form {form_id}: {str(e)}")
        
        return leads
    
    def _save_lead(self, lead_data, form_name):
        """Save lead to database if it doesn't exist"""
        try:
            lead_id = lead_data.get('id')
            
            # Check if lead already exists
            if Lead.objects.filter(lead_id=lead_id).exists():
                return False
            
            # Parse field data
            field_data = lead_data.get('field_data', [])
            lead_info = self._parse_field_data(field_data)
            
            # Parse created time
            created_time = lead_data.get('created_time')
            if created_time:
                created_time = datetime.fromisoformat(created_time.replace('Z', '+00:00'))
            else:
                created_time = timezone.now()
            
            # Create lead with transaction for data integrity
            with transaction.atomic():
                Lead.objects.create(
                    lead_id=lead_id,
                    form_name=form_name,
                    full_name=lead_info.get('full_name', ''),
                    first_name=lead_info.get('first_name', ''),
                    last_name=lead_info.get('last_name', ''),
                    email=lead_info.get('email', ''),
                    phone_number=lead_info.get('phone_number', ''),
                    city=lead_info.get('city', ''),
                    budget=lead_info.get('budget', ''),
                    configuration=lead_info.get('configuration', ''),
                    created_time=created_time,
                    stage='new'
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving lead {lead_data.get('id', 'unknown')}: {str(e)}")
            return False
    
    def _parse_field_data(self, field_data):
        """Parse Meta field data into lead information"""
        lead_info = {}
        
        for field in field_data:
            field_name = field.get('name', '').lower()
            field_values = field.get('values', [])
            
            if not field_values:
                continue
                
            value = field_values[0]
            
            # Map field names to lead attributes
            if 'email' in field_name:
                lead_info['email'] = value
            elif 'phone' in field_name or 'mobile' in field_name:
                lead_info['phone_number'] = value
            elif 'full_name' in field_name or field_name == 'name':
                lead_info['full_name'] = value
            elif 'first_name' in field_name:
                lead_info['first_name'] = value
            elif 'last_name' in field_name:
                lead_info['last_name'] = value
            elif 'city' in field_name:
                lead_info['city'] = value
            elif 'budget' in field_name:
                lead_info['budget'] = value
            elif 'configuration' in field_name:
                lead_info['configuration'] = value
        
        return lead_info
    
    def _log_sync_result(self, synced_leads, forms_processed, total_forms):
        """Log sync result to database and console"""
        try:
            # Save to sync log
            SyncLog.objects.create(
                sync_type='meta_auto',
                leads_synced=synced_leads,
                forms_processed=forms_processed,
                total_forms=total_forms,
                success=True,
                sync_time=timezone.now()
            )
            
            self.last_sync_time = timezone.now()
            
        except Exception as e:
            logger.error(f"Error logging sync result: {str(e)}")
    
    def get_sync_status(self):
        """Get current sync status"""
        return {
            'running': self.running,
            'last_sync': self.last_sync_time.isoformat() if self.last_sync_time else None,
            'total_forms': self.total_forms_count
        }

# Global sync instance
meta_sync = EnhancedMetaSync()

def start_enhanced_sync():
    """Start the enhanced sync service"""
    return meta_sync.start_auto_sync()

def stop_enhanced_sync():
    """Stop the enhanced sync service"""
    return meta_sync.stop_auto_sync()

def get_sync_status():
    """Get sync status"""
    return meta_sync.get_sync_status()

def manual_sync_now():
    """Trigger manual sync"""
    return meta_sync.sync_all_forms()