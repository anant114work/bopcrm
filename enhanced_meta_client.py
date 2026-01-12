import requests
from datetime import datetime, timedelta

class EnhancedMetaClient:
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = "https://graph.facebook.com/v23.0"
    
    def get_all_leads(self, page_id, limit=100):
        """Get ALL leads with pagination"""
        all_leads = []
        url = f"{self.base_url}/{page_id}/leadgen_forms"
        
        # First get all forms
        forms_response = requests.get(url, params={
            'access_token': self.access_token,
            'fields': 'id,name,status,leads_count'
        })
        
        if forms_response.status_code != 200:
            return {'error': f'Forms API error: {forms_response.text}'}
        
        forms = forms_response.json().get('data', [])
        
        # Get leads from each form
        for form in forms:
            form_id = form['id']
            leads_url = f"{self.base_url}/{form_id}/leads"
            
            next_url = leads_url
            while next_url:
                response = requests.get(next_url, params={
                    'access_token': self.access_token,
                    'limit': limit,
                    'fields': 'id,created_time,field_data,ad_id,adset_id,campaign_id,form_id,is_organic'
                })
                
                if response.status_code != 200:
                    break
                
                data = response.json()
                leads = data.get('data', [])
                
                for lead in leads:
                    lead['form_name'] = form['name']
                    all_leads.append(lead)
                
                # Check for next page
                next_url = data.get('paging', {}).get('next')
        
        return {'leads': all_leads, 'total': len(all_leads)}
    
    def get_ad_spend_data(self, account_id, date_range_days=30):
        """Get ad spend by campaign, adset, and ad"""
        since = (datetime.now() - timedelta(days=date_range_days)).strftime('%Y-%m-%d')
        until = datetime.now().strftime('%Y-%m-%d')
        
        # Get campaigns with spend
        campaigns_url = f"{self.base_url}/act_{account_id}/campaigns"
        campaigns_response = requests.get(campaigns_url, params={
            'access_token': self.access_token,
            'fields': 'id,name,status,insights{spend,impressions,clicks,cpm,cpc,ctr}',
            'time_range': f'{{"since":"{since}","until":"{until}"}}'
        })
        
        if campaigns_response.status_code != 200:
            return {'error': f'Campaigns API error: {campaigns_response.text}'}
        
        campaigns = campaigns_response.json().get('data', [])
        
        # Get adsets with spend
        adsets_url = f"{self.base_url}/act_{account_id}/adsets"
        adsets_response = requests.get(adsets_url, params={
            'access_token': self.access_token,
            'fields': 'id,name,campaign_id,status,insights{spend,impressions,clicks,cpm,cpc,ctr}',
            'time_range': f'{{"since":"{since}","until":"{until}"}}'
        })
        
        adsets = adsets_response.json().get('data', []) if adsets_response.status_code == 200 else []
        
        # Get ads with spend
        ads_url = f"{self.base_url}/act_{account_id}/ads"
        ads_response = requests.get(ads_url, params={
            'access_token': self.access_token,
            'fields': 'id,name,adset_id,campaign_id,status,insights{spend,impressions,clicks,cpm,cpc,ctr}',
            'time_range': f'{{"since":"{since}","until":"{until}"}}'
        })
        
        ads = ads_response.json().get('data', []) if ads_response.status_code == 200 else []
        
        return {
            'campaigns': campaigns,
            'adsets': adsets,
            'ads': ads,
            'date_range': {'since': since, 'until': until}
        }
    
    def sync_leads_with_spend(self, page_id, account_id):
        """Sync leads and match with spend data"""
        # Get all leads
        leads_result = self.get_all_leads(page_id)
        if 'error' in leads_result:
            return leads_result
        
        # Get spend data
        spend_result = self.get_ad_spend_data(account_id)
        if 'error' in spend_result:
            return spend_result
        
        # Create lookup dictionaries for spend data
        campaign_spend = {c['id']: c for c in spend_result['campaigns']}
        adset_spend = {a['id']: a for a in spend_result['adsets']}
        ad_spend = {a['id']: a for a in spend_result['ads']}
        
        # Enrich leads with spend data
        enriched_leads = []
        for lead in leads_result['leads']:
            enriched_lead = lead.copy()
            
            # Add campaign spend data
            if lead.get('campaign_id') in campaign_spend:
                enriched_lead['campaign_data'] = campaign_spend[lead['campaign_id']]
            
            # Add adset spend data
            if lead.get('adset_id') in adset_spend:
                enriched_lead['adset_data'] = adset_spend[lead['adset_id']]
            
            # Add ad spend data
            if lead.get('ad_id') in ad_spend:
                enriched_lead['ad_data'] = ad_spend[lead['ad_id']]
            
            enriched_leads.append(enriched_lead)
        
        return {
            'leads': enriched_leads,
            'total_leads': len(enriched_leads),
            'spend_summary': spend_result
        }

# Usage example
if __name__ == "__main__":
    ACCESS_TOKEN = "EAAgVjAbsIWoBPw4ggkNHJaO3igkkILRQ1ccESdGdhJp7wrZAHYIExnD2xbvZCxHXPQZAzvtd4nxDq2gj3STKTpcs9CMfv9YjZAf507vQIkwKYZBzCzqhKHcpa1wDecXRBxLx4YH3AUG1QzeMxfUZCF7EsJtVwwTMZBpwf6xavBZBx9N6EplcTeL0CuZBDDKa83JxEpXAwOhT6KFQ0SNbvp3GUliKIz6WrWhLsIATtGed2hQ3egRo4W49cVlD6vfdJOZB5vYZBseuk155XLFjVrFdsU6LAZDZD"
    PAGE_ID = "YOUR_PAGE_ID"
    ACCOUNT_ID = "YOUR_AD_ACCOUNT_ID"
    
    client = EnhancedMetaClient(ACCESS_TOKEN)
    result = client.sync_leads_with_spend(PAGE_ID, ACCOUNT_ID)
    print(f"Synced {result.get('total_leads', 0)} leads with spend data")