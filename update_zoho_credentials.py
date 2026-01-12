#!/usr/bin/env python3
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import ZohoConfig

def update_zoho_credentials():
    """Update Zoho credentials with new Client ID and Secret"""
    
    # New credentials from your Zoho console
    new_client_id = "1000.N86NWH8YA8XTVCQ2LPIUGV3V8L8LNA"
    new_client_secret = "97e14674507d101d6b86e8a695c9cf097f7f38db8e"
    
    try:
        config = ZohoConfig.objects.first()
        if config:
            # Update with new credentials
            config.client_id = new_client_id
            config.client_secret = new_client_secret
            config.access_token = ''  # Clear old token
            config.refresh_token = ''  # Clear old token
            config.save()
            print("Zoho credentials updated successfully!")
            print(f"New Client ID: {new_client_id}")
        else:
            # Create new config
            ZohoConfig.objects.create(
                client_id=new_client_id,
                client_secret=new_client_secret,
                redirect_uri="http://localhost:8000/zoho-callback/",
                is_active=True
            )
            print("New Zoho config created!")
        
        print("\nNext steps:")
        print("1. Go to: http://localhost:8000/zoho-config/")
        print("2. Click 'Authorize with Zoho'")
        print("3. Complete OAuth flow")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    update_zoho_credentials()