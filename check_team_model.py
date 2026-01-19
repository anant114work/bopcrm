#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import TeamMember

print("=== TEAM MEMBER MODEL FIELDS ===")
member = TeamMember.objects.first()
if member:
    print("Available fields:")
    for field in member._meta.fields:
        print(f"- {field.name}")
    
    print("\nSample team member data:")
    print(f"ID: {member.id}")
    print(f"Name: {member.name}")
    print(f"Phone: {member.phone}")
    print(f"Email: {member.email}")
else:
    print("No team members found")

print(f"\nTotal team members: {TeamMember.objects.count()}")