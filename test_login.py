#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from django.contrib.auth import authenticate
from django.contrib.auth.models import User

print("=== TESTING LOGIN CREDENTIALS ===")

# Test each admin user
credentials = [
    ('admin', 'admin123'),
    ('superadmin', 'super123'),
    ('manager', 'manager123')
]

for username, password in credentials:
    print(f"\nTesting: {username} / {password}")
    
    # Check if user exists
    try:
        user = User.objects.get(username=username)
        print(f"[OK] User exists: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Is Active: {user.is_active}")
        print(f"   Is Staff: {user.is_staff}")
        print(f"   Is Superuser: {user.is_superuser}")
        
        # Test authentication
        auth_user = authenticate(username=username, password=password)
        if auth_user:
            print(f"[OK] Authentication SUCCESS")
        else:
            print(f"[FAIL] Authentication FAILED")
            
    except User.DoesNotExist:
        print(f"[FAIL] User does not exist")

print("\n=== DJANGO SERVER STATUS ===")
print("Make sure Django server is running:")
print("python manage.py runserver")
print("Then go to: http://localhost:8000/admin/")