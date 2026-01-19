#!/usr/bin/env python3
"""
Diagnose Zoho integration issues
"""

import os
import sys
import django
import requests

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import ZohoConfig

def check_zoho_config():
    """Check current Zoho configuration"""
    print("Checking Zoho Configuration")
    print("=" * 40)
    
    config = ZohoConfig.objects.first()
    if not config:
        print("ERROR: No Zoho configuration found")
        return None
    
    print(f"Client ID: {config.client_id[:20]}...")
    print(f"Client Secret: {'*' * 20}")
    print(f"Redirect URI: {config.redirect_uri}")
    print(f"API Domain: {config.api_domain}")
    print(f"Has Access Token: {bool(config.access_token)}")
    print(f"Has Refresh Token: {bool(config.refresh_token)}")
    
    if config.access_token:
        print(f"Access Token (first 30 chars): {config.access_token[:30]}...")
    
    if config.refresh_token:
        print(f"Refresh Token (first 30 chars): {config.refresh_token[:30]}...")
    
    return config

def test_simple_api_call(config):
    """Test a simple API call to see exact error"""
    print("\nTesting Simple API Call")
    print("=" * 40)
    
    if not config or not config.access_token:
        print("ERROR: No access token to test")
        return
    
    headers = {
        'Authorization': f'Zoho-oauthtoken {config.access_token}',
        'Content-Type': 'application/json'
    }
    
    # Try the simplest possible endpoint
    test_url = "https://www.zohoapis.in/crm/v8/users"
    
    try:
        print(f"Making request to: {test_url}")
        print(f"Authorization header: Zoho-oauthtoken {config.access_token[:20]}...")
        
        response = requests.get(test_url, headers=headers, timeout=10)
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text[:500]}...")
        
        if response.status_code == 200:
            print("SUCCESS: API call worked!")
            return True
        elif response.status_code == 401:
            print("ERROR: 401 Unauthorized - Token is invalid or expired")
            
            # Try to parse the error
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print("Could not parse error response as JSON")
                
        else:
            print(f"ERROR: Unexpected status code {response.status_code}")
            
    except Exception as e:
        print(f"ERROR: Exception during API call: {e}")
    
    return False

def check_token_validity(config):
    """Check if tokens are in correct format"""
    print("\nChecking Token Validity")
    print("=" * 40)
    
    if not config:
        return
    
    # Zoho access tokens should be in format: 1000.xxxxx.xxxxx
    if config.access_token:
        parts = config.access_token.split('.')
        if len(parts) == 3 and parts[0] == '1000':
            print("Access token format: VALID")
        else:
            print("Access token format: INVALID (should be 1000.xxxxx.xxxxx)")
    
    if config.refresh_token:
        parts = config.refresh_token.split('.')
        if len(parts) == 3 and parts[0] == '1000':
            print("Refresh token format: VALID")
        else:
            print("Refresh token format: INVALID (should be 1000.xxxxx.xxxxx)")

def suggest_solutions():
    """Suggest solutions based on findings"""
    print("\nSuggested Solutions")
    print("=" * 40)
    
    print("1. RE-AUTHORIZE ZOHO:")
    print("   - Go to /zoho-config/ in your app")
    print("   - Click 'Authorize Zoho'")
    print("   - Complete OAuth flow again")
    print("   - This will get fresh access + refresh tokens")
    
    print("\n2. CHECK SCOPES:")
    print("   - Ensure you have ZohoCRM.modules.ALL scope")
    print("   - Your app needs CRM permissions")
    
    print("\n3. VERIFY REGION:")
    print("   - You're using India (.in) datacenter")
    print("   - Make sure your Zoho account is in India region")
    
    print("\n4. ALTERNATIVE - CSV EXPORT:")
    print("   - Export leads to CSV")
    print("   - Manually import to Zoho CRM")
    print("   - Bypass API integration issues")

def main():
    print("Zoho Integration Diagnostic Tool")
    print("=" * 50)
    
    config = check_zoho_config()
    
    if config:
        check_token_validity(config)
        test_simple_api_call(config)
    
    suggest_solutions()
    
    print("\n" + "=" * 50)
    print("Diagnostic complete!")

if __name__ == "__main__":
    main()