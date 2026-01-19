#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import Lead
from leads.call_report_models import CallReportRecord

def test_call_report_matching():
    print("🧪 TESTING CALL REPORT MATCHING LOGIC")
    print("=" * 60)
    
    # Build lead lookup (same as in call_report_views.py)
    print("Building lead lookup...")
    all_leads = Lead.objects.filter(phone_number__isnull=False).exclude(phone_number='')
    lead_lookup = {}
    
    for lead in all_leads:
        lead_digits = ''.join(filter(str.isdigit, str(lead.phone_number)))
        if len(lead_digits) >= 10:
            key = lead_digits[-10:]
            if key not in lead_lookup:
                lead_lookup[key] = []
            lead_lookup[key].append(lead)
    
    print(f"Built lookup for {len(all_leads)} leads")
    
    # Test with some sample phone numbers from your output
    test_phones = [
        "16395068729.0",
        "917290007968.0", 
        "917088845807.0",
        "918448734630.0",
        "919798770967.0",
        "19129784148.0",
        "919679824614.0",
        "919140980043.0",
        "918955351317.0"
    ]
    
    print(f"\n🔍 Testing {len(test_phones)} phone numbers:")
    print("-" * 40)
    
    matched_count = 0
    
    for phone in test_phones:
        matched = False
        
        # Extract digits
        phone_clean = ''.join(filter(str.isdigit, phone.replace('.0', '')))
        
        # Try direct lookup
        if len(phone_clean) >= 10:
            search_key = phone_clean[-10:]
            if search_key in lead_lookup:
                matched_lead = lead_lookup[search_key][0]
                print(f"✅ {phone} → {matched_lead.phone_number} ({matched_lead.full_name})")
                matched = True
                matched_count += 1
        
        # Try float conversion if no match
        if not matched:
            try:
                phone_float = float(phone)
                phone_str = str(int(phone_float))
                if len(phone_str) >= 10:
                    search_key = phone_str[-10:]
                    if search_key in lead_lookup:
                        matched_lead = lead_lookup[search_key][0]
                        print(f"✅ {phone} → {matched_lead.phone_number} ({matched_lead.full_name}) [float conversion]")
                        matched = True
                        matched_count += 1
            except (ValueError, TypeError):
                pass
        
        if not matched:
            print(f"❌ {phone} → No match found")
    
    print("-" * 40)
    print(f"📊 Results: {matched_count}/{len(test_phones)} matched ({matched_count/len(test_phones)*100:.1f}%)")
    
    # Check existing unmatched call reports
    unmatched_reports = CallReportRecord.objects.filter(is_matched=False)
    print(f"\n📋 Current unmatched call reports: {unmatched_reports.count()}")
    
    if unmatched_reports.exists():
        print("Sample unmatched numbers:")
        for record in unmatched_reports[:5]:
            print(f"  - {record.phone_number}")

if __name__ == "__main__":
    test_call_report_matching()