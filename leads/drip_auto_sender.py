import time
import threading
import json
import requests
from django.utils import timezone
from datetime import timedelta
from .drip_campaign_models import DripSubscriber, DripMessageLog

# AI Sensy Configuration
AISENSY_API_URL = "https://backend.aisensy.com/campaign/t1/api/v2"

def send_drip_message(subscriber, drip_message):
    """Send a single drip message via AI Sensy"""
    print(f"[DRIP SEND] Starting send to {subscriber.phone_number} - Day {drip_message.day_number}")
    
    try:
        # Check if this exact message was already sent to this lead
        existing_log = DripMessageLog.objects.filter(
            phone_number=subscriber.phone_number,
            drip_message=drip_message,
            status='sent'
        ).first()
        
        if existing_log:
            print(f"[DRIP SEND] ⚠️ DUPLICATE PREVENTED: Day {drip_message.day_number} already sent to {subscriber.phone_number} on {existing_log.sent_at}")
            return {
                'success': False,
                'error': 'Message already sent',
                'duplicate': True
            }
        
        # Clean phone number
        clean_phone = subscriber.phone_number.replace('+91', '').replace('+', '').replace(' ', '').replace('-', '')
        if not clean_phone.startswith('91'):
            clean_phone = f"91{clean_phone}"
        
        # Build AI Sensy payload
        payload = {
            "apiKey": drip_message.api_key,
            "campaignName": drip_message.campaign_name,
            "destination": clean_phone,
            "userName": subscriber.first_name,
            "templateParams": [subscriber.first_name] if '{{1}}' in drip_message.message_text else [],
            "source": "new-landing-page form",
            "media": {},
            "buttons": [],
            "carouselCards": [],
            "location": {},
            "paramsFallbackValue": drip_message.fallback_params if drip_message.fallback_params else {}
        }
        
        # Create message log
        message_log = DripMessageLog.objects.create(
            subscriber=subscriber,
            drip_message=drip_message,
            phone_number=subscriber.phone_number,
            recipient_name=subscriber.first_name,
            final_message_text=drip_message.message_text.replace('{{1}}', subscriber.first_name),
            scheduled_at=timezone.now(),
            status='pending'
        )
        
        # Send via AI Sensy API
        response = requests.post(
            AISENSY_API_URL,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            message_log.status = 'sent'
            message_log.sent_at = timezone.now()
            drip_message.sent_count += 1
            drip_message.save()
            print(f"[DRIP SEND] ✅ SUCCESS: Day {drip_message.day_number} sent to {subscriber.first_name} ({subscriber.phone_number}) - Lead ID: {subscriber.lead.id if subscriber.lead else 'N/A'}")
            success = True
            error = None
        else:
            # Store detailed error for debugging
            error_details = f'API Error {response.status_code}: {response.text}'
            print(f"[DRIP SEND] ERROR: {error_details}")
            print(f"[DRIP SEND] Campaign: {payload['campaignName']} - Check if it exists in AI Sensy")
            
            message_log.status = 'failed'
            message_log.failed_at = timezone.now()
            message_log.error_message = error_details
            message_log.api_response = {
                'status_code': response.status_code,
                'response': response.text,
                'payload_sent': payload
            }
            drip_message.failed_count += 1
            drip_message.save()
            success = False
            error = error_details
        
        message_log.save()
        
        return {
            'success': success,
            'message_log_id': message_log.id,
            'error': error
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

class DripAutoSender:
    def __init__(self):
        self.running = False
        self.thread = None
    
    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_loop, daemon=True)
            self.thread.start()
            print("[AUTO SENDER] Started drip message auto-sender")
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        print("[AUTO SENDER] Stopped drip message auto-sender")
    
    def _run_loop(self):
        while self.running:
            try:
                self._process_pending_messages()
                time.sleep(30)  # Check every 30 seconds
            except Exception as e:
                print(f"[AUTO SENDER] Error: {str(e)}")
                time.sleep(60)  # Wait longer on error
    
    def _process_pending_messages(self):
        now = timezone.now()
        
        # Get subscribers ready for next message
        subscribers_ready = DripSubscriber.objects.filter(
            status='active',
            next_message_at__lte=now
        )
        
        if subscribers_ready.count() > 0:
            print(f"[AUTO SENDER] Found {subscribers_ready.count()} subscribers ready for messages")
        
        for subscriber in subscribers_ready:
            try:
                next_message = subscriber.get_next_message()
                if next_message:
                    print(f"[AUTO SENDER] Sending Day {next_message.day_number} to {subscriber.phone_number}")
                    
                    result = send_drip_message(subscriber, next_message)
                    
                    if result['success']:
                        subscriber.current_day = next_message.day_number
                        subscriber.schedule_next_message()
                        print(f"[AUTO SENDER] ✅ SUCCESS: {subscriber.phone_number} - Day {next_message.day_number} sent")
                    elif result.get('duplicate'):
                        # Skip duplicate, move to next day
                        subscriber.current_day = next_message.day_number
                        subscriber.schedule_next_message()
                        print(f"[AUTO SENDER] ⚠️ SKIPPED DUPLICATE: {subscriber.phone_number} - Day {next_message.day_number}")
                    else:
                        print(f"[AUTO SENDER] ❌ FAILED: {subscriber.phone_number} - {result['error']}")
                        # Retry after 2 minutes for failed messages
                        subscriber.next_message_at = timezone.now() + timedelta(minutes=2)
                        subscriber.save()
                        print(f"[AUTO SENDER] 🔄 Scheduled retry for {subscriber.phone_number} in 2 minutes")
                else:
                    # No more messages, mark as completed
                    subscriber.status = 'completed'
                    subscriber.completed_at = timezone.now()
                    subscriber.next_message_at = None
                    subscriber.save()
                    print(f"[AUTO SENDER] Completed sequence for {subscriber.phone_number}")
                    
            except Exception as e:
                print(f"[AUTO SENDER] Error processing {subscriber.phone_number}: {str(e)}")

# Global instance
auto_sender = DripAutoSender()