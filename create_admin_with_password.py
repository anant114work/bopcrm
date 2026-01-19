#!/usr/bin/env python
import os
import sys
import django

sys.path.append('d:\\AI-proto\\CRM\\drip')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from django.contrib.auth.models import User

# Create admin with known password
admin_user, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@crm.com',
        'is_staff': True,
        'is_superuser': True,
        'is_active': True
    }
)

# Set password
admin_user.set_password('admin123')
admin_user.is_staff = True
admin_user.is_superuser = True
admin_user.save()

print("=== ADMIN USER READY ===")
print(f"Username: {admin_user.username}")
print("Password: admin123")
print(f"Is Staff: {admin_user.is_staff}")
print(f"Can access integrations: {admin_user.is_staff}")
print("\nLogin with these credentials to see the Integrations panel!")