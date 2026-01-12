#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from django.contrib.auth.models import User
from leads.models import TeamMember

def link_users_to_team_members():
    """Link existing Django users to TeamMember records"""
    
    # Get all users and team members
    users = User.objects.all()
    team_members = TeamMember.objects.all()
    
    linked_count = 0
    
    for user in users:
        # Try to find matching team member by username or email
        team_member = None
        
        # First try by username (which should be first name)
        try:
            team_member = TeamMember.objects.get(
                name__icontains=user.username,
                user__isnull=True
            )
        except (TeamMember.DoesNotExist, TeamMember.MultipleObjectsReturned):
            pass
        
        # If not found, try by email
        if not team_member and user.email:
            try:
                team_member = TeamMember.objects.get(
                    email=user.email,
                    user__isnull=True
                )
            except (TeamMember.DoesNotExist, TeamMember.MultipleObjectsReturned):
                pass
        
        # Link if found
        if team_member:
            team_member.user = user
            team_member.save()
            print(f"Linked {user.username} -> {team_member.name} ({team_member.role})")
            linked_count += 1
        else:
            print(f"No team member found for user: {user.username}")
    
    print(f"\nLinked {linked_count} users to team members")
    
    # Show unlinked team members
    unlinked = TeamMember.objects.filter(user__isnull=True)
    print(f"Unlinked team members: {unlinked.count()}")
    for tm in unlinked[:10]:  # Show first 10
        print(f"  - {tm.name} ({tm.role})")

if __name__ == "__main__":
    link_users_to_team_members()