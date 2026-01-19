"""
Meta (Facebook) Lead Ads synchronization module
"""
import requests
import socket
from datetime import datetime, timedelta
from django.utils import timezone
from .models import Lead
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Force IPv4 to avoid DNS resolution issues
old_getaddrinfo = socket.getaddrinfo
def new_getaddrinfo(*args, **kwargs):
    responses = old_getaddrinfo(*args, **kwargs)
    return [response for response in responses if response[0] == socket.AF_INET]
socket.getaddrinfo = new_getaddrinfo

# Meta API Configuration
META_ACCESS_TOKEN = "EAAgVjAbsIWoBQAxNXvZCqSTCkiZAYjQHBZBUiJ45UvDDZCqxmnP33ZCqZCpEYxqKTFOfNg8ICZCZBF0C61gsF29gLA1AAKbCr5RQadZBzDiKGdzZAI3tHBUIIzCr7c97EZC1G3N6QYZC6rZCu3GZCTJFUGioYqssTtVwYFwrimKPRAZA7MTczslkdQpMkyk16yNo05vNAqRiQQulynb"
META_PAGE_ID = "296508423701621"  # BOP Realty

def sync_meta_leads(start_date=None, end_date=None):
    """
    Sync Meta leads from Facebook Lead Ads
    
    Args:
        start_date: Start date for historical sync
        end_date: End date for historical sync
    
    Returns:
        dict: Sync results with counts and status
    """
    try:
        if not start_date:
            start_date = datetime.now() - timedelta(days=7)
        if not end_date:
            end_date = datetime.now()
        
        # Convert to timestamps for Meta API
        since = int(start_date.timestamp())
        until = int(end_date.timestamp())
        
        # Meta Graph API endpoint for lead ads
        url = f"https://graph.facebook.com/v18.0/{META_PAGE_ID}/leadgen_forms"
        
        params = {
            'access_token': META_ACCESS_TOKEN,
            'fields': 'id,name,leads{id,created_time,field_data}',
            'since': since,
            'until': until,
            'limit': 100
        }
        
        synced_count = 0
        errors = []
        
        try:
            # Create session with retry logic
            session = requests.Session()
            retry = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
            adapter = HTTPAdapter(max_retries=retry)
            session.mount('https://', adapter)
            
            response = session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Process forms and their leads
                for form in data.get('data', []):
                    form_name = form.get('name', 'Unknown Form')
                    
                    # Process leads for this form
                    for lead_data in form.get('leads', {}).get('data', []):
                        try:
                            # Extract lead information from field_data
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
                                    elif 'name' in field_name and 'full' in field_name:
                                        lead_info['full_name'] = value
                                    elif 'first' in field_name and 'name' in field_name:
                                        lead_info['first_name'] = value
                                    elif 'last' in field_name and 'name' in field_name:
                                        lead_info['last_name'] = value
                                    elif 'city' in field_name:
                                        lead_info['city'] = value
                                    elif 'budget' in field_name:
                                        lead_info['budget'] = value
                            
                            # Create or update lead
                            lead_id = lead_data.get('id')
                            created_time = lead_data.get('created_time')
                            
                            if created_time:
                                created_time = datetime.fromisoformat(created_time.replace('Z', '+00:00'))
                            else:
                                created_time = timezone.now()
                            
                            # Check if lead already exists
                            existing_lead = Lead.objects.filter(lead_id=lead_id).first()
                            
                            if not existing_lead:
                                # Create new lead
                                new_lead = Lead.objects.create(
                                    lead_id=lead_id,
                                    form_name=form_name,
                                    full_name=lead_info.get('full_name', ''),
                                    first_name=lead_info.get('first_name', ''),
                                    last_name=lead_info.get('last_name', ''),
                                    email=lead_info.get('email', ''),
                                    phone_number=lead_info.get('phone_number', ''),
                                    city=lead_info.get('city', ''),
                                    budget=lead_info.get('budget', ''),
                                    created_time=created_time,
                                    stage='new'
                                )
                                synced_count += 1
                        
                        except Exception as lead_error:
                            errors.append(f"Lead processing error: {str(lead_error)}")
                            continue
            
            else:
                errors.append(f"Meta API error: {response.status_code} - {response.text}")
        
        except requests.exceptions.RequestException as req_error:
            errors.append(f"Request error: {str(req_error)}")
        
        return {
            'synced': synced_count,
            'errors': errors,
            'success': synced_count > 0 or len(errors) == 0,
            'message': f'Synced {synced_count} leads from Meta'
        }
    
    except Exception as e:
        return {
            'synced': 0,
            'errors': [str(e)],
            'success': False,
            'message': f'Historical sync failed: {str(e)}'
        }

def sync_recent_meta_leads():
    """Sync recent Meta leads (last 24 hours)"""
    end_date = datetime.now()
    start_date = end_date - timedelta(hours=24)
    return sync_meta_leads(start_date, end_date)