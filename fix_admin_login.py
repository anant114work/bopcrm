#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from django.contrib.auth.models import User

print("=== CURRENT ADMIN USERS ===")
admins = User.objects.filter(is_superuser=True)
for admin in admins:
    print(f"Username: {admin.username}, Email: {admin.email}")

print("\n=== DELETING OLD ADMIN USERS ===")
User.objects.filter(username__in=['admin', 'superadmin', 'manager']).delete()

print("=== CREATING NEW ADMIN USER ===")
# Create simple admin user
admin_user = User.objects.create_user(
    username='admin',
    email='admin@company.com',
    password='admin123'
)
admin_user.is_staff = True
admin_user.is_superuser = True
admin_user.save()

print("CREATED: admin / admin123")

# Test the login
from django.contrib.auth import authenticate
test_user = authenticate(username='admin', password='admin123')
if test_user:
    print("✓ LOGIN TEST PASSED")
else:
    print("✗ LOGIN TEST FAILED")

print("\nNow try: admin / admin123")