import requests
import time
import threading
from django.utils import timezone
from .bulk_call_models import BulkCallCampaign, BulkCallRecord

# CallKaro API Configuration
CALLKARO_API_URL = "https://api.callkaro.com/v1/call"
CALLKARO_API_KEY = "your_callkaro_api_key"  # Replace with actual key

def initiate_callkaro_call(phone_number, name=None, agent_id=None):
    """Initiate a call using CallKaro AI agent - NO NAMES to avoid sample data"""
    try:
        import requests
        
        # Use same API key as working system
        api_key = "bc422db39aa327234a911dd901accfcfa975623ee84c65c83aae9c4f844ffdb8"
        
        # Use AU Reality agent ID
        if not agent_id:
            agent_id = "69294d3d2cc1373b1f3a3972"  # AU Reality Agent (CORRECT)
        
        print(f"[CALLKARO BULK] Initiating call to {phone_number} with agent: {agent_id}")
        
        # Format phone number same as working system
        if not phone_number.startswith('+'):
            phone_number = f"+91{phone_number}" if len(phone_number) == 10 else f"+{phone_number}"
        
        # Use exact same payload structure as working system - NO NAME in metadata
        payload = {
            "to_number": phone_number,
            "agent_id": agent_id,
            "metadata": {
                "source": "bulk_call_campaign",
                "campaign_type": "bulk_upload"
            },
            "priority": 1
        }
        
        headers = {
            "Content-Type": "application/json",
            "X-API-KEY": api_key
        }
        
        # Use correct agent names
        agent_names = {
            "6923ff797a5d5a94d5a5dfcf": "Gaur Yamuna Agent",
            "692d5b6ad10e948b7bbfc2db": "AU Realty Agent 1", 
            "69294d3d2cc1373b1f3a3972": "AU Reality Agent"
        }
        agent_name = agent_names.get(agent_id, "AU Reality Agent")
        
        print(f"\n{'='*60}")
        print(f"CALL KARO AI - BULK CALLING")
        print(f"{'='*60}")
        print(f"Phone: {phone_number}")
        print(f"Agent ID: {agent_id}")
        print(f"Agent: {agent_name}")
        print(f"API Key: {api_key[:20]}...")
        print(f"Metadata: {payload['metadata']}")
        print(f"{'='*60}")
        
        # Use exact same API call as working system
        response = requests.post(
            "https://api.callkaro.ai/call/outbound",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        print(f"API Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            api_response = response.json()
            call_id = api_response.get('call_sid', api_response.get('call_id', 'N/A'))
            print(f"SUCCESS: {api_response}")
            print(f"{'='*60}\n")
            return {
                'success': True,
                'call_id': call_id,
                'response': api_response
            }
        else:
            error_msg = response.text
            print(f"API ERROR: {error_msg}")
            print(f"{'='*60}\n")
            
            # Check if it's an agent error
            if 'agent' in error_msg.lower():
                return {
                    'success': False,
                    'error': f'Error getting agent! Agent ID: {agent_id} may be invalid'
                }
            else:
                return {
                    'success': False,
                    'error': f'Call Karo AI Error: {error_msg}'
                }
            
    except Exception as e:
        print(f"[CALLKARO BULK] Exception: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

class BulkCallProcessor:
    def __init__(self):
        self.running_campaigns = {}
        self.threads = {}
    
    def get_campaign_status(self, campaign_id):
        """Get detailed campaign status"""
        try:
            campaign = BulkCallCampaign.objects.get(id=campaign_id)
            is_running_in_memory = campaign_id in self.running_campaigns
            
            return {
                'success': True,
                'campaign_id': campaign_id,
                'name': campaign.name,
                'status': campaign.status,
                'running_in_memory': is_running_in_memory,
                'total_numbers': campaign.total_numbers,
                'completed_calls': campaign.completed_calls,
                'successful_calls': campaign.successful_calls,
                'failed_calls': campaign.failed_calls,
                'pending_calls': campaign.call_records.filter(status='pending').count()
            }
        except BulkCallCampaign.DoesNotExist:
            return {'success': False, 'error': 'Campaign not found'}
    
    def cleanup_campaigns(self):
        """Clean up any inconsistent campaign states"""
        try:
            # Find campaigns marked as running but not in memory
            running_campaigns = BulkCallCampaign.objects.filter(status='running')
            cleaned = 0
            
            for campaign in running_campaigns:
                if campaign.id not in self.running_campaigns:
                    # Check if it has pending calls
                    pending_calls = campaign.call_records.filter(status='pending').count()
                    if pending_calls == 0:
                        campaign.status = 'completed'
                    else:
                        campaign.status = 'paused'
                    campaign.save()
                    cleaned += 1
                    print(f"[BULK CALL] Cleaned up campaign {campaign.name} - set to {campaign.status}")
            
            return {'success': True, 'cleaned': cleaned}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def start_campaign(self, campaign_id):
        """Start processing a bulk call campaign"""
        if campaign_id in self.running_campaigns:
            return False, "Campaign already running in memory"
        
        try:
            campaign = BulkCallCampaign.objects.get(id=campaign_id)
            
            # Only mark as skipped if already called in THIS campaign
            already_called_in_campaign = set(campaign.call_records.exclude(status='pending').values_list('phone_number', flat=True))
            duplicate_records = campaign.call_records.filter(status='pending', phone_number__in=already_called_in_campaign)
            skipped_count = duplicate_records.count()
            
            if skipped_count > 0:
                duplicate_records.update(status='skipped', error_message='Already called in this campaign')
                print(f"[BULK CALL] Marked {skipped_count} duplicate numbers as skipped (within same campaign)")
            
            # Check if campaign has pending calls
            pending_calls = campaign.call_records.filter(status='pending').count()
            if pending_calls == 0:
                return False, f"No pending calls in campaign (skipped {skipped_count} duplicates)"
            
            campaign.status = 'running'
            campaign.started_at = timezone.now()
            campaign.save()
            
            self.running_campaigns[campaign_id] = True
            thread = threading.Thread(target=self._process_campaign, args=(campaign_id,), daemon=True)
            self.threads[campaign_id] = thread
            thread.start()
            
            message = f"Campaign started with {pending_calls} calls"
            if skipped_count > 0:
                message += f" (skipped {skipped_count} duplicates)"
            
            print(f"[BULK CALL] Started campaign: {campaign.name} with {pending_calls} pending calls")
            return True, message
            
        except BulkCallCampaign.DoesNotExist:
            return False, "Campaign not found"
        except Exception as e:
            return False, str(e)
    
    def stop_campaign(self, campaign_id):
        """Stop a running campaign"""
        try:
            campaign = BulkCallCampaign.objects.get(id=campaign_id)
            
            if campaign_id in self.running_campaigns:
                self.running_campaigns[campaign_id] = False
                campaign.status = 'paused'
                campaign.save()
                print(f"[BULK CALL] Stopped campaign: {campaign.name}")
                return True, "Campaign stopped"
            else:
                # Campaign exists but not running - just update status
                if campaign.status == 'running':
                    campaign.status = 'paused'
                    campaign.save()
                    print(f"[BULK CALL] Campaign {campaign.name} was marked as running but not in memory - paused")
                    return True, "Campaign paused"
                else:
                    print(f"[BULK CALL] Campaign {campaign.name} is already {campaign.status}")
                    return True, f"Campaign is already {campaign.status}"
        except BulkCallCampaign.DoesNotExist:
            return False, "Campaign not found"
    
    def _process_campaign(self, campaign_id):
        """Process all calls in a campaign"""
        try:
            campaign = BulkCallCampaign.objects.get(id=campaign_id)
            pending_calls = campaign.call_records.filter(status='pending')
            
            print(f"[BULK CALL] Processing {pending_calls.count()} calls for {campaign.name}")
            
            # Only skip numbers already called in THIS campaign
            called_in_campaign = set(campaign.call_records.exclude(status='pending').values_list('phone_number', flat=True))
            if called_in_campaign:
                pending_calls = pending_calls.exclude(phone_number__in=called_in_campaign)
                print(f"[BULK CALL] Skipping {len(called_in_campaign)} already called numbers in this campaign")
                print(f"[BULK CALL] Remaining to call: {pending_calls.count()}")
            
            for call_record in pending_calls:
                if not self.running_campaigns.get(campaign_id, False):
                    print(f"[BULK CALL] Campaign {campaign_id} stopped")
                    break
                
                # Update status to calling
                call_record.status = 'calling'
                call_record.initiated_at = timezone.now()
                call_record.save()
                
                # Initiate call (no name to avoid sample names)
                result = initiate_callkaro_call(call_record.phone_number, None, campaign.agent_id)
                
                if result['success']:
                    call_record.status = 'connected'
                    call_record.call_id = result.get('call_id', '')
                    call_record.connected_at = timezone.now()
                    call_record.api_response = result.get('response', {})
                    campaign.successful_calls += 1
                    print(f"[BULK CALL] SUCCESS Connected: {call_record.phone_number}")
                else:
                    call_record.status = 'failed'
                    call_record.error_message = result.get('error', 'Unknown error')
                    call_record.api_response = {'error': result.get('error')}
                    campaign.failed_calls += 1
                    print(f"[BULK CALL] FAILED: {call_record.phone_number} - {result.get('error')}")
                
                call_record.ended_at = timezone.now()
                call_record.save()
                
                campaign.completed_calls += 1
                campaign.save()
                
                # Wait 5 seconds between calls
                time.sleep(5)
            
            # Mark campaign as completed
            campaign.status = 'completed'
            campaign.completed_at = timezone.now()
            campaign.save()
            
            if campaign_id in self.running_campaigns:
                del self.running_campaigns[campaign_id]
            
            print(f"[BULK CALL] SUCCESS Campaign completed: {campaign.name}")
            print(f"[BULK CALL] Results: {campaign.successful_calls} successful, {campaign.failed_calls} failed")
            
        except Exception as e:
            print(f"[BULK CALL] ERROR Campaign error: {str(e)}")
            try:
                campaign = BulkCallCampaign.objects.get(id=campaign_id)
                campaign.status = 'failed'
                campaign.save()
                if campaign_id in self.running_campaigns:
                    del self.running_campaigns[campaign_id]
            except:
                pass

# Global processor instance
bulk_call_processor = BulkCallProcessor()