#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import TeamMember

def check_admin_users():
    """Check existing admin users and their credentials"""
    
    print("=== Current Team Members ===")
    all_members = TeamMember.objects.all()
    
    for member in all_members:
        print(f"ID: {member.id}")
        print(f"Name: {member.name}")
        print(f"Email: {member.email}")
        print(f"Phone: {member.phone}")
        print(f"Role: {member.role}")
        print(f"Active: {member.is_active}")
        print("-" * 40)
    
    print("\n=== Admin Users Only ===")
    admin_members = TeamMember.objects.filter(role='Admin')
    
    for admin in admin_members:
        username = admin.name.split()[0].lower()
        print(f"Username: {username}")
        print(f"Password: {admin.phone}")
        print(f"Full Name: {admin.name}")
        print(f"Active: {admin.is_active}")
        print("-" * 30)
    
    # Check specific user
    print("\n=== Checking admin1 user ===")
    admin1_users = TeamMember.objects.filter(name__icontains='admin1')
    if admin1_users:
        for user in admin1_users:
            print(f"Found: {user.name} - Phone: {user.phone} - Role: {user.role}")
    else:
        print("No user with 'admin1' in name found")
    
    # Check by phone number
    print("\n=== Checking phone 7290001154 ===")
    phone_users = TeamMember.objects.filter(phone='7290001154')
    if phone_users:
        for user in phone_users:
            print(f"Found: {user.name} - Phone: {user.phone} - Role: {user.role}")
    else:
        print("No user with phone 7290001154 found")

if __name__ == '__main__':
    check_admin_users()