from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from leads.models import ScheduledCall, CallLog
import requests
import time

class Command(BaseCommand):
    help = 'Run scheduled calls automatically'

    def handle(self, *args, **options):
        self.stdout.write('Starting scheduled calls service...')
        
        while True:
            try:
                # Check for due calls every 30 seconds
                now = timezone.now()
                window_start = now - timedelta(minutes=1)
                window_end = now + timedelta(minutes=1)
                
                due_calls = ScheduledCall.objects.filter(
                    scheduled_datetime__range=(window_start, window_end),
                    status='pending'
                )
                
                for call in due_calls:
                    self.stdout.write(f'Executing scheduled call for {call.lead.full_name}')
                    success = self.execute_call(call)
                    
                    if success:
                        call.status = 'completed'
                        call.executed_at = now
                        self.stdout.write(f'✅ Call executed for {call.lead.full_name}')
                    else:
                        call.status = 'failed'
                        self.stdout.write(f'❌ Call failed for {call.lead.full_name}')
                    
                    call.save()
                
                time.sleep(30)  # Check every 30 seconds
                
            except KeyboardInterrupt:
                self.stdout.write('Stopping scheduled calls service...')
                break
            except Exception as e:
                self.stdout.write(f'Error: {str(e)}')
                time.sleep(30)

    def execute_call(self, scheduled_call):
        """Execute a scheduled call via API"""
        try:
            url = "https://api.acefone.in/v1/click_to_call_support"
            headers = {"accept": "application/json", "content-type": "application/json"}
            payload = {
                "customer_number": scheduled_call.phone_number, 
                "api_key": "2449a616-b256-448e-8dd7-3bdf21696f67", 
                "async": 1
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            
            # Log the call
            CallLog.objects.create(
                lead=scheduled_call.lead,
                team_member=scheduled_call.team_member,
                phone_number=scheduled_call.phone_number,
                call_type='scheduled',
                status='initiated' if response.status_code == 200 else 'failed'
            )
            
            return response.status_code == 200
            
        except Exception as e:
            self.stdout.write(f'Call execution error: {str(e)}')
            return False