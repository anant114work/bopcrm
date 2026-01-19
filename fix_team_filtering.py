#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from django.contrib.auth.models import User
from leads.models import TeamMember, Lead, LeadAssignment
from leads.project_models import Project

def test_project_filtering():
    """Test project lead filtering for Ankush"""
    
    # Find Ankush Kadyan's user
    ankush_user = User.objects.get(username='ankush1')
    team_member = ankush_user.team_member
    
    # Get all team members under Ankush
    team_members = team_member.get_all_team_members()
    team_member_ids = [tm.id for tm in team_members]
    
    # Test Bhutani Grand Central project
    try:
        bgc_project = Project.objects.get(name__icontains='Bhutani Grand Central')
        print(f"Project: {bgc_project.name}")
        
        # Get all leads for this project (current behavior)
        all_project_leads = bgc_project.get_leads()
        print(f"Total project leads: {all_project_leads.count()}")
        
        # Apply team filtering
        team_project_leads = all_project_leads.filter(assignment__assigned_to__id__in=team_member_ids)
        print(f"Team project leads: {team_project_leads.count()}")
        
        # Show the difference
        print(f"Ankush should see {team_project_leads.count()} leads, not {all_project_leads.count()}")
        
    except Project.DoesNotExist:
        print("Bhutani Grand Central project not found")
        
    # List all projects
    print(f"\nAll projects:")
    for project in Project.objects.all():
        all_leads = project.get_leads().count()
        team_leads = project.get_leads().filter(assignment__assigned_to__id__in=team_member_ids).count()
        print(f"  - {project.name}: {all_leads} total, {team_leads} for Ankush's team")

if __name__ == "__main__":
    test_project_filtering()