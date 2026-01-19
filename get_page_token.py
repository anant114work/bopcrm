#!/usr/bin/env python
"""
Get Page Access Token from User Access Token
"""
import requests

USER_ACCESS_TOKEN = "EAAgVjAbsIWoBQOC73ozqLuI0jSx9ZCLf6tBt2jxEvhbu5JwBELE9jHJYbVBt0pC4PslMy7y4nH3GOojo5zuMFKdzZCs4rtUYfyVbleQidrvKcQQLAhZBgK6jrZCOBd3HotiOitOnJr4OsYO8DmLAqhCCS8OHgosiZCrRtKgI8dBwZCZCYFoMWFgCYQG3duhlvB5"
PAGE_ID = "296508423701621"

print("Getting Page Access Token")
print("=" * 40)

# Step 1: Get user's pages
print("1. Getting user pages...")
url = "https://graph.facebook.com/v18.0/me/accounts"
params = {
    'access_token': USER_ACCESS_TOKEN,
    'fields': 'id,name,access_token'
}

try:
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        pages = data.get('data', [])
        
        print(f"Found {len(pages)} pages:")
        
        page_token = None
        for page in pages:
            page_id = page.get('id')
            page_name = page.get('name')
            page_access_token = page.get('access_token')
            
            print(f"  - {page_name} (ID: {page_id})")
            
            if page_id == PAGE_ID:
                page_token = page_access_token
                print(f"    FOUND TARGET PAGE!")
                print(f"    Page Token: {page_access_token[:30]}...")
        
        if page_token:
            print("\n" + "=" * 40)
            print("PAGE ACCESS TOKEN FOUND!")
            print("=" * 40)
            print("Update your .env file with:")
            print(f"META_ACCESS_TOKEN={page_token}")
            print("\nThen run the sync again.")
        else:
            print(f"\nPage {PAGE_ID} not found in your pages.")
            print("Make sure you have admin access to the page.")
    
    else:
        print(f"Error: {response.status_code}")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"Error: {str(e)}")

print("=" * 40)