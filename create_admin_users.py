#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from django.contrib.auth.models import User

# Delete existing admin users if they exist
User.objects.filter(username__in=['admin', 'superadmin', 'manager']).delete()

# Create new admin users
admin = User.objects.create_superuser('admin', 'admin@company.com', 'admin123')
superadmin = User.objects.create_superuser('superadmin', 'super@company.com', 'super123')
manager = User.objects.create_user('manager', 'manager@company.com', 'manager123')
manager.is_staff = True
manager.save()

print("ADMIN USERS CREATED:")
print("admin / admin123")
print("superadmin / super123") 
print("manager / manager123")
print("\nLogin at: http://localhost:8000/admin/")