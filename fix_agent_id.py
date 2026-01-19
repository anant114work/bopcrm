#!/usr/bin/env python3
"""
Fix Agent ID for Existing Campaign
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.bulk_call_models import BulkCallCampaign

def fix_agent_ids():
    """Fix agent IDs to use AU Reality agent"""
    print("FIXING AGENT IDS")
    print("=" * 30)
    
    # AU Reality agent ID
    correct_agent_id = "69294d3d2cc1373b1f3a3972"
    
    campaigns = BulkCallCampaign.objects.all()
    
    for campaign in campaigns:
        print(f"Campaign: {campaign.name}")
        print(f"  Current Agent ID: {campaign.agent_id}")
        
        if campaign.agent_id != correct_agent_id:
            campaign.agent_id = correct_agent_id
            campaign.save()
            print(f"  FIXED: Changed to {correct_agent_id}")
        else:
            print(f"  OK: Already using correct agent ID")

if __name__ == "__main__":
    fix_agent_ids()
    print("\nAGENT ID FIX COMPLETE!")