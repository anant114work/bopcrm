#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from leads.models import TeamMember
from leads.project_views import project_leads
from leads.project_models import Project

def test_session_filtering():
    """Test session-based filtering"""
    
    # Create a mock request with session
    factory = RequestFactory()
    request = factory.get('/test/')
    
    # Add session middleware
    middleware = SessionMiddleware(lambda x: None)
    middleware.process_request(request)
    request.session.save()
    
    # Set up Ankush's session
    ankush_team_member = TeamMember.objects.get(name='Ankush Kadyan')
    request.session['is_team_member'] = True
    request.session['team_member_id'] = ankush_team_member.id
    request.session['team_member_name'] = ankush_team_member.name
    request.session['team_member_role'] = ankush_team_member.role
    
    print(f"Testing session auth for: {ankush_team_member.name}")
    print(f"Session team_member_id: {request.session.get('team_member_id')}")
    print(f"Session is_team_member: {request.session.get('is_team_member')}")
    
    # Test project filtering
    try:
        bgc_project = Project.objects.get(name__icontains='Bhutani Grand Central')
        print(f"\\nTesting project: {bgc_project.name}")
        
        # Get all project leads
        all_leads = bgc_project.get_leads()
        print(f"Total project leads: {all_leads.count()}")
        
        # Apply session-based filtering manually
        team_members = ankush_team_member.get_all_team_members()
        team_member_ids = [tm.id for tm in team_members]
        filtered_leads = all_leads.filter(assignment__assigned_to__id__in=team_member_ids)
        print(f"Filtered leads for Ankush's team: {filtered_leads.count()}")
        
        print(f"\\nAnkush should see {filtered_leads.count()} leads, not {all_leads.count()}")
        
    except Project.DoesNotExist:
        print("Project not found")

if __name__ == "__main__":
    test_session_filtering()