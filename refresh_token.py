import requests
from leads.models import ZohoConfig

def refresh_zoho_token(config):
    """Refresh Zoho access token using refresh token"""
    if not config.refresh_token:
        return False
    
    try:
        if 'zoho.in' in config.api_domain:
            token_url = "https://accounts.zoho.in/oauth/v2/token"
        else:
            token_url = "https://accounts.zoho.com/oauth/v2/token"
        
        data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': config.refresh_token
        }
        
        response = requests.post(token_url, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            if 'access_token' in token_data:
                config.access_token = token_data['access_token']
                config.save()
                return True
    except:
        pass
    
    return False

# Add this function to views.py
refresh_function = '''
def refresh_zoho_token(config):
    """Refresh Zoho access token using refresh token"""
    if not config.refresh_token:
        return False
    
    try:
        if 'zoho.in' in config.api_domain:
            token_url = "https://accounts.zoho.in/oauth/v2/token"
        else:
            token_url = "https://accounts.zoho.com/oauth/v2/token"
        
        data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': config.refresh_token
        }
        
        response = requests.post(token_url, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            if 'access_token' in token_data:
                config.access_token = token_data['access_token']
                config.save()
                return True
    except:
        pass
    
    return False
'''

print("Add this function to your views.py file:")
print(refresh_function)