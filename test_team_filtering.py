#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from django.contrib.auth.models import User
from leads.models import TeamMember, Lead, LeadAssignment

def test_team_filtering():
    """Test team filtering for Ankush Kadyan"""
    
    # Find Ankush Kadyan's user
    try:
        ankush_user = User.objects.get(username='ankush1')
        print(f"Found user: {ankush_user.username}")
        
        if hasattr(ankush_user, 'team_member'):
            team_member = ankush_user.team_member
            print(f"Team member: {team_member.name} ({team_member.role})")
            
            # Get all team members under Ankush
            team_members = team_member.get_all_team_members()
            print(f"Team members under {team_member.name}: {len(team_members)}")
            for tm in team_members:
                print(f"  - {tm.name} ({tm.role})")
            
            # Get team member IDs
            team_member_ids = [tm.id for tm in team_members]
            print(f"Team member IDs: {team_member_ids}")
            
            # Test lead filtering
            all_leads = Lead.objects.all().count()
            team_leads = Lead.objects.filter(assignment__assigned_to__id__in=team_member_ids).count()
            
            print(f"Total leads in system: {all_leads}")
            print(f"Leads assigned to Ankush's team: {team_leads}")
            
            # Show some sample leads
            sample_leads = Lead.objects.filter(assignment__assigned_to__id__in=team_member_ids)[:5]
            print(f"Sample team leads:")
            for lead in sample_leads:
                assigned_to = lead.assignment.assigned_to if hasattr(lead, 'assignment') else 'Unassigned'
                print(f"  - {lead.full_name} -> {assigned_to}")
                
        else:
            print("User has no team_member relationship")
            
    except User.DoesNotExist:
        print("Ankush user not found")
    except Exception as e:
        print(f"Error: {e}")

def check_assignments():
    """Check lead assignments"""
    total_leads = Lead.objects.count()
    assigned_leads = LeadAssignment.objects.count()
    unassigned_leads = total_leads - assigned_leads
    
    print(f"\nLead Assignment Status:")
    print(f"Total leads: {total_leads}")
    print(f"Assigned leads: {assigned_leads}")
    print(f"Unassigned leads: {unassigned_leads}")
    
    # Show some assignments
    assignments = LeadAssignment.objects.select_related('lead', 'assigned_to')[:10]
    print(f"\nSample assignments:")
    for assignment in assignments:
        print(f"  - {assignment.lead.full_name} -> {assignment.assigned_to.name}")

if __name__ == "__main__":
    test_team_filtering()
    check_assignments()