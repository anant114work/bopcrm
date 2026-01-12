#!/usr/bin/env python
"""
Simple script to fix call report matching by matching phone numbers aggressively
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

def fix_all_matching():
    """Fix all unmatched call records with aggressive matching"""
    print("🔍 Finding unmatched call records...")
    
    unmatched = CallReportRecord.objects.filter(is_matched=False)
    print(f"📊 Found {unmatched.count()} unmatched records")
    
    matched_count = 0
    
    for record in unmatched:
        phone = str(record.phone_number).strip()
        if not phone or phone == 'nan':
            continue
        
        # Extract only digits
        digits = ''.join(filter(str.isdigit, phone))
        
        if len(digits) >= 10:
            last_10 = digits[-10:]
            
            # Find any lead with these 10 digits
            lead = Lead.objects.filter(
                phone_number__iregex=f'.*{last_10}.*'
            ).first()
            
            if lead:
                record.matched_lead = lead
                record.is_matched = True
                record.save()
                matched_count += 1
                print(f"✅ {phone} → {lead.phone_number} ({lead.full_name})")
    
    print(f"\n🎉 Matched {matched_count} records!")
    
    # Show final stats
    total = CallReportRecord.objects.count()
    matched = CallReportRecord.objects.filter(is_matched=True).count()
    rate = (matched / total * 100) if total > 0 else 0
    
    print(f"📈 Final Stats:")
    print(f"   Total: {total}")
    print(f"   Matched: {matched}")
    print(f"   Rate: {rate:.1f}%")

if __name__ == "__main__":
    fix_all_matching()