#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from django.contrib.auth.models import User
from leads.models import TeamMember

def test_user_relationships():
    """Test user-team member relationships"""
    
    print("Testing user-team member relationships:")
    print("=" * 50)
    
    # Check Ankush specifically
    try:
        ankush_user = User.objects.get(username='ankush1')
        print(f"User: {ankush_user.username}")
        print(f"Has team_member attribute: {hasattr(ankush_user, 'team_member')}")
        
        if hasattr(ankush_user, 'team_member'):
            team_member = ankush_user.team_member
            print(f"Team member: {team_member.name} ({team_member.role})")
        else:
            print("No team_member relationship found")
            
            # Check if there's a team member with matching email
            try:
                team_member = TeamMember.objects.get(email=ankush_user.email)
                print(f"Found team member by email: {team_member.name}")
                print(f"Team member user field: {team_member.user}")
            except TeamMember.DoesNotExist:
                print("No team member found by email either")
                
    except User.DoesNotExist:
        print("Ankush user not found")
    
    print("\n" + "=" * 50)
    
    # Check all users with team_member relationships
    users_with_teams = User.objects.filter(team_member__isnull=False)
    print(f"Users with team_member relationships: {users_with_teams.count()}")
    
    for user in users_with_teams[:10]:
        print(f"  - {user.username} -> {user.team_member.name}")
    
    # Check team members without users
    team_members_without_users = TeamMember.objects.filter(user__isnull=True)
    print(f"\nTeam members without user relationships: {team_members_without_users.count()}")
    
    for tm in team_members_without_users[:10]:
        print(f"  - {tm.name} ({tm.email})")

if __name__ == "__main__":
    test_user_relationships()