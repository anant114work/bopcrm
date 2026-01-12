#!/usr/bin/env python3
"""
Fix Campaign Status Issues
This script helps diagnose and fix "Campaign not running" errors
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.bulk_call_models import BulkCallCampaign, BulkCallRecord
from leads.bulk_call_service import bulk_call_processor

def diagnose_campaigns():
    """Diagnose all campaign issues"""
    print("DIAGNOSING BULK CALL CAMPAIGNS")
    print("=" * 50)
    
    campaigns = BulkCallCampaign.objects.all().order_by('-created_at')
    
    if not campaigns:
        print("No campaigns found")
        return
    
    for campaign in campaigns:
        print(f"\nCampaign: {campaign.name}")
        print(f"   ID: {campaign.id}")
        print(f"   Status: {campaign.status}")
        print(f"   Total Numbers: {campaign.total_numbers}")
        print(f"   Completed: {campaign.completed_calls}")
        print(f"   Successful: {campaign.successful_calls}")
        print(f"   Failed: {campaign.failed_calls}")
        
        # Check pending calls
        pending_calls = campaign.call_records.filter(status='pending').count()
        print(f"   Pending Calls: {pending_calls}")
        
        # Check if running in memory
        try:
            is_running_in_memory = campaign.id in bulk_call_processor.running_campaigns
        except AttributeError:
            is_running_in_memory = False
        print(f"   Running in Memory: {is_running_in_memory}")
        
        # Check for inconsistencies
        if campaign.status == 'running' and not is_running_in_memory:
            print("   WARNING: Marked as running but not in memory")
        
        if pending_calls == 0 and campaign.status in ['pending', 'running']:
            print("   WARNING: No pending calls but status is pending/running")

def fix_campaigns():
    """Fix campaign status issues"""
    print("\nFIXING CAMPAIGN ISSUES")
    print("=" * 50)
    
    try:
        result = bulk_call_processor.cleanup_campaigns()
        
        if result['success']:
            print(f"SUCCESS: Cleaned up {result['cleaned']} campaigns")
        else:
            print(f"ERROR: {result['error']}")
    except Exception as e:
        print(f"ERROR: Could not run cleanup - {str(e)}")
        
        # Manual cleanup
        print("\nRunning manual cleanup...")
        campaigns = BulkCallCampaign.objects.filter(status='running')
        fixed = 0
        
        for campaign in campaigns:
            pending_calls = campaign.call_records.filter(status='pending').count()
            if pending_calls == 0:
                campaign.status = 'completed'
                campaign.save()
                print(f"   Fixed: {campaign.name} -> completed")
                fixed += 1
            else:
                campaign.status = 'paused'
                campaign.save()
                print(f"   Fixed: {campaign.name} -> paused")
                fixed += 1
        
        print(f"SUCCESS: Manually fixed {fixed} campaigns")

def show_recent_calls():
    """Show recent call activity"""
    print("\nRECENT CALL ACTIVITY")
    print("=" * 50)
    
    recent_calls = BulkCallRecord.objects.exclude(status='pending').order_by('-initiated_at')[:10]
    
    if not recent_calls:
        print("No recent calls found")
        return
    
    for call in recent_calls:
        print(f"{call.name} - {call.phone_number} ({call.status})")
        if call.initiated_at:
            print(f"   Time: {call.initiated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        if call.error_message:
            print(f"   Error: {call.error_message}")

def test_callkaro_connection():
    """Test CallKaro API connection"""
    print("\nTESTING CALLKARO CONNECTION")
    print("=" * 50)
    
    try:
        from leads.bulk_call_service import initiate_callkaro_call
        
        # Test with a dummy number (won't actually call)
        result = initiate_callkaro_call("+919999999999", None, "692d5b6ad10e948b7bbfc2db")
        
        if result['success']:
            print("SUCCESS: CallKaro API connection successful")
            print(f"   Response: {result.get('response', {})}")
        else:
            print("ERROR: CallKaro API connection failed")
            print(f"   Error: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"ERROR: Could not test connection - {str(e)}")

if __name__ == "__main__":
    print("BULK CALL CAMPAIGN DIAGNOSTICS")
    print("=" * 60)
    
    try:
        # Run diagnostics
        diagnose_campaigns()
        
        # Fix issues
        fix_campaigns()
        
        # Show recent activity
        show_recent_calls()
        
        # Test API connection
        test_callkaro_connection()
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")
    
    print("\nDIAGNOSTICS COMPLETE")
    print("=" * 60)