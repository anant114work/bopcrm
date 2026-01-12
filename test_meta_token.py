#!/usr/bin/env python
"""
Test Meta API connection and provide token refresh instructions
"""
import os
import django
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.meta_sync import META_ACCESS_TOKEN, META_PAGE_ID

print("Meta API Connection Test")
print("=" * 50)
print(f"Page ID: {META_PAGE_ID}")
print(f"Token: {META_ACCESS_TOKEN[:20]}...{META_ACCESS_TOKEN[-10:]}")
print()

# Test token validity
url = f"https://graph.facebook.com/v18.0/me"
params = {'access_token': META_ACCESS_TOKEN}

try:
    response = requests.get(url, params=params, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        print("Token is VALID")
        print(f"  User: {data.get('name', 'Unknown')}")
        print(f"  ID: {data.get('id', 'Unknown')}")
    else:
        print("Token is INVALID")
        print(f"  Status: {response.status_code}")
        print(f"  Error: {response.text}")
        
        print("\n" + "=" * 50)
        print("TOKEN REFRESH INSTRUCTIONS:")
        print("=" * 50)
        print("1. Go to: https://developers.facebook.com/tools/explorer/")
        print("2. Select your app and page")
        print("3. Add permissions: pages_read_engagement, leads_retrieval")
        print("4. Generate new access token")
        print("5. Update META_ACCESS_TOKEN in meta_sync.py")
        print("6. Run this script again to test")
        
except Exception as e:
    print(f"Connection Error: {str(e)}")

print("\n" + "=" * 50)