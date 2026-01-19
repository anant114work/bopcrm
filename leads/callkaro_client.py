import requests
import json
from django.conf import settings
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class CallKaroClient:
    """Client for Call Karo AI API integration"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or getattr(settings, 'CALLKARO_API_KEY', None)
        self.base_url = "https://api.callkaro.ai"
        self.headers = {
            "Content-Type": "application/json",
            "X-API-KEY": self.api_key
        }
    
    def initiate_outbound_call(self, to_number, agent_id, metadata=None, **kwargs):
        """
        Initiate an outbound call using Call Karo AI
        
        Args:
            to_number (str): Phone number in international format
            agent_id (str): ID of the AI agent
            metadata (dict): Customer metadata
            **kwargs: Additional parameters like schedule_at, retries, etc.
        """
        url = f"{self.base_url}/call/outbound"
        
        payload = {
            "to_number": to_number,
            "agent_id": agent_id
        }
        
        if metadata:
            payload["metadata"] = metadata
            
        # Add optional parameters
        optional_params = [
            'schedule_at', 'min_trigger_time', 'max_trigger_time', 
            'carry_over', 'number_of_retries', 'gap_between_retries', 'priority'
        ]
        
        for param in optional_params:
            if param in kwargs:
                payload[param] = kwargs[param]
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "data": response.json()
                }
            else:
                error_data = response.json() if response.content else {}
                return {
                    "success": False,
                    "error": error_data.get("message", f"HTTP {response.status_code}")
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Call Karo API error: {str(e)}")
            return {
                "success": False,
                "error": f"Network error: {str(e)}"
            }
    
    def create_campaign(self, name, agent_id=None):
        """
        Create a new campaign (batch call)
        
        Args:
            name (str): Campaign name
            agent_id (str): Optional agent ID for v1 API
        """
        if agent_id:
            # Use v1 API with agent_id
            url = f"{self.base_url}/call/campaign"
            payload = {
                "name": name,
                "agent_id": agent_id
            }
        else:
            # Use v2 API without agent_id
            url = f"{self.base_url}/v2/call/campaign"
            payload = {
                "name": name
            }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "data": response.json()
                }
            else:
                error_data = response.json() if response.content else {}
                return {
                    "success": False,
                    "error": error_data.get("message", f"HTTP {response.status_code}")
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Call Karo Campaign API error: {str(e)}")
            return {
                "success": False,
                "error": f"Network error: {str(e)}"
            }
    
    def schedule_campaign_call(self, to_number, batch_id, agent_id, metadata=None, **kwargs):
        """
        Schedule a call as part of a campaign
        
        Args:
            to_number (str): Phone number in international format
            batch_id (str): Campaign batch ID
            agent_id (str): AI agent ID
            metadata (dict): Customer metadata
            **kwargs: Additional scheduling parameters
        """
        url = f"{self.base_url}/call/outbound"
        
        payload = {
            "to_number": to_number,
            "batch_id": batch_id,
            "agent_id": agent_id
        }
        
        if metadata:
            payload["metadata"] = metadata
            
        # Add optional parameters
        optional_params = [
            'schedule_at', 'min_trigger_time', 'max_trigger_time', 
            'carry_over', 'number_of_retries', 'gap_between_retries', 'priority'
        ]
        
        for param in optional_params:
            if param in kwargs:
                payload[param] = kwargs[param]
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "data": response.json()
                }
            else:
                error_data = response.json() if response.content else {}
                return {
                    "success": False,
                    "error": error_data.get("message", f"HTTP {response.status_code}")
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Call Karo Campaign Call API error: {str(e)}")
            return {
                "success": False,
                "error": f"Network error: {str(e)}"
            }