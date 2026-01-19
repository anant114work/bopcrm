#!/usr/bin/env python3
"""
Quick Fix for Campaign Status Issues
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.bulk_call_models import BulkCallCampaign, BulkCallRecord

def fix_campaign_status():
    """Fix campaign status issues manually"""
    print("FIXING CAMPAIGN STATUS ISSUES")
    print("=" * 40)
    
    # Get all campaigns
    campaigns = BulkCallCampaign.objects.all()
    
    for campaign in campaigns:
        print(f"\nCampaign: {campaign.name} (ID: {campaign.id})")
        print(f"Current Status: {campaign.status}")
        
        # Count pending calls
        pending_calls = campaign.call_records.filter(status='pending').count()
        print(f"Pending Calls: {pending_calls}")
        
        # Fix status based on pending calls
        if pending_calls == 0:
            if campaign.status in ['pending', 'running']:
                campaign.status = 'completed'
                campaign.save()
                print(f"FIXED: Changed status to 'completed'")
        else:
            if campaign.status == 'running':
                campaign.status = 'paused'
                campaign.save()
                print(f"FIXED: Changed status to 'paused' (was running but not in memory)")
        
        print(f"New Status: {campaign.status}")

def check_agent_config():
    """Check CallKaro agent configuration"""
    print("\nCHECKING AGENT CONFIGURATION")
    print("=" * 40)
    
    try:
        from leads.callkaro_models import CallKaroAgent
        agents = CallKaroAgent.objects.filter(is_active=True)
        
        print(f"Found {agents.count()} active agents:")
        for agent in agents:
            print(f"  - {agent.name}: {agent.agent_id}")
            
        if agents.count() == 0:
            print("WARNING: No active CallKaro agents found!")
            print("This might be causing the 'Error getting agent!' issue")
            
    except Exception as e:
        print(f"ERROR: Could not check agents - {str(e)}")

if __name__ == "__main__":
    fix_campaign_status()
    check_agent_config()
    print("\nFIX COMPLETE!")