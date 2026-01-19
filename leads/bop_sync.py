import requests
import json
from django.conf import settings
from leads.models import Lead
import logging

logger = logging.getLogger(__name__)

class BOPCRMSync:
    def __init__(self):
        self.api_key = "827c76a8-adbf-4f7f-b2b7-a956da6a4a93"
        self.endpoint = "https://crm.boprealty.com/welcome/insert_lead"
    
    def sync_lead_to_bop(self, lead):
        """Sync a lead to BOP CRM"""
        try:
            # Prepare payload according to BOP API format
            payload = {
                "api_key": self.api_key,
                "Name": lead.full_name or "Unknown",
                "Mobile": lead.phone_number or "",
                "Email": lead.email or "",
                "Project": lead.form_name or "Unknown Project",
                "Source": "Meta CRM",
                "Msg": f"Lead from {lead.source} - Stage: {lead.stage}"
            }
            
            print(f"[BOP SYNC] Syncing lead {lead.full_name} to BOP CRM")
            print(f"[BOP SYNC] Payload: {payload}")
            
            response = requests.post(
                self.endpoint,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            print(f"[BOP SYNC] Response: {response.status_code} - {response.text}")
            
            if response.status_code == 200 and "Success" in response.text:
                print(f"[BOP SYNC SUCCESS] Lead {lead.full_name} synced successfully")
                return True, "Lead synced successfully"
            else:
                print(f"[BOP SYNC ERROR] Failed to sync lead: {response.text}")
                return False, response.text
                
        except Exception as e:
            error_msg = f"BOP sync error for {lead.full_name}: {str(e)}"
            print(f"[BOP SYNC ERROR] {error_msg}")
            return False, error_msg

# Global instance
bop_sync = BOPCRMSync()

def sync_lead_to_bop_crm(lead):
    """Function to sync lead to BOP CRM"""
    return bop_sync.sync_lead_to_bop(lead)