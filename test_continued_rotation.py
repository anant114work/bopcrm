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

def test_continued_rotation():
    print("Testing continued rotation with 5 more leads...")
    
    for i in range(5):
        lead = Lead.objects.create(
            lead_id=f'TEST_CONT_{i+1}',
            created_time=timezone.now(),
            full_name=f'Continue Test {i+1}',
            email=f'cont{i+1}@example.com',
            phone_number=f'666000{i}',
            form_name='Continuation Test'
        )
        
        assignment = auto_assign_new_lead(lead)
        print(f'Lead {i+1} assigned to: {assignment.assigned_to.name if assignment else "No assignment"}')
    
    print("\nFinal distribution after 15 total leads:")
    
    # Show members with assignments
    members_with_assignments = TeamMember.objects.filter(
        is_active=True,
        role__in=['Sales Executive - T5', 'Sales Manager - T4', 'Team leader - t3']
    ).order_by('name')
    
    for member in members_with_assignments:
        count = LeadAssignment.objects.filter(assigned_to=member).count()
        if count > 0:
            print(f"{member.name}: {count} leads")

if __name__ == "__main__":
    test_continued_rotation()