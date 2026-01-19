#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from django.contrib.auth.models import User
from leads.models import TeamMember

# Create Django admin user
admin_user, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@crm.com',
        'is_staff': True,
        'is_superuser': True
    }
)
admin_user.set_password('password123')
admin_user.save()

# Create TeamMember for CRM access
team_admin, created = TeamMember.objects.get_or_create(
    name='ADMIN USER',
    defaults={
        'email': 'admin@crm.com',
        'phone': '9999999999',
        'role': 'Admin',
        'is_active': True
    }
)

print("CREATED CRM ADMIN ACCESS:")
print("Django Admin: admin / password123 -> http://localhost:8000/admin/")
print("CRM Access: ADMIN / 9999999999 -> http://localhost:8000/")
print("\nFor full CRM access, use: ADMIN / 9999999999")