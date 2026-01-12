#!/usr/bin/env python3
"""
Fix Zoho token issues and test connection
"""

import os
import sys
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import ZohoConfig

def refresh_zoho_token():
    """Refresh expired Zoho access token"""
    config = ZohoConfig.objects.first()
    if not config:
        print("ERROR: No Zoho config found")
        return False
    
    if not config.refresh_token:
        print("ERROR: No refresh token available - need to re-authorize")
        return False
    
    print("Refreshing Zoho access token...")
    
    # Use India datacenter for token refresh
    token_url = "https://accounts.zoho.in/oauth/v2/token"
    
    data = {
        'client_id': config.client_id,
        'client_secret': config.client_secret,
        'grant_type': 'refresh_token',
        'refresh_token': config.refresh_token
    }
    
    try:
        response = requests.post(token_url, data=data, timeout=10)
        result = response.json()
        
        if response.status_code == 200 and 'access_token' in result:
            # Update access token
            config.access_token = result['access_token']
            config.save()
            
            print("SUCCESS: Token refreshed successfully!")
            print(f"   New token: {config.access_token[:20]}...")
            return True
        else:
            print(f"ERROR: Token refresh failed: {result}")
            return False
            
    except Exception as e:
        print(f"ERROR: Error refreshing token: {e}")
        return False

def test_zoho_connection():
    """Test Zoho API connection with proper endpoints"""
    config = ZohoConfig.objects.first()
    if not config or not config.access_token:
        print("ERROR: No valid Zoho config")
        return False
    
    print("Testing Zoho API connection...")
    
    headers = {
        'Authorization': f'Zoho-oauthtoken {config.access_token}',
        'Content-Type': 'application/json'
    }
    
    # Test CRM API (correct endpoint for India)
    test_url = "https://www.zohoapis.in/crm/v8/users"
    
    try:
        response = requests.get(test_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            users = data.get('users', [])
            print(f"SUCCESS: Connection successful! Found {len(users)} users")
            return True
        elif response.status_code == 401:
            print("ERROR: Invalid token - attempting refresh...")
            if refresh_zoho_token():
                return test_zoho_connection()  # Retry with new token
            return False
        else:
            print(f"ERROR: API Error: {response.status_code} - {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"ERROR: Connection error: {e}")
        return False

def sync_test_lead():
    """Sync a test lead to Zoho CRM"""
    config = ZohoConfig.objects.first()
    if not config or not config.access_token:
        print("ERROR: No valid Zoho config")
        return False
    
    print("Testing lead sync to Zoho CRM...")
    
    headers = {
        'Authorization': f'Zoho-oauthtoken {config.access_token}',
        'Content-Type': 'application/json'
    }
    
    # Create test lead data
    lead_data = {
        "data": [{
            "Last_Name": "Test Lead",
            "Email": "test@example.com", 
            "Phone": "1234567890",
            "Lead_Source": "CRM Integration Test",
            "City": "Test City",
            "Description": "Test lead from CRM integration"
        }]
    }
    
    # Use CRM Leads API
    url = "https://www.zohoapis.in/crm/v8/Leads"
    
    try:
        response = requests.post(url, headers=headers, json=lead_data, timeout=10)
        
        if response.status_code in [200, 201]:
            result = response.json()
            if result.get('data') and result['data'][0].get('code') == 'SUCCESS':
                print("SUCCESS: Test lead synced successfully!")
                return True
            else:
                print(f"ERROR: Sync failed: {result}")
                return False
        elif response.status_code == 401:
            print("ERROR: Invalid token during sync - attempting refresh...")
            if refresh_zoho_token():
                return sync_test_lead()  # Retry with new token
            return False
        else:
            print(f"ERROR: Sync error: {response.status_code} - {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"ERROR: Sync error: {e}")
        return False

def main():
    print("Zoho Integration Fix & Test")
    print("=" * 40)
    
    # Step 1: Test current connection
    if not test_zoho_connection():
        print("\nERROR: Connection test failed")
        return
    
    # Step 2: Test lead sync
    if not sync_test_lead():
        print("\nERROR: Lead sync test failed")
        return
    
    print("\nSUCCESS: All tests passed! Zoho integration is working.")
    print("\nNext steps:")
    print("   1. Your Zoho integration is now fixed")
    print("   2. You can sync leads from the dashboard")
    print("   3. Token will auto-refresh when needed")

if __name__ == "__main__":
    main()