#!/usr/bin/env python
"""
Fix Excel phone number matching - remove .0 and match properly
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

def fix_excel_matching():
    """Fix Excel phone matching by handling .0 suffix"""
    print("🔧 FIXING EXCEL PHONE MATCHING...")
    
    unmatched = CallReportRecord.objects.filter(is_matched=False)
    print(f"Found {unmatched.count()} unmatched records")
    
    # Get all leads
    all_leads = list(Lead.objects.filter(phone_number__isnull=False).exclude(phone_number=''))
    print(f"Found {len(all_leads)} leads")
    
    matched_count = 0
    
    for record in unmatched:
        call_phone = str(record.phone_number).strip()
        
        # Remove .0 suffix from Excel
        if call_phone.endswith('.0'):
            call_phone = call_phone[:-2]
        
        # Extract digits
        call_digits = ''.join(filter(str.isdigit, call_phone))
        
        if len(call_digits) < 10:
            continue
        
        # Try different lengths - Excel might have extra digits
        for length in [10, 11, 12, 13]:
            if len(call_digits) >= length:
                call_number = call_digits[-length:]
                
                # Find matching lead
                for lead in all_leads:
                    lead_digits = ''.join(filter(str.isdigit, str(lead.phone_number)))
                    
                    # Try matching different parts
                    if (len(lead_digits) >= 10 and len(call_number) >= 10 and 
                        lead_digits[-10:] == call_number[-10:]):
                        
                        record.matched_lead = lead
                        record.is_matched = True
                        record.save()
                        matched_count += 1
                        print(f"✅ MATCHED: {record.phone_number} → {lead.phone_number} ({lead.full_name})")
                        break
                
                if record.is_matched:
                    break
    
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
    fix_excel_matching()