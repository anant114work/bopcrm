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

def create_admin_users():
    """Create admin users with proper credentials"""
    
    admin_users = [
        {
            'name': 'admin1',
            'email': 'admin1@company.com',
            'phone': '7290001154',
            'role': 'Admin'
        },
        {
            'name': 'Gaurav Mavi',
            'email': 'gaurav@company.com', 
            'phone': '9910266552',
            'role': 'Admin'
        },
        {
            'name': 'Atul Verma',
            'email': 'atul@company.com',
            'phone': '9999929832', 
            'role': 'Admin'
        }
    ]
    
    for admin_data in admin_users:
        # Check if user already exists
        existing = TeamMember.objects.filter(
            phone=admin_data['phone']
        ).first()
        
        if existing:
            print(f"Admin {admin_data['name']} already exists")
            # Update role to Admin if needed
            if existing.role != 'Admin':
                existing.role = 'Admin'
                existing.save()
                print(f"Updated {existing.name} role to Admin")
        else:
            admin = TeamMember.objects.create(**admin_data)
            print(f"Created admin user: {admin.name}")
    
    print("\nAdmin users created/updated successfully!")
    print("Login credentials:")
    for admin_data in admin_users:
        username = admin_data['name'].split()[0].lower()
        print(f"Username: {username}, Password: {admin_data['phone']}")

if __name__ == '__main__':
    create_admin_users()