#!/usr/bin/env python3
"""
Test Starting Campaign with Duplicate Prevention
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.bulk_call_service import bulk_call_processor

def test_start_with_duplicates():
    """Test starting campaign with duplicate prevention"""
    print("TESTING CAMPAIGN START WITH DUPLICATE PREVENTION")
    print("=" * 60)
    
    # Try to start campaign 2 (which has already called some numbers)
    campaign_id = 2
    
    print(f"Starting campaign {campaign_id}...")
    success, message = bulk_call_processor.start_campaign(campaign_id)
    
    print(f"Result: {success}")
    print(f"Message: {message}")
    
    if success:
        print("\nStopping campaign to prevent actual calls...")
        success2, message2 = bulk_call_processor.stop_campaign(campaign_id)
        print(f"Stop result: {success2} - {message2}")

if __name__ == "__main__":
    test_start_with_duplicates()
    print("\nTEST COMPLETE!")