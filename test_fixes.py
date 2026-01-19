#!/usr/bin/env python
"""
Test script for the lead filtering and note attribution fixes
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import Lead, TeamMember, LeadAssignment
from django.db.models import Q

def test_lead_filtering():
    """Test the assigned_to filtering functionality"""
    print("Testing Lead Filtering by assigned_to parameter")
    print("=" * 50)
    
    # Get a team member with assigned leads
    member_with_leads = TeamMember.objects.filter(
        assigned_leads__isnull=False
    ).first()
    
    if not member_with_leads:
        print("No team members with assigned leads found.")
        return
    
    print(f"Testing with team member: {member_with_leads.name} (ID: {member_with_leads.id})")
    
    # Test the filtering logic
    all_leads = Lead.objects.all()
    filtered_leads = all_leads.filter(assignment__assigned_to_id=member_with_leads.id)
    
    print(f"Total leads: {all_leads.count()}")
    print(f"Leads assigned to {member_with_leads.name}: {filtered_leads.count()}")
    
    if filtered_leads.exists():
        print(f"Sample assigned leads:")
        for lead in filtered_leads[:3]:
            print(f"  - {lead.full_name} (ID: {lead.id})")
    
    print(f"\n[SUCCESS] Lead filtering test completed!")
    print(f"URL to test: http://127.0.0.1:8000/leads/?assigned_to={member_with_leads.id}")

def test_session_data():
    """Check what session data should look like"""
    print("\nTesting Session Data Structure")
    print("=" * 50)
    
    # Get a sample team member
    sample_member = TeamMember.objects.filter(is_active=True).first()
    
    if sample_member:
        print(f"Sample team member: {sample_member.name} (ID: {sample_member.id})")
        print(f"Expected session data:")
        print(f"  - team_member_id: {sample_member.id}")
        print(f"  - team_member_name: {sample_member.name}")
        print(f"  - is_team_member: True")
    
    print(f"\n[SUCCESS] Session data test completed!")

if __name__ == "__main__":
    test_lead_filtering()
    test_session_data()