#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from django.contrib.auth.models import User

print("=== EXISTING TEAM USERS (Sample) ===")
users = User.objects.filter(is_superuser=False)[:10]
for user in users:
    print(f"Username: {user.username}")
    print(f"Email: {user.email}")
    print("Password: [ENCRYPTED - Cannot retrieve]")
    print("-" * 30)

print("\n=== ADMIN USERS ===")
admin_users = User.objects.filter(is_superuser=True)
for user in admin_users:
    print(f"Username: {user.username}")
    print(f"Email: {user.email}")
    print("Password: [Check auth/quick_login.md]")
    print("-" * 30)