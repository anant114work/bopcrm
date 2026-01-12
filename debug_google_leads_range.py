#!/usr/bin/env python
import os
import sys
import django
from datetime import date, datetime

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import Lead
from leads.project_models import Project

def debug_google_leads():
    print("🔍 DEBUGGING GOOGLE LEADS DATE RANGE ISSUE")
    print("=" * 60)
    
    # Get the AU project
    try:
        project = Project.objects.get(name__icontains='AU Aspire')
        print(f"📋 Project: {project.name}")
    except Project.DoesNotExist:
        print("❌ AU Aspire project not found")
        return
    
    # Check date range Dec 12-15, 2025
    from_date = datetime.strptime('2025-12-12', '%Y-%m-%d').date()
    to_date = datetime.strptime('2025-12-15', '%Y-%m-%d').date()
    
    print(f"📅 Date Range: {from_date} to {to_date}")
    
    # Get all leads in this date range
    all_leads_in_range = project.get_leads().filter(
        created_time__date__gte=from_date,
        created_time__date__lte=to_date
    )
    
    print(f"📊 Total leads in range: {all_leads_in_range.count()}")
    
    # Get Google leads in this range
    google_leads_in_range = all_leads_in_range.filter(source='Google Sheets')
    print(f"🟢 Google leads in range: {google_leads_in_range.count()}")
    
    # Get Google leads with phone numbers
    google_leads_with_phone = google_leads_in_range.filter(
        phone_number__isnull=False
    ).exclude(phone_number='')
    
    print(f"📞 Google leads with phone: {google_leads_with_phone.count()}")
    
    # Show some examples
    print("\n📋 Sample Google leads with phones:")
    for lead in google_leads_with_phone[:5]:
        print(f"  - {lead.full_name}: {lead.phone_number} ({lead.created_time.date()})")
    
    # Check what's being excluded
    from leads.models import CallLog
    today = date.today()
    
    called_today_raw = CallLog.objects.filter(
        initiated_at__date=today,
        call_type__startswith='auto_daily',
        status='initiated'
    ).values_list('phone_number', flat=True)
    
    excluded_numbers = ['919955967814', '917943595065', '+919955967814', '+917943595065']
    for phone in called_today_raw:
        excluded_numbers.append(phone)
        if phone.startswith('+91'):
            excluded_numbers.append(phone[3:])
        elif phone.startswith('91') and len(phone) == 12:
            excluded_numbers.append(f'+{phone}')
        elif len(phone) == 10:
            excluded_numbers.append(f'+91{phone}')
            excluded_numbers.append(f'91{phone}')
    
    print(f"\n🚫 Excluded numbers count: {len(excluded_numbers)}")
    print("🚫 Sample excluded numbers:")
    for num in excluded_numbers[:10]:
        print(f"  - {num}")
    
    # Final filtered count
    final_google_leads = google_leads_with_phone.exclude(phone_number__in=excluded_numbers)
    print(f"\n✅ Final callable Google leads: {final_google_leads.count()}")
    
    if final_google_leads.count() == 0:
        print("\n❌ NO CALLABLE GOOGLE LEADS FOUND!")
        print("🔍 Checking if all numbers are excluded...")
        
        for lead in google_leads_with_phone:
            if lead.phone_number in excluded_numbers:
                print(f"  ❌ {lead.full_name} ({lead.phone_number}) - EXCLUDED")
            else:
                print(f"  ✅ {lead.full_name} ({lead.phone_number}) - AVAILABLE")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    debug_google_leads()