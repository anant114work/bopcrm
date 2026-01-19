#!/usr/bin/env python
"""
Script to fix call report matching by improving phone number normalization
"""

import os
import sys
import django
from django.db import transaction

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.call_report_models import CallReportRecord
from leads.models import Lead

def normalize_phone(phone):
    """Normalize phone number to all possible variants"""
    if not phone or phone == 'nan':
        return []
    
    # Clean phone number
    phone_clean = str(phone).replace('+91', '').replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '').strip()
    
    if len(phone_clean) >= 10:
        # Extract last 10 digits
        last_10 = phone_clean[-10:]
        
        # Create all possible variants
        variants = [
            phone_clean,  # Original cleaned
            last_10,      # Last 10 digits
            f"+91{last_10}",  # +91 prefix
            f"91{last_10}",   # 91 prefix
        ]
        
        # Remove duplicates and empty strings
        return list(set([v for v in variants if v]))
    
    return [phone_clean] if phone_clean else []

def fix_unmatched_records():
    """Re-process unmatched call report records"""
    print("🔍 Finding unmatched call report records...")
    
    unmatched_records = CallReportRecord.objects.filter(is_matched=False)
    print(f"📊 Found {unmatched_records.count()} unmatched records")
    
    if unmatched_records.count() == 0:
        print("✅ All records are already matched!")
        return
    
    matched_count = 0
    
    with transaction.atomic():
        for record in unmatched_records:
            phone_variants = normalize_phone(record.phone_number)
            
            if not phone_variants:
                continue
            
            # Try to find matching lead
            matched_lead = None
            
            for phone_variant in phone_variants:
                # Try exact match first
                lead = Lead.objects.filter(phone_number=phone_variant).first()
                if lead:
                    matched_lead = lead
                    break
                
                # Try partial match (last 10 digits)
                if len(phone_variant) >= 10:
                    last_10 = phone_variant[-10:]
                    lead = Lead.objects.filter(phone_number__endswith=last_10).first()
                    if lead:
                        matched_lead = lead
                        break
            
            if matched_lead:
                record.matched_lead = matched_lead
                record.is_matched = True
                record.save()
                matched_count += 1
                print(f"✅ Matched {record.phone_number} → {matched_lead.full_name} ({matched_lead.phone_number})")
    
    print(f"\n🎉 Successfully matched {matched_count} additional records!")
    
    # Show updated statistics
    total_records = CallReportRecord.objects.count()
    matched_records = CallReportRecord.objects.filter(is_matched=True).count()
    match_rate = (matched_records / total_records * 100) if total_records > 0 else 0
    
    print(f"📈 Updated Statistics:")
    print(f"   Total Records: {total_records}")
    print(f"   Matched Records: {matched_records}")
    print(f"   Match Rate: {match_rate:.1f}%")

def show_sample_phone_formats():
    """Show sample phone number formats from both sources"""
    print("📱 Sample phone number formats:")
    
    print("\n🔍 Call Report Records:")
    sample_records = CallReportRecord.objects.all()[:10]
    for record in sample_records:
        variants = normalize_phone(record.phone_number)
        print(f"   Original: {record.phone_number} → Variants: {variants}")
    
    print("\n🔍 Lead Records:")
    sample_leads = Lead.objects.filter(phone_number__isnull=False)[:10]
    for lead in sample_leads:
        print(f"   Lead: {lead.phone_number} ({lead.full_name})")

if __name__ == "__main__":
    print("=" * 60)
    print("📞 Call Report Matching Fix Tool")
    print("=" * 60)
    
    choice = input("\nChoose option:\n1. Show phone number formats\n2. Fix unmatched records\n3. Both\n\nEnter choice (1, 2, or 3): ")
    
    if choice in ["1", "3"]:
        show_sample_phone_formats()
    
    if choice in ["2", "3"]:
        fix_unmatched_records()
    
    print("\n" + "=" * 60)