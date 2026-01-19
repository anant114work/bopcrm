#!/usr/bin/env python
import os
import sys
import django

sys.path.append('d:\\AI-proto\\CRM\\drip')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from django.contrib.auth.models import User

print("=== USER STATUS CHECK ===")

# Check all users
users = User.objects.all()
print(f"Total users: {users.count()}")

for user in users:
    print(f"\nUser: {user.username}")
    print(f"  Email: {user.email}")
    print(f"  Is Staff: {user.is_staff}")
    print(f"  Is Superuser: {user.is_superuser}")
    print(f"  Is Active: {user.is_active}")

# Make sure admin user has staff privileges
admin_user, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@crm.com',
        'is_staff': True,
        'is_superuser': True,
        'is_active': True
    }
)

if not admin_user.is_staff:
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.save()
    print(f"\nUpdated {admin_user.username} to have staff privileges")

print(f"\n=== INTEGRATION ACCESS ===")
print(f"Admin user '{admin_user.username}' can access integrations: {admin_user.is_staff}")
print("Login with username: admin")
print("If you don't know the password, reset it in Django admin")