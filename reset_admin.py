#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from django.contrib.auth.models import User

# Delete ALL admin users
User.objects.filter(is_superuser=True).delete()
print("Deleted all existing admin users")

# Create fresh admin
admin = User.objects.create_superuser(
    username='admin',
    email='admin@test.com', 
    password='password123'
)
print("Created: admin / password123")

# Test it
from django.contrib.auth import authenticate
test = authenticate(username='admin', password='password123')
print(f"Test result: {test is not None}")

print("\nTRY THIS LOGIN:")
print("Username: admin")
print("Password: password123")
print("URL: http://localhost:8000/admin/")