import requests
import json
from datetime import datetime, timedelta
from django.conf import settings

class GoogleAdsClient:
    def __init__(self):
        self.developer_token = "Qqs06KvnUON1MNgyVWI0hw"
        self.base_url = "https://googleads.googleapis.com/v17"
        # You'll need to get OAuth2 access token for boprealtygod@gmail.com
        self.access_token = None  # Set this after OAuth flow
        self.manager_customer_id = None  # Manager account customer ID
        self.client_customer_id = None   # Client account with ads
        
    def set_credentials(self, access_token, manager_customer_id, client_customer_id):
        self.access_token = access_token
        self.manager_customer_id = manager_customer_id.replace('-', '')
        self.client_customer_id = client_customer_id.replace('-', '')
    
    def get_headers(self):
        return {
            'Authorization': f'Bearer {self.access_token}',
            'developer-token': self.developer_token,
            'login-customer-id': self.manager_customer_id,
            'Content-Type': 'application/json'
        }
    
    def get_campaigns(self):
        """Get all campaigns from the client account"""
        url = f"{self.base_url}/customers/{self.client_customer_id}/googleAds:search"
        
        query = """
        SELECT 
            campaign.id,
            campaign.name,
            campaign.status,
            campaign.advertising_channel_type,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros
        FROM campaign 
        WHERE campaign.status != 'REMOVED'
        """
        
        payload = {"query": query}
        
        try:
            response = requests.post(url, headers=self.get_headers(), json=payload)
            if response.status_code == 200:
                return response.json().get('results', [])
            else:
                print(f"Error getting campaigns: {response.text}")
                return []
        except Exception as e:
            print(f"Exception getting campaigns: {e}")
            return []
    
    def get_leads_from_forms(self, days_back=30):
        """Get leads from lead forms in the last N days"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        url = f"{self.base_url}/customers/{self.client_customer_id}/googleAds:search"
        
        query = f"""
        SELECT 
            lead_form_submission_data.id,
            lead_form_submission_data.asset_id,
            lead_form_submission_data.campaign_id,
            lead_form_submission_data.form_submission_date_time,
            lead_form_submission_data.custom_lead_form_submission_fields
        FROM lead_form_submission_data 
        WHERE segments.date >= '{start_date.strftime('%Y-%m-%d')}'
        AND segments.date <= '{end_date.strftime('%Y-%m-%d')}'
        """
        
        payload = {"query": query}
        
        try:
            response = requests.post(url, headers=self.get_headers(), json=payload)
            if response.status_code == 200:
                return response.json().get('results', [])
            else:
                print(f"Error getting leads: {response.text}")
                return []
        except Exception as e:
            print(f"Exception getting leads: {e}")
            return []
    
    def get_ad_performance(self, days_back=7):
        """Get ad performance data"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        url = f"{self.base_url}/customers/{self.client_customer_id}/googleAds:search"
        
        query = f"""
        SELECT 
            ad_group_ad.ad.id,
            ad_group_ad.ad.name,
            campaign.name,
            ad_group.name,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions
        FROM ad_group_ad 
        WHERE segments.date >= '{start_date.strftime('%Y-%m-%d')}'
        AND segments.date <= '{end_date.strftime('%Y-%m-%d')}'
        AND ad_group_ad.status != 'REMOVED'
        """
        
        payload = {"query": query}
        
        try:
            response = requests.post(url, headers=self.get_headers(), json=payload)
            if response.status_code == 200:
                return response.json().get('results', [])
            else:
                print(f"Error getting ad performance: {response.text}")
                return []
        except Exception as e:
            print(f"Exception getting ad performance: {e}")
            return []
    
    def get_accessible_customers(self):
        """Get list of accessible customer accounts"""
        url = f"{self.base_url}/customers:listAccessibleCustomers"
        
        try:
            response = requests.get(url, headers=self.get_headers())
            if response.status_code == 200:
                return response.json().get('resourceNames', [])
            else:
                print(f"Error getting customers: {response.text}")
                return []
        except Exception as e:
            print(f"Exception getting customers: {e}")
            return []