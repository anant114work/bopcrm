#!/usr/bin/env python
"""
Simple fix for phone matching
"""

import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.call_report_models import CallReportRecord
from leads.models import Lead

# Create a lookup dict of all leads by their core phone number
print("Building lead lookup...")
lead_lookup = {}
for lead in Lead.objects.filter(phone_number__isnull=False).exclude(phone_number=''):
    digits = ''.join(filter(str.isdigit, str(lead.phone_number)))
    if len(digits) >= 10:
        # Store by last 10 digits
        key = digits[-10:]
        lead_lookup[key] = lead

print(f"Built lookup for {len(lead_lookup)} leads")

# Fix all unmatched records
unmatched = CallReportRecord.objects.filter(is_matched=False)
print(f"Processing {unmatched.count()} unmatched records...")

matched_count = 0

for record in unmatched:
    phone_str = str(record.phone_number).replace('.0', '')
    digits = ''.join(filter(str.isdigit, phone_str))
    
    if len(digits) >= 10:
        # Try matching with different digit combinations
        for i in range(len(digits) - 9):
            test_digits = digits[i:i+10]
            if test_digits in lead_lookup:
                lead = lead_lookup[test_digits]
                record.matched_lead = lead
                record.is_matched = True
                record.save()
                matched_count += 1
                print(f"✅ {record.phone_number} → {lead.phone_number} ({lead.full_name})")
                break

print(f"\n🎉 Matched {matched_count} records!")

# Show final stats
total = CallReportRecord.objects.count()
matched = CallReportRecord.objects.filter(is_matched=True).count()
print(f"Final: {matched}/{total} matched ({matched/total*100:.1f}%)")