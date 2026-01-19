#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import Lead, TeamMember, LeadAssignment
from leads.assignment import auto_assign_new_lead
from django.utils import timezone

def test_proper_round_robin():
    print("Testing PROPER round-robin assignment...")
    
    # Clear existing test assignments
    LeadAssignment.objects.filter(lead__lead_id__startswith='TEST_').delete()
    Lead.objects.filter(lead_id__startswith='TEST_').delete()
    
    print("Creating 10 test leads to see proper distribution...")
    
    for i in range(10):
        lead = Lead.objects.create(
            lead_id=f'TEST_PROPER_{i+1}',
            created_time=timezone.now(),
            full_name=f'Proper Test User {i+1}',
            email=f'proper_test{i+1}@example.com',
            phone_number=f'555000{i:04d}',
            form_name='Round Robin Test Form'
        )
        
        assignment = auto_assign_new_lead(lead)
        print(f'Lead {i+1:2d} "{lead.full_name}" assigned to: {assignment.assigned_to.name if assignment else "No assignment"}')
    
    print("\n" + "="*60)
    print("ASSIGNMENT DISTRIBUTION SUMMARY:")
    print("="*60)
    
    # Get all available members and their assignment counts
    available_members = TeamMember.objects.filter(
        is_active=True,
        role__in=['Sales Executive - T5', 'Sales Manager - T4', 'Team leader - t3']
    ).order_by('name')
    
    total_assignments = 0
    for member in available_members:
        assigned_count = LeadAssignment.objects.filter(assigned_to=member).count()
        if assigned_count > 0:
            print(f"{member.name:25} ({member.role:20}): {assigned_count:2d} leads")
            total_assignments += assigned_count
    
    print("-" * 60)
    print(f"{'TOTAL ASSIGNMENTS':25} {'':<20}: {total_assignments:2d} leads")
    print(f"{'AVAILABLE MEMBERS':25} {'':<20}: {available_members.count():2d} members")
    
    if available_members.count() > 0:
        avg_per_member = total_assignments / available_members.count()
        print(f"{'AVERAGE PER MEMBER':25} {'':<20}: {avg_per_member:.1f} leads")

if __name__ == "__main__":
    test_proper_round_robin()