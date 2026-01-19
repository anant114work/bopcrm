import requests
import json
from django.conf import settings
from leads.models import Lead, TeamMember
from leads.acefone_models import AcefoneConfig, DIDNumber
from leads.models import AutoCallConfig, AutoCallLog
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class AutoCallService:
    def __init__(self):
        self.acefone_config = AcefoneConfig.objects.filter(is_active=True).first()
        
    def trigger_auto_call(self, lead):
        """Trigger automatic call for any new lead"""
        if not lead.phone_number:
            return False, "No phone number"
            
        # Find agent based on project mapping
        agent = self._get_mapped_agent(lead)
        if not agent:
            return False, "No agent mapped"
            
        # Get agent's DID number
        agent_did = DIDNumber.objects.filter(assigned_user=agent, is_active=True).first()
        if not agent_did:
            return False, "Agent has no DID number"
            
        # Initiate call via Acefone
        return self._initiate_acefone_call(lead, agent, agent_did)
    

    def _get_mapped_agent(self, lead):
        """Get the mapped agent for the lead's project"""
        form_name = (lead.form_name or '').lower()
        
        # Check for configured project mappings
        for config in AutoCallConfig.objects.filter(is_active=True):
            if config.project_name.lower() in form_name:
                return config.mapped_agent
        
        # Default agent for all leads (Anat Sharma)
        default_agent = TeamMember.objects.filter(
            name__icontains='anat',
            is_active=True
        ).first()
        
        if not default_agent:
            default_agent = TeamMember.objects.filter(
                phone='918062451617',
                is_active=True
            ).first()
        
        if default_agent:
            print(f"[AUTO CALL] Using default agent: {default_agent.name} ({default_agent.phone})")
            return default_agent
            
        # Final fallback
        fallback_agent = TeamMember.objects.filter(is_active=True).first()
        if fallback_agent:
            print(f"[AUTO CALL] Using fallback agent: {fallback_agent.name} ({fallback_agent.phone})")
        return fallback_agent
    
    def _initiate_acefone_call(self, lead, agent, agent_did):
        """Initiate call through Acefone API"""
        if not self.acefone_config:
            print(f"[AUTO CALL ERROR] Acefone not configured")
            return False, "Acefone not configured"
            
        try:
            # Clean phone numbers
            customer_phone = self._clean_phone(lead.phone_number)
            agent_phone = self._clean_phone(agent.phone)
            
            print(f"[AUTO CALL] Initiating call for {lead.full_name}")
            print(f"[AUTO CALL] Customer: {customer_phone}, Agent: {agent_phone}")
            
            # Use Acefone Click2Call Support API
            api_url = "https://api.acefone.in/v1/click_to_call_support"
            
            payload = {
                'api_key': self.acefone_config.token,
                'customer_number': customer_phone,
                'caller_id': agent_did.number if agent_did else agent_phone,
                'async': 1
            }
            
            headers = {
                'accept': 'application/json',
                'content-type': 'application/json'
            }
            
            print(f"[AUTO CALL] API URL: {api_url}")
            print(f"[AUTO CALL] Payload: {payload}")
            
            response = requests.post(
                api_url, 
                json=payload,
                headers=headers,
                timeout=10
            )
            
            print(f"[AUTO CALL] Response Status: {response.status_code}")
            print(f"[AUTO CALL] Response: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                call_id = result.get('call_id', 'unknown')
                
                # Create call record
                from .acefone_models import CallRecord
                CallRecord.objects.create(
                    acefone_call_id=call_id,
                    lead=lead,
                    agent=agent,
                    lead_name=lead.full_name,
                    lead_number=customer_phone,
                    from_number=agent_phone,
                    status='initiated'
                )
                
                # Log the call (handle null call_id)
                AutoCallLog.objects.create(
                    lead=lead,
                    agent=agent,
                    call_id=call_id or result.get('ref_id', 'unknown'),
                    status='initiated'
                )
                
                print(f"[AUTO CALL SUCCESS] Call initiated for {lead.full_name} - Call ID: {call_id}")
                
                return True, f"Call initiated - ID: {call_id}"
            else:
                error_msg = f"API Error: {response.status_code} - {response.text}"
                print(f"[AUTO CALL ERROR] {error_msg}")
                return False, error_msg
                
        except Exception as e:
            # Log failed call (handle null call_id)
            AutoCallLog.objects.create(
                lead=lead,
                agent=agent,
                call_id='failed',
                status='failed',
                error_message=str(e)
            )
            
            error_msg = f"Auto call failed for {lead.full_name}: {str(e)}"
            print(f"[AUTO CALL ERROR] {error_msg}")
            return False, str(e)
    
    def _clean_phone(self, phone):
        """Clean and format phone number"""
        if not phone:
            return ""
        
        # Remove all non-digits
        clean = ''.join(filter(str.isdigit, phone))
        
        # Add country code if missing
        if len(clean) == 10:
            clean = '91' + clean
        elif len(clean) == 11 and clean.startswith('0'):
            clean = '91' + clean[1:]
            
        return clean

# Global service instance
auto_call_service = AutoCallService()

def trigger_auto_call_for_lead(lead):
    """Trigger auto call for any new lead"""
    return auto_call_service.trigger_auto_call(lead)