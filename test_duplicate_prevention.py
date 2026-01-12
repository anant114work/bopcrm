#!/usr/bin/env python3
"""
Test Duplicate Call Prevention
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.bulk_call_models import BulkCallCampaign, BulkCallRecord

def test_duplicate_prevention():
    """Test that duplicate numbers are properly tracked"""
    print("TESTING DUPLICATE PREVENTION")
    print("=" * 40)
    
    # Get campaign
    campaign = BulkCallCampaign.objects.first()
    if not campaign:
        print("No campaigns found")
        return
    
    print(f"Campaign: {campaign.name}")
    
    # Check current status
    total_records = campaign.call_records.count()
    pending_records = campaign.call_records.filter(status='pending').count()
    called_records = campaign.call_records.exclude(status='pending').count()
    skipped_records = campaign.call_records.filter(status='skipped').count()
    
    print(f"Total records: {total_records}")
    print(f"Pending: {pending_records}")
    print(f"Already called: {called_records}")
    print(f"Skipped duplicates: {skipped_records}")
    
    # Show some called numbers
    called_numbers = list(campaign.call_records.exclude(status='pending').values_list('phone_number', flat=True)[:5])
    print(f"Sample called numbers: {called_numbers}")
    
    # Check if any pending numbers match called numbers
    all_called_numbers = set(BulkCallRecord.objects.exclude(status='pending').values_list('phone_number', flat=True))
    pending_numbers = set(campaign.call_records.filter(status='pending').values_list('phone_number', flat=True))
    
    duplicates = pending_numbers.intersection(all_called_numbers)
    print(f"Duplicates found in pending: {len(duplicates)}")
    
    if duplicates:
        print("WARNING: Found duplicate numbers that should be skipped!")
        print(f"Sample duplicates: {list(duplicates)[:3]}")
    else:
        print("SUCCESS: No duplicates found in pending calls")

if __name__ == "__main__":
    test_duplicate_prevention()
    print("\nTEST COMPLETE!")