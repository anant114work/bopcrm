import requests
from django.conf import settings

class TataAPIClient:
    BASE_URL = "https://api-smartflo.tatateleservices.com/v1"
    
    def __init__(self):
        self.token = getattr(settings, 'TATA_API_TOKEN', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIzMTE2MDAiLCJjciI6dHJ1ZSwiaXNzIjoiaHR0cHM6Ly9jbG91ZHBob25lLnRhdGF0ZWxlc2VydmljZXMuY29tL3Rva2VuL2dlbmVyYXRlIiwiaWF0IjoxNzUxOTc4Nzg5LCJleHAiOjIwNTE5Nzg3ODksIm5iZiI6MTc1MTk3ODc4OSwianRpIjoiY3Bvc1Z4TW9oOHpWZ2d3MCJ9.G8qzkWIN0i3Dj5zxnct5JW-PpBlk6DUjXlSq6sWvc9I')
        self.headers = {'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json'}
    
    def get_active_calls(self):
        response = requests.get(f"{self.BASE_URL}/call/active", headers=self.headers)
        return response.json() if response.status_code == 200 else None
    
    def get_call_records(self, from_date=None, to_date=None, limit=50):
        params = {'limit': limit}
        if from_date: params['from_date'] = from_date
        if to_date: params['to_date'] = to_date
        try:
            response = requests.get(f"{self.BASE_URL}/call/records", headers=self.headers, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Call Records API failed: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Call Records API error: {str(e)}")
            return None
    
    def add_call_note(self, call_id, message, disposition=None):
        data = {'message': message}
        if disposition: data['agent_disposition'] = disposition
        response = requests.post(f"{self.BASE_URL}/call/note/{call_id}", headers=self.headers, json=data)
        return response.json() if response.status_code == 200 else None
    
    def get_call_notes(self, customer_number, limit=10):
        params = {'limit': limit}
        response = requests.get(f"{self.BASE_URL}/call/notes/{customer_number}", headers=self.headers, params=params)
        return response.json() if response.status_code == 200 else None
    
    def sync_call_records(self, days_back=1, limit=200):
        """Enhanced sync with better date range and processing"""
        from datetime import datetime, timedelta
        from django.utils import timezone
        from leads.models import Lead
        from .models import TataCall
        
        try:
            # Get calls with current time to catch latest calls
            from datetime import datetime, timedelta
            now = datetime.now()
            to_date = now.strftime('%Y-%m-%d %H:%M:%S')
            from_date = (now - timedelta(days=days_back)).strftime('%Y-%m-%d %H:%M:%S')
            

            
            response = self.get_call_records(from_date, to_date, limit)
            
            if response and 'count' in response:
                pass
            
            if not response:
                return {'message': 'No call data received', 'synced': 0}
            
            # Handle different response formats
            if 'results' in response:
                calls_data = response.get('results', [])
            elif 'data' in response:
                calls_data = response.get('data', [])
            else:
                calls_data = response if isinstance(response, list) else []
            synced_count = 0
            updated_count = 0
            

            
            for call_data in calls_data:
                call_id = call_data.get('call_id') or call_data.get('uuid')
                if not call_id:
                    continue
                
                # Skip if this call already exists and has proper data
                existing_call = TataCall.objects.filter(call_id=call_id).first()
                if existing_call and existing_call.customer_number and existing_call.start_stamp:
                    continue
                
                # Get customer phone number from correct API field
                customer_number = (
                    call_data.get('caller_id_num') or 
                    call_data.get('client_number') or 
                    call_data.get('customer_number') or ''
                )
                

                
                if not customer_number:
                    continue
                
                lead = self._find_lead_by_phone(customer_number)
                
                # Parse timestamps - combine date and time fields
                start_time_str = f"{call_data.get('date', '')} {call_data.get('time', '')}".strip()
                start_stamp = self._parse_timestamp(start_time_str) if start_time_str else self._parse_timestamp(call_data.get('start_stamp'))
                end_stamp = self._parse_timestamp(call_data.get('end_stamp'))
                
                # Ensure timezone awareness
                if start_stamp and timezone.is_naive(start_stamp):
                    start_stamp = timezone.make_aware(start_stamp)
                if end_stamp and timezone.is_naive(end_stamp):
                    end_stamp = timezone.make_aware(end_stamp)
                
                # Extract department and agent info
                agent_name = (call_data.get('agent_name') or call_data.get('answered_by_name', '')).strip()
                department = call_data.get('department_name') or 'General'
                
                # Create or update call record with database lock handling
                from django.db import transaction
                import time
                import sqlite3
                
                for retry in range(5):
                    try:
                        with transaction.atomic():
                            call_obj, created = TataCall.objects.update_or_create(
                                call_id=call_id,
                                defaults={
                                    'uuid': call_data.get('uuid', ''),
                                    'lead': lead,
                                    'customer_number': customer_number,
                                    'agent_number': call_data.get('agent_number') or call_data.get('answered_by', ''),
                                    'agent_name': agent_name,
                                    'department': department,
                                    'direction': call_data.get('direction', 'inbound'),
                                    'status': call_data.get('status') or call_data.get('call_status', 'received'),
                                    'start_stamp': start_stamp,
                                    'end_stamp': end_stamp if end_stamp else None,
                                    'duration': int(call_data.get('call_duration') or call_data.get('duration') or call_data.get('talk_time', 0)),
                                    'recording_url': call_data.get('recording_url') or call_data.get('recording', '')
                                }
                            )
                        break
                    except (sqlite3.OperationalError, Exception) as e:
                        if ("database is locked" in str(e) or "locked" in str(e).lower()) and retry < 4:
                            from django.db import connection
                            connection.close()
                            time.sleep(0.1 * (retry + 1))  # Exponential backoff
                            continue
                        if retry == 4:
                            continue
                        raise e
                
                if created:
                    synced_count += 1
            
            return {
                'message': f'Synced {synced_count} new calls from {len(calls_data)} total records',
                'synced': synced_count,
                'total': len(calls_data)
            }
            
        except Exception as e:
            return {'error': str(e), 'message': 'Sync failed'}
    
    def _find_lead_by_phone(self, phone_number):
        """Enhanced phone number matching"""
        if not phone_number:
            return None
            
        from leads.models import Lead
        
        # Clean phone number
        clean_phone = phone_number.replace('+91', '').replace('+', '').replace('-', '').replace(' ', '')
        
        # Try exact match first
        lead = Lead.objects.filter(phone_number=phone_number).first()
        if lead:
            return lead
            
        # Try without country code
        lead = Lead.objects.filter(phone_number__icontains=clean_phone[-10:]).first()
        if lead:
            return lead
            
        # Try with +91
        lead = Lead.objects.filter(phone_number__icontains=f'+91{clean_phone[-10:]}').first()
        return lead
    
    def _parse_timestamp(self, timestamp_str):
        """Parse timestamp string to datetime"""
        if not timestamp_str:
            return None
            
        from django.utils.dateparse import parse_datetime
        from django.utils import timezone
        from datetime import datetime
        
        try:
            # Try Django's parser first
            dt = parse_datetime(timestamp_str)
            if dt:
                if timezone.is_naive(dt):
                    dt = timezone.make_aware(dt)
                return dt
                
            # Try common formats
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S.%f']:
                try:
                    dt = datetime.strptime(timestamp_str, fmt)
                    # Always make timezone aware to prevent warnings
                    if dt:
                        if timezone.is_naive(dt):
                            dt = timezone.make_aware(dt)
                        return dt
                except ValueError:
                    continue
                    
        except Exception as e:
            pass
            
        return None
    
    def get_departments(self):
        """Fetch all departments with agents"""
        try:
            response = requests.get(f"{self.BASE_URL}/departments", headers=self.headers)
            print(f"Departments API - Status: {response.status_code}, Response: {response.text[:500]}")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Departments API failed: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Departments API error: {str(e)}")
            return None
    
    def get_recordings(self):
        """Fetch all system recordings"""
        try:
            response = requests.get(f"{self.BASE_URL}/recordings", headers=self.headers)
            print(f"Recordings API - Status: {response.status_code}, Response: {response.text[:500]}")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Recordings API failed: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Recordings API error: {str(e)}")
            return None
    
    def get_users(self):
        """Fetch all users/agents"""
        response = requests.get(f"{self.BASE_URL}/users", headers=self.headers)
        return response.json() if response.status_code == 200 else None
    
    def initiate_click_to_call(self, agent_number, customer_number, caller_id=None):
        data = {
            'agent_number': agent_number,
            'destination_number': customer_number,
            'async': 1
        }
        if caller_id: data['caller_id'] = caller_id
        response = requests.post(f"{self.BASE_URL}/click_to_call", headers=self.headers, json=data)
        return response.json() if response.status_code == 200 else None