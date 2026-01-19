#!/usr/bin/env python3
"""
Test Campaign Fix
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.bulk_call_models import BulkCallCampaign
from leads.bulk_call_service import bulk_call_processor

def test_campaign_operations():
    """Test campaign start/stop operations"""
    print("TESTING CAMPAIGN OPERATIONS")
    print("=" * 40)
    
    # Get a campaign with pending calls
    campaign = BulkCallCampaign.objects.filter(status='paused').first()
    
    if not campaign:
        print("No paused campaigns found to test")
        return
    
    print(f"Testing with campaign: {campaign.name} (ID: {campaign.id})")
    print(f"Status: {campaign.status}")
    
    pending_calls = campaign.call_records.filter(status='pending').count()
    print(f"Pending calls: {pending_calls}")
    
    if pending_calls == 0:
        print("No pending calls - cannot test start operation")
        return
    
    # Test start campaign
    print("\nTesting START campaign...")
    success, message = bulk_call_processor.start_campaign(campaign.id)
    print(f"Result: {success} - {message}")
    
    if success:
        # Wait a moment then test stop
        import time
        time.sleep(2)
        
        print("\nTesting STOP campaign...")
        success, message = bulk_call_processor.stop_campaign(campaign.id)
        print(f"Result: {success} - {message}")
    
    # Test stop on non-running campaign (should not give "Campaign not running" error)
    print("\nTesting STOP on non-running campaign...")
    success, message = bulk_call_processor.stop_campaign(campaign.id)
    print(f"Result: {success} - {message}")

if __name__ == "__main__":
    test_campaign_operations()
    print("\nTEST COMPLETE!")