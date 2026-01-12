#!/usr/bin/env python3
import os
import sys
import django
import requests

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import ZohoConfig

def test_zoho_simple():
    """Simple test without complex API calls"""
    config = ZohoConfig.objects.first()
    if not config or not config.access_token:
        print("No Zoho config found")
        return
    
    print(f"Testing with token: {config.access_token[:20]}...")
    
    # Try a very simple API call
    headers = {'Authorization': f'Zoho-oauthtoken {config.access_token}'}
    
    # Test with a basic endpoint
    test_urls = [
        "https://www.zohoapis.in/marketingautomation/v1/getmailinglists.json",
        "https://accounts.zoho.in/oauth/user/info"  # Simple user info endpoint
    ]
    
    for url in test_urls:
        print(f"\nTesting: {url}")
        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
            if response.status_code == 200:
                print("SUCCESS!")
                return True
            elif response.status_code == 400:
                print("Bad Request - API endpoint or parameters incorrect")
            elif response.status_code == 401:
                print("Unauthorized - Token invalid or expired")
            else:
                print(f"Error: {response.status_code}")
                
        except Exception as e:
            print(f"Exception: {e}")
    
    return False

def create_simple_integration():
    """Create a simple CSV export instead of API integration"""
    print("\n" + "="*50)
    print("ALTERNATIVE SOLUTION: CSV Export for Zoho")
    print("="*50)
    
    from leads.models import Lead
    import csv
    from datetime import datetime
    
    # Export leads to CSV format that can be imported to Zoho
    leads = Lead.objects.filter(email__isnull=False).exclude(email='')[:10]
    
    filename = f"zoho_leads_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Zoho Marketing Automation CSV headers
        writer.writerow([
            'Contact Email', 'First Name', 'Last Name', 'Phone', 
            'Lead Source', 'City', 'Configuration', 'Company'
        ])
        
        for lead in leads:
            name_parts = (lead.full_name or '').split(' ', 1)
            first_name = name_parts[0] if name_parts else ''
            last_name = name_parts[1] if len(name_parts) > 1 else ''
            
            writer.writerow([
                lead.email or '',
                first_name,
                last_name,
                lead.phone_number or '',
                lead.form_name or 'CRM Import',
                lead.city or '',
                lead.configuration or '',
                'Lead from CRM'
            ])
    
    print(f"Created: {filename}")
    print(f"Exported {len(leads)} leads")
    print("\nManual Import Steps:")
    print("1. Go to Zoho Marketing Automation")
    print("2. Navigate to Contacts > Import")
    print(f"3. Upload the file: {filename}")
    print("4. Map the columns and import")
    
    return filename

if __name__ == "__main__":
    print("Testing Zoho Marketing Automation Connection")
    print("="*50)
    
    success = test_zoho_simple()
    
    if not success:
        print("\nSince API integration has issues with localhost,")
        print("   creating CSV export as alternative solution...")
        create_simple_integration()
    
    print("\nTest complete!")