#!/usr/bin/env python3
"""
Test script to verify Zoho Marketing Automation fixes
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import ZohoConfig, Lead
import requests
import json

def test_zoho_endpoints():
    """Test the corrected Zoho API endpoints"""
    
    print("Testing Zoho Marketing Automation API endpoints...")
    
    # Test endpoints - correct Zoho Marketing Automation format
    endpoints = {
        'India': 'https://marketingautomation.zoho.in/api/v1/getmailinglists.json',
        'Global': 'https://marketingautomation.zoho.com/api/v1/getmailinglists.json'
    }
    
    for region, url in endpoints.items():
        print(f"\nTesting {region} endpoint: {url}")
        
        # Test without auth (should get 401)
        try:
            response = requests.get(url, timeout=10)
            print(f"   Status: {response.status_code}")
            if response.status_code == 401:
                print("   OK: Endpoint is valid (401 = needs auth)")
            else:
                print(f"   WARNING: Unexpected status: {response.status_code}")
        except Exception as e:
            print(f"   ERROR: {e}")
    
    print("\n" + "="*50)
    
def test_lead_data_format():
    """Test the corrected lead data format"""
    
    print("Testing lead data format for Zoho...")
    
    # Sample lead data
    sample_lead_data = {
        'listkey': '1892576000000008001',
        'contactinfo': json.dumps({
            'Contact Email': 'test@example.com',
            'First Name': 'Test User',
            'Phone': '+1234567890',
            'Lead Source': 'CRM Import',
            'City': 'Test City',
            'Configuration': 'Test Config'
        })
    }
    
    print("Sample lead data structure:")
    print(json.dumps(sample_lead_data, indent=2))
    
    print("\n" + "="*50)

def check_database_config():
    """Check if Zoho config exists in database"""
    
    print("Checking Zoho configuration in database...")
    
    try:
        config = ZohoConfig.objects.first()
        if config:
            print("Zoho config found:")
            print(f"   Client ID: {config.client_id[:10]}...")
            print(f"   Has Access Token: {'Yes' if config.access_token else 'No'}")
            print(f"   API Domain: {config.api_domain or 'Not set'}")
        else:
            print("WARNING: No Zoho configuration found in database")
            print("   Please configure Zoho in the admin panel first")
    except Exception as e:
        print(f"ERROR checking config: {e}")
    
    print("\n" + "="*50)

def check_sample_leads():
    """Check if there are leads to test with"""
    
    print("Checking available leads for testing...")
    
    try:
        total_leads = Lead.objects.count()
        leads_with_email = Lead.objects.filter(email__isnull=False).exclude(email='').count()
        
        print(f"Total leads: {total_leads}")
        print(f"Leads with email: {leads_with_email}")
        
        if leads_with_email > 0:
            sample_leads = Lead.objects.filter(email__isnull=False).exclude(email='')[:3]
            print("\nSample leads for testing:")
            for lead in sample_leads:
                print(f"   • {lead.full_name or 'No Name'} - {lead.email}")
        else:
            print("WARNING: No leads with email found for testing")
            
    except Exception as e:
        print(f"ERROR checking leads: {e}")
    
    print("\n" + "="*50)

if __name__ == "__main__":
    print("Zoho Marketing Automation Fix Verification")
    print("=" * 50)
    
    test_zoho_endpoints()
    test_lead_data_format()
    check_database_config()
    check_sample_leads()
    
    print("\nVerification complete!")
    print("\nNext steps:")
    print("1. Configure Zoho credentials in /zoho-config/")
    print("2. Complete OAuth authorization")
    print("3. Test connection in /zoho-status/")
    print("4. Try syncing a lead")