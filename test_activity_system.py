#!/usr/bin/env python
"""
Test script for the Lead Activity & Reassignment Log System
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import Lead, TeamMember, LeadAssignment, LeadReassignmentLog, LeadViewActivity
from django.utils import timezone

def test_activity_system():
    print("Testing Lead Activity & Reassignment Log System")
    print("=" * 50)
    
    # Get some test data
    leads = list(Lead.objects.all()[:3])
    team_members = list(TeamMember.objects.filter(is_active=True)[:3])
    
    if not leads or not team_members:
        print("No test data available. Please ensure you have leads and team members.")
        return
    
    print(f"Found {len(leads)} leads and {len(team_members)} team members")
    
    # Test 1: Create a lead assignment
    print("\n1. Testing Lead Assignment...")
    lead = leads[0]
    team_member1 = team_members[0]
    team_member2 = team_members[-1] if len(team_members) > 1 else team_members[0]
    
    assignment, created = LeadAssignment.objects.get_or_create(
        lead=lead,
        defaults={'assigned_to': team_member1}
    )
    
    if created:
        print(f"Created assignment: {lead.full_name} -> {team_member1.name}")
    else:
        print(f"Assignment already exists: {lead.full_name} -> {assignment.assigned_to.name}")
    
    # Test 2: Create a reassignment (this should trigger the signal)
    print("\n2. Testing Lead Reassignment...")
    if team_member1 != team_member2:
        # Store reassignment info for signal
        assignment._reassigned_by = team_member1
        assignment._reassignment_reason = "Testing reassignment system"
        assignment.assigned_to = team_member2
        assignment.save()
        
        # Check if reassignment log was created
        reassignment_logs = LeadReassignmentLog.objects.filter(lead=lead)
        if reassignment_logs.exists():
            log = reassignment_logs.first()
            print(f"Reassignment logged: {log.previous_assignee.name} -> {log.new_assignee.name}")
            print(f"   Reason: {log.reason}")
        else:
            print("Reassignment log not created")
    
    # Test 3: Create a view activity log
    print("\n3. Testing View Activity Logging...")
    view_activity = LeadViewActivity.objects.create(
        lead=lead,
        viewed_by=team_member1,
        ip_address='127.0.0.1'
    )
    print(f"View activity logged: {lead.full_name} viewed by {team_member1.name}")
    
    # Test 4: Check hierarchy permissions
    print("\n4. Testing Hierarchy Permissions...")
    from leads.activity_views import get_accessible_leads, can_view_lead_activity, can_reassign_lead
    
    for member in team_members:
        accessible_count = get_accessible_leads(member).count()
        can_view = can_view_lead_activity(member, lead)
        can_reassign = can_reassign_lead(member, lead)
        
        print(f"   {member.name} ({member.role}):")
        print(f"     - Can access {accessible_count} leads")
        print(f"     - Can view activity: {can_view}")
        print(f"     - Can reassign: {can_reassign}")
    
    # Test 5: Display summary
    print("\nSystem Summary:")
    print(f"   - Total reassignment logs: {LeadReassignmentLog.objects.count()}")
    print(f"   - Total view activities: {LeadViewActivity.objects.count()}")
    print(f"   - Total lead assignments: {LeadAssignment.objects.count()}")
    
    print("\nActivity system test completed successfully!")
    print("\nYou can now:")
    print("   1. Visit /activity-dashboard/ to see the activity dashboard")
    print("   2. Visit any lead detail page to see activity tracking")
    print("   3. Use the reassign functionality in lead details")

if __name__ == "__main__":
    test_activity_system()