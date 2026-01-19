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

def test_round_robin():
    print("Testing round-robin assignment...")
    
    for i in range(5):
        lead = Lead.objects.create(
            lead_id=f'TEST_RR_{i+1}',
            created_time=timezone.now(),
            full_name=f'Test User {i+1}',
            email=f'test{i+1}@example.com',
            phone_number=f'987654321{i}',
            form_name='Test Form'
        )
        
        assignment = auto_assign_new_lead(lead)
        print(f'Lead {i+1} "{lead.full_name}" assigned to: {assignment.assigned_to.name if assignment else "No assignment"}')
    
    print("\nCurrent team members available for assignment:")
    available_members = TeamMember.objects.filter(
        is_active=True,
        role__in=['Sales Executive - T5', 'Sales Manager - T4', 'Team leader - t3']
    )
    
    for member in available_members:
        assigned_count = LeadAssignment.objects.filter(assigned_to=member).count()
        print(f"- {member.name} ({member.role}): {assigned_count} leads assigned")

if __name__ == "__main__":
    test_round_robin()