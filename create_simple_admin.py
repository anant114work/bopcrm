#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

# Delete existing admin
try:
    User.objects.get(username='admin').delete()
    print("Deleted existing admin user")
except:
    print("No existing admin user found")

# Create new admin
admin = User.objects.create_superuser('admin', 'admin@test.com', 'admin123')
print("Created admin user: admin / admin123")

# Test login
test = authenticate(username='admin', password='admin123')
if test:
    print("LOGIN TEST: SUCCESS")
    print("User is active:", test.is_active)
    print("User is staff:", test.is_staff)
    print("User is superuser:", test.is_superuser)
else:
    print("LOGIN TEST: FAILED")

print("\nTry logging in with:")
print("Username: admin")
print("Password: admin123")
print("URL: http://localhost:8000/admin/")