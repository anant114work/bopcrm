#!/usr/bin/env python3
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import ZohoConfig

def reset_zoho_config():
    """Reset Zoho configuration to force re-authorization"""
    try:
        config = ZohoConfig.objects.first()
        if config:
            # Clear tokens but keep client credentials
            config.access_token = ''
            config.refresh_token = ''
            config.save()
            print("Zoho tokens cleared. Please re-authorize.")
            print("Go to: http://localhost:8000/zoho-config/")
        else:
            print("No Zoho config found.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    reset_zoho_config()