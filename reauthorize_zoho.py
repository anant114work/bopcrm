#!/usr/bin/env python3
"""
Re-authorize Zoho with correct scopes
"""

import os
import sys
import django
import urllib.parse

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import ZohoConfig

def generate_auth_url():
    """Generate the correct authorization URL"""
    config = ZohoConfig.objects.first()
    if not config:
        print("ERROR: No Zoho configuration found")
        print("Please go to /zoho-config/ first to set up client credentials")
        return None
    
    # Comprehensive scopes for Zoho CRM
    scopes = "ZohoCRM.modules.ALL,ZohoCRM.settings.ALL,ZohoCRM.users.ALL,ZohoCRM.org.ALL"
    
    auth_url = (
        f"https://accounts.zoho.in/oauth/v2/auth"
        f"?response_type=code"
        f"&client_id={config.client_id}"
        f"&scope={scopes}"
        f"&redirect_uri={urllib.parse.quote(config.redirect_uri)}"
        f"&access_type=offline"
    )
    
    return auth_url

def main():
    print("Zoho Re-Authorization Helper")
    print("=" * 40)
    
    auth_url = generate_auth_url()
    
    if auth_url:
        print("STEP 1: Copy this URL and open it in your browser:")
        print("-" * 60)
        print(auth_url)
        print("-" * 60)
        
        print("\nSTEP 2: Complete the authorization in your browser")
        print("- Log in to your Zoho account")
        print("- Accept the permissions")
        print("- You'll be redirected back to your app")
        
        print("\nSTEP 3: After authorization, test the connection")
        print("- Go to /zoho-status/ in your app")
        print("- Click 'Test Connection'")
        print("- Should now work with proper scopes!")
        
        print("\nAlternatively, you can:")
        print("1. Go to http://127.0.0.1:8000/zoho-config/")
        print("2. Click 'Authorize Zoho' button")
        print("3. Complete the OAuth flow")
    
    print("\n" + "=" * 40)

if __name__ == "__main__":
    main()