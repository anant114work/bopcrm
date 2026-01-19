#!/usr/bin/env python
"""
Debug script to see phone number formats and fix matching
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.call_report_models import CallReportRecord
from leads.models import Lead

def debug_phone_formats():
    """Show phone number formats from both sources"""
    print("📞 CALL REPORT PHONE NUMBERS:")
    call_records = CallReportRecord.objects.all()[:10]
    for record in call_records:
        digits = ''.join(filter(str.isdigit, str(record.phone_number)))
        print(f"   {record.phone_number} → digits: {digits} → last10: {digits[-10:] if len(digits) >= 10 else 'N/A'}")
    
    print("\n📞 LEAD PHONE NUMBERS:")
    leads = Lead.objects.filter(phone_number__isnull=False).exclude(phone_number='')[:10]
    for lead in leads:
        digits = ''.join(filter(str.isdigit, str(lead.phone_number)))
        print(f"   {lead.phone_number} ({lead.full_name}) → digits: {digits} → last10: {digits[-10:] if len(digits) >= 10 else 'N/A'}")

def force_match_all():
    """Force match all records by any means necessary"""
    print("\n🔧 FORCE MATCHING ALL RECORDS...")
    
    unmatched = CallReportRecord.objects.filter(is_matched=False)
    print(f"Found {unmatched.count()} unmatched records")
    
    # Get all leads for comparison
    all_leads = list(Lead.objects.filter(phone_number__isnull=False).exclude(phone_number=''))
    print(f"Found {len(all_leads)} leads with phone numbers")
    
    matched_count = 0
    
    for record in unmatched:
        call_phone = str(record.phone_number).strip()
        call_digits = ''.join(filter(str.isdigit, call_phone))
        
        if len(call_digits) < 10:
            continue
            
        call_last10 = call_digits[-10:]
        
        # Try to match with any lead
        matched_lead = None
        
        for lead in all_leads:
            lead_digits = ''.join(filter(str.isdigit, str(lead.phone_number)))
            
            if len(lead_digits) >= 10:
                lead_last10 = lead_digits[-10:]
                
                # Match if last 10 digits are same
                if call_last10 == lead_last10:
                    matched_lead = lead
                    break
        
        if matched_lead:
            record.matched_lead = matched_lead
            record.is_matched = True
            record.save()
            matched_count += 1
            print(f"✅ MATCHED: {call_phone} → {matched_lead.phone_number} ({matched_lead.full_name})")
        else:
            print(f"❌ NO MATCH: {call_phone} (digits: {call_digits})")
    
    print(f"\n🎉 Successfully matched {matched_count} records!")
    
    # Final stats
    total = CallReportRecord.objects.count()
    matched = CallReportRecord.objects.filter(is_matched=True).count()
    rate = (matched / total * 100) if total > 0 else 0
    
    print(f"\n📊 FINAL STATISTICS:")
    print(f"   Total Records: {total}")
    print(f"   Matched Records: {matched}")
    print(f"   Success Rate: {rate:.1f}%")

if __name__ == "__main__":
    print("=" * 60)
    print("🔍 PHONE NUMBER MATCHING DEBUG")
    print("=" * 60)
    
    debug_phone_formats()
    force_match_all()
    
    print("\n" + "=" * 60)