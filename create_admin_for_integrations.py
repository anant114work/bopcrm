#!/usr/bin/env python
import os
import sys
import django

sys.path.append('d:\\AI-proto\\CRM\\drip')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from django.contrib.auth.models import User

# Create or update admin user
admin_user, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@crm.com',
        'is_staff': True,
        'is_superuser': True,
        'is_active': True
    }
)

if created:
    admin_user.set_password('admin123')
    admin_user.save()
    print("Created admin user: admin / admin123")
else:
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.is_active = True
    admin_user.save()
    print("Updated existing admin user to have staff privileges")

print(f"Admin user '{admin_user.username}' can now access Integrations panel")
print("Login at: /admin/ or use team login with admin privileges")