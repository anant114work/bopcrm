#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import TeamMember

print("=== TEAM MEMBER LOGIN CREDENTIALS ===")
print("Format: First Name / Phone Number")
print("-" * 40)

team_members = TeamMember.objects.all()[:20]  # Get first 20 members
for member in team_members:
    print(f"Username: {member.first_name}")
    print(f"Password: {member.phone}")
    print(f"Full Name: {member.first_name} {member.last_name}")
    print(f"Email: {member.email}")
    print("-" * 30)

if not team_members:
    print("No team members found in database")
    
print(f"\nTotal team members: {TeamMember.objects.count()}")