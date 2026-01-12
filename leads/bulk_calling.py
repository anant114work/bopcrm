import requests
import json
from datetime import datetime, timedelta
from django.utils import timezone
from leads.models import Lead, TeamMember
import asyncio
import time

class BulkCallingService:
    def __init__(self):
        self.api_token = "2449a616-b256-448e-8dd7-3bdf21696f67"  # Click-to-Call Support API Token
        self.agent_numbers = ["918062451619", "918062451617", "918064068787"]
        self.caller_id = "918062451620"  # Valid DID from Ace X panel
        self.base_url = "https://api.acefone.in/v1"
        self.bulk_paused = False
        self.current_bulk_index = 0
        
    def make_click_to_call(self, agent_number, customer_number, caller_id=None):
        """Make a click-to-call using Acefone API"""
        url = f"{self.base_url}/click_to_call"
        
        # Format destination number with country code
        dest = customer_number.strip()
        if len(dest) == 10:
            dest = "91" + dest
        
        payload = {
            "agent_number": agent_number,
            "destination_number": dest,
            "caller_id": caller_id or self.caller_id,
            "async": "1",
            "call_timeout": 120
        }
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_token}"
        }
        
        print(f"[BULK CALL] Calling {dest} via agent {agent_number} (original: {customer_number})")
        print(f"[BULK CALL] Payload: {payload}")
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            print(f"[BULK CALL] Response: {response.status_code} - {response.text}")
            if response.status_code != 200:
                print(f"[BULK CALL] Failed payload was: {payload}")
            return response.status_code == 200, response.json()
        except Exception as e:
            print(f"[BULK CALL ERROR] {str(e)}")
            return False, str(e)
    
    def schedule_callback(self, customer_name, customer_number, agent_id, schedule_datetime):
        """Schedule a callback using Acefone API"""
        url = f"{self.base_url}/dialer/schedule_call/"
        
        payload = {
            "customer_name": customer_name,
            "schedule_date_time": schedule_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            "assigned_to": agent_id,
            "customer_number": customer_number,
            "reminder_schedule_callbacks": True,
            "reminder_time": 10,
            "call_end_min": 15
        }
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_token}"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            return response.status_code == 200, response.json()
        except Exception as e:
            return False, str(e)
    
    def fetch_scheduled_calls(self):
        """Fetch upcoming scheduled calls"""
        url = f"{self.base_url}/dialer/schedule_call/"
        
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_token}"
        }
        
        now = datetime.now()
        params = {
            "from_date": now.strftime("%Y-%m-%d"),
            "to_date": (now + timedelta(minutes=5)).strftime("%Y-%m-%d")
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                return response.json().get("data", [])
            return []
        except Exception as e:
            print(f"[SCHEDULED CALLS ERROR] {str(e)}")
            return []
    
    def check_for_scheduled_interruption(self):
        """Check if any scheduled call should interrupt bulk calling"""
        scheduled_calls = self.fetch_scheduled_calls()
        now = datetime.now()
        
        for call in scheduled_calls:
            scheduled_time = datetime.strptime(call["schedule_date_time"], "%Y-%m-%d %H:%M:%S")
            if scheduled_time <= now + timedelta(minutes=1):  # Due within 1 minute
                return call
        return None
    
    def bulk_call_leads(self, lead_ids, agent_number=None):
        """Execute bulk calling with scheduled call interruption"""
        if not agent_number:
            agent_number = self.agent_numbers[0]
        
        leads = Lead.objects.filter(id__in=lead_ids, phone_number__isnull=False).exclude(phone_number='')
        
        print(f"[BULK CALL] Starting bulk call for {leads.count()} leads")
        
        self.current_bulk_index = 0
        self.bulk_paused = False
        
        for i, lead in enumerate(leads):
            if self.bulk_paused:
                print(f"[BULK CALL] Paused at lead {i}")
                break
                
            self.current_bulk_index = i
            
            # Check for scheduled interruption before each call
            scheduled_call = self.check_for_scheduled_interruption()
            if scheduled_call:
                print(f"[SCHEDULED INTERRUPT] Found scheduled call for {scheduled_call['customer_number']}")
                return {
                    'interrupted': True,
                    'scheduled_call': scheduled_call,
                    'current_index': i,
                    'remaining_leads': len(leads) - i
                }
            
            # Make the call
            success, result = self.make_click_to_call(
                agent_number, 
                lead.phone_number,
                self.caller_id
            )
            
            if success:
                print(f"[BULK CALL] Successfully called {lead.full_name} ({lead.phone_number})")
            else:
                print(f"[BULK CALL] Failed to call {lead.full_name}: {result}")
            
            # Small delay between calls
            time.sleep(2)
        
        print(f"[BULK CALL] Completed bulk calling")
        return {
            'interrupted': False,
            'completed': True,
            'total_processed': len(leads)
        }
    
    def handle_scheduled_call(self, scheduled_call):
        """Handle a scheduled callback"""
        print(f"[SCHEDULED CALL] Handling scheduled call for {scheduled_call['customer_number']}")
        
        success, result = self.make_click_to_call(
            scheduled_call['assigned_to'],
            scheduled_call['customer_number'],
            self.caller_id
        )
        
        return success, result
    
    def resume_bulk_calling(self, lead_ids, start_index, agent_number=None):
        """Resume bulk calling from a specific index"""
        if not agent_number:
            agent_number = self.agent_numbers[0]
            
        leads = Lead.objects.filter(id__in=lead_ids, phone_number__isnull=False).exclude(phone_number='')[start_index:]
        
        print(f"[BULK CALL] Resuming bulk call from index {start_index}")
        
        return self.bulk_call_leads([lead.id for lead in leads], agent_number)

# Global service instance
bulk_calling_service = BulkCallingService()