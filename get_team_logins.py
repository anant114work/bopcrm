#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import TeamMember

print("=== TEAM MEMBER LOGIN CREDENTIALS ===")
print("Username: First Name | Password: Phone Number")
print("-" * 50)

team_members = TeamMember.objects.all()[:15]  # Get first 15 members
for member in team_members:
    first_name = member.name.split()[0] if member.name else "Unknown"
    print(f"Username: {first_name}")
    print(f"Password: {member.phone}")
    print(f"Full Name: {member.name}")
    print(f"Email: {member.email}")
    print("-" * 30)

print(f"\nTotal available: {TeamMember.objects.count()} team members")