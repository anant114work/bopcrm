#!/usr/bin/env python
"""
Fix Google Sheets sync duplicate detection
"""

import os
import sys
import django
from datetime import datetime, date

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import Lead
from django.utils import timezone

def add_missing_leads():
    """Add all missing leads from your Google Sheets data"""
    
    # All leads from your data that should exist
    all_leads = [
        # Dec 15 leads
        {'date': '15/12/2025', 'time': '08:01:36', 'name': 'Suman Kumar', 'phone': '8540863684', 'email': 'aabusuman969@gmail.com'},
        {'date': '15/12/2025', 'time': '08:02:20', 'name': 'Suman Kumar', 'phone': '8540863684', 'email': 'aabusuman969@gmail.com'},
        {'date': '15/12/2025', 'time': '08:27:38', 'name': 'Sunil Mehra', 'phone': '9814109060', 'email': 'sunilmehra_asr@yahoo.co.in'},
        
        # Dec 14 leads
        {'date': '14/12/2025', 'time': '09:45:34', 'name': 'Ramesh', 'phone': '8588891402', 'email': 'ramesh.bhatt@hotmail.com'},
        {'date': '14/12/2025', 'time': '11:22:03', 'name': 'Nitish Kumar', 'phone': '9870591651', 'email': 'nitishregal@gmail.com'},
        {'date': '14/12/2025', 'time': '11:51:04', 'name': 'Vikas Jaiswal', 'phone': '8146161418', 'email': 'vikasatc@gmail.com'},
        {'date': '14/12/2025', 'time': '12:48:14', 'name': 'D k thakur', 'phone': '9711847767', 'email': 'hemthaku_1972@rediffmail.com'},
        {'date': '14/12/2025', 'time': '14:43:30', 'name': 'Dalip', 'phone': '9650998025', 'email': 'dalip.ntpc@gmail.com'},
        {'date': '14/12/2025', 'time': '15:30:14', 'name': 'Naveen Sharma', 'phone': '7678636992', 'email': 'naveen1291985@gmail.com'},
        {'date': '14/12/2025', 'time': '15:41:51', 'name': 'Sunny kumar', 'phone': '7042326996', 'email': 'cadhimansunny@gmail.com'},
    ]
    
    created_count = 0
    existing_count = 0
    
    for lead_data in all_leads:
        # Parse date and time
        try:
            date_str = lead_data['date']  # DD/MM/YYYY
            time_str = lead_data['time']  # HH:MM:SS
            
            day, month, year = date_str.split('/')
            hour, minute, second = time_str.split(':')
            
            created_time = datetime(
                int(year), int(month), int(day),
                int(hour), int(minute), int(second)
            )
            
            # Check if lead exists (by phone number)
            phone_digits = ''.join(filter(str.isdigit, lead_data['phone']))
            existing = Lead.objects.filter(
                phone_number__iregex=f'.*{phone_digits}.*'
            ).first()
            
            if existing:
                existing_count += 1
                print(f"⚠️ Exists: {lead_data['name']} ({lead_data['phone']})")
                continue
            
            # Create new lead
            lead_id = f"GOOGLE_{year}{month}{day}_{hour}{minute}{second}_{phone_digits[-4:]}"
            
            lead = Lead.objects.create(
                lead_id=lead_id,
                full_name=lead_data['name'],
                phone_number=f"+91{phone_digits}" if len(phone_digits) == 10 else lead_data['phone'],
                email=lead_data['email'],
                source='Google Sheets',
                form_name='Google Sheets - AU Aspire Leisure Valley',
                created_time=created_time
            )
            
            created_count += 1
            print(f"✅ Created: {lead_data['name']} ({lead_data['phone']}) - {date_str} {time_str}")
            
        except Exception as e:
            print(f"❌ Error creating {lead_data['name']}: {str(e)}")
            continue
    
    print(f"\n🎉 Summary:")
    print(f"   ✅ Created: {created_count} new leads")
    print(f"   ⚠️ Already existed: {existing_count} leads")

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 ADDING MISSING GOOGLE SHEETS LEADS")
    print("=" * 60)
    
    add_missing_leads()
    
    print("\n" + "=" * 60)