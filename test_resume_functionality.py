#!/usr/bin/env python3
"""
Test Resume Functionality
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.bulk_call_models import BulkCallCampaign
from leads.bulk_call_upload_views import resume_bulk_calling
from django.http import HttpRequest
import json

def test_resume():
    """Test resume functionality"""
    print("TESTING RESUME FUNCTIONALITY")
    print("=" * 40)
    
    # Get campaign
    campaign = BulkCallCampaign.objects.first()
    if not campaign:
        print("No campaigns found")
        return
    
    print(f"Campaign: {campaign.name}")
    
    # Check current status
    total = campaign.call_records.count()
    pending = campaign.call_records.filter(status='pending').count()
    called = campaign.call_records.exclude(status='pending').count()
    
    print(f"Total records: {total}")
    print(f"Already called: {called}")
    print(f"Pending: {pending}")
    
    if pending == 0:
        print("No pending calls to test resume")
        return
    
    # Create mock request
    request = HttpRequest()
    request.method = 'POST'
    
    print(f"\nTesting resume for campaign {campaign.id}...")
    
    # Test resume (this will just check the logic, not actually make calls)
    try:
        from leads.bulk_call_service import bulk_call_processor
        
        # Check if we can start (this will mark duplicates as skipped)
        success, message = bulk_call_processor.start_campaign(campaign.id)
        
        print(f"Resume test result: {success}")
        print(f"Message: {message}")
        
        if success:
            # Stop immediately to prevent actual calls
            success2, message2 = bulk_call_processor.stop_campaign(campaign.id)
            print(f"Stop result: {success2} - {message2}")
            
            # Check how many were marked as skipped
            skipped = campaign.call_records.filter(status='skipped').count()
            print(f"Numbers marked as skipped: {skipped}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_resume()
    print("\nTEST COMPLETE!")