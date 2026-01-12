#!/usr/bin/env python3
"""
Export leads to CSV format for Zoho CRM import
"""

import os
import sys
import django
import csv
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import Lead

def export_leads_to_csv():
    """Export leads to Zoho-compatible CSV format"""
    
    # Get leads with email addresses
    leads = Lead.objects.filter(email__isnull=False).exclude(email='')
    
    if not leads:
        print("No leads with email addresses found")
        return None
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"zoho_leads_export_{timestamp}.csv"
    
    # Zoho CRM CSV headers
    headers = [
        'Last Name', 'First Name', 'Email', 'Phone', 
        'Lead Source', 'City', 'Description', 'Company'
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        
        for lead in leads:
            # Split name into first/last
            name_parts = (lead.full_name or '').split(' ', 1)
            first_name = name_parts[0] if name_parts else ''
            last_name = name_parts[1] if len(name_parts) > 1 else name_parts[0] if name_parts else 'Unknown'
            
            writer.writerow([
                last_name,
                first_name,
                lead.email,
                lead.phone_number or '',
                lead.form_name or 'CRM Import',
                lead.city or '',
                lead.configuration or '',
                'Lead from CRM'
            ])
    
    return filename, len(leads)

def main():
    print("Zoho CRM Lead Export Tool")
    print("=" * 40)
    
    result = export_leads_to_csv()
    
    if result:
        filename, count = result
        print(f"SUCCESS: Exported {count} leads to {filename}")
        
        print("\nManual Import Instructions:")
        print("1. Log in to Zoho CRM")
        print("2. Go to Leads module")
        print("3. Click 'Import' button")
        print(f"4. Upload the file: {filename}")
        print("5. Map the columns:")
        print("   - Last Name -> Last Name")
        print("   - First Name -> First Name") 
        print("   - Email -> Email")
        print("   - Phone -> Phone")
        print("   - Lead Source -> Lead Source")
        print("   - City -> City")
        print("   - Description -> Description")
        print("6. Complete the import")
        
        print(f"\nFile location: {os.path.abspath(filename)}")
    else:
        print("No leads to export")

if __name__ == "__main__":
    main()