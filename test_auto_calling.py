#!/usr/bin/env python3
"""
Test Auto Calling Functionality
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.auto_call_new_leads import auto_call_service

def test_auto_calling():
    """Test auto-calling functionality"""
    print("TESTING AUTO CALLING FUNCTIONALITY")
    print("=" * 50)
    
    # Check new leads in last 24 hours
    new_leads = auto_call_service.get_new_leads_for_calling(
        form_names=[
            'AU without OTP form 06/12/2025, 16:48',
            'AU Leisure Valley form 18/11/2025, 15:11'
        ],
        since_minutes=1440  # 24 hours
    )
    
    print(f"New AU leads in last 24 hours: {new_leads.count()}")
    
    if new_leads.count() > 0:
        print("\nRecent leads:")
        for lead in new_leads[:5]:
            print(f"  {lead.full_name} - {lead.phone_number} - {lead.form_name}")
            print(f"    Created: {lead.created_time}")
    
    # Test calling (dry run - just check the logic)
    print(f"\nTesting auto-call service...")
    print(f"Agent ID: {auto_call_service.agent_id}")
    
    # Don't actually call, just show what would happen
    if new_leads.count() > 0:
        print(f"Would call {new_leads.count()} leads with AU Reality Agent")
    else:
        print("No new leads to call")

if __name__ == "__main__":
    test_auto_calling()
    print("\nTEST COMPLETE!")