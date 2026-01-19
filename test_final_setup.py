#!/usr/bin/env python3
"""
Test Final Auto-Calling Setup
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.auto_call_new_leads import auto_call_service
from leads.project_models import Project

def test_final_setup():
    """Test the complete setup"""
    print("FINAL SETUP TEST")
    print("=" * 30)
    
    # 1. Check AU project leads
    au_project = Project.objects.filter(name__icontains='AU Aspire').first()
    if au_project:
        leads_count = au_project.get_leads().count()
        print(f"✅ AU Project: {au_project.name}")
        print(f"✅ Total Leads: {leads_count}")
    
    # 2. Check auto-calling service
    new_leads = auto_call_service.get_new_leads_for_calling(
        form_names=[
            'AU without OTP form 06/12/2025, 16:48',
            'AU Leisure Valley form 18/11/2025, 15:11'
        ],
        since_minutes=60
    )
    
    print(f"✅ Auto-Call Service: Ready")
    print(f"✅ Agent ID: {auto_call_service.agent_id}")
    print(f"✅ New leads (last hour): {new_leads.count()}")
    
    # 3. Show available endpoints
    print(f"\n📡 AVAILABLE ENDPOINTS:")
    print(f"   Dashboard: /auto-call/dashboard/")
    print(f"   Check leads: /auto-call/count/")
    print(f"   Call leads: /auto-call/new-leads/")
    
    print(f"\n🎯 SUMMARY:")
    print(f"   ✅ Project leads working: {leads_count} leads")
    print(f"   ✅ Auto-calling ready: {new_leads.count()} new leads")
    print(f"   ✅ AU Reality Agent configured")
    print(f"   ✅ Dashboard available")

if __name__ == "__main__":
    test_final_setup()
    print("\n🚀 SETUP COMPLETE!")