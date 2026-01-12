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

def debug_google_date_issue():
    print("🔍 DEBUGGING GOOGLE LEADS DATE ISSUE")
    print("=" * 60)
    
    # Get the AU project
    try:
        project = Project.objects.get(name__icontains='AU Aspire')
        print(f"📋 Project: {project.name}")
    except Project.DoesNotExist:
        print("❌ AU Aspire project not found")
        return
    
    # Check date range Dec 14-15, 2025
    from_date = datetime.strptime('2025-12-14', '%Y-%m-%d').date()
    to_date = datetime.strptime('2025-12-15', '%Y-%m-%d').date()
    
    print(f"📅 Date Range: {from_date} to {to_date}")
    
    # Get all Google leads in project
    all_google_leads = project.get_leads().filter(source='Google Sheets')
    print(f"📊 Total Google leads in project: {all_google_leads.count()}")
    
    # Show recent Google leads with dates
    print(f"\n📋 Recent Google leads (showing dates):")
    for lead in all_google_leads.order_by('-created_time')[:10]:
        print(f"  - {lead.full_name}: {lead.created_time} (date: {lead.created_time.date()})")
    
    # Check leads in the specific date range
    google_in_range = all_google_leads.filter(
        created_time__date__gte=from_date,
        created_time__date__lte=to_date
    )
    print(f"\n🎯 Google leads in range {from_date} to {to_date}: {google_in_range.count()}")
    
    for lead in google_in_range:
        print(f"  - {lead.full_name}: {lead.phone_number} ({lead.created_time.date()})")
    
    # Check with phone numbers
    google_with_phone = google_in_range.filter(
        phone_number__isnull=False
    ).exclude(phone_number='')
    
    print(f"\n📞 Google leads with phone in range: {google_with_phone.count()}")
    
    for lead in google_with_phone:
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
    
    print(f"\n🚫 Total excluded numbers: {len(excluded_numbers)}")
    
    # Final check after exclusions
    final_google_leads = google_with_phone.exclude(phone_number__in=excluded_numbers)
    print(f"\n✅ Final callable Google leads after exclusions: {final_google_leads.count()}")
    
    if final_google_leads.count() == 0:
        print("\n❌ NO CALLABLE GOOGLE LEADS FOUND!")
        print("🔍 Checking exclusion reasons...")
        
        for lead in google_with_phone:
            if lead.phone_number in excluded_numbers:
                print(f"  ❌ {lead.full_name} ({lead.phone_number}) - EXCLUDED (already called)")
            else:
                print(f"  ✅ {lead.full_name} ({lead.phone_number}) - SHOULD BE AVAILABLE")
    else:
        print("✅ Found callable Google leads:")
        for lead in final_google_leads:
            print(f"  - {lead.full_name}: {lead.phone_number} ({lead.created_time.date()})")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    debug_google_date_issue()