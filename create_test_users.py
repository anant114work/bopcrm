#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from django.contrib.auth.models import User

# Admin users
User.objects.create_superuser('admin', 'admin@company.com', 'Admin@123')
User.objects.create_superuser('superadmin', 'super@company.com', 'Super@456')
User.objects.create_user('manager', 'manager@company.com', 'Manager@789')

# Sales team
User.objects.create_user('sales1', 'sales1@company.com', 'Sales@123')
User.objects.create_user('sales2', 'sales2@company.com', 'Sales@456')
User.objects.create_user('sales3', 'sales3@company.com', 'Sales@789')
User.objects.create_user('manager1', 'manager1@company.com', 'SalesM@123')

# Support team
User.objects.create_user('support1', 'support1@company.com', 'Support@123')
User.objects.create_user('support2', 'support2@company.com', 'Support@456')
User.objects.create_user('supportmgr', 'supportmgr@company.com', 'SupportM@789')

# Team leads
User.objects.create_user('teamlead1', 'lead1@company.com', 'Lead@123')
User.objects.create_user('teamlead2', 'lead2@company.com', 'Lead@456')

print("All test users created successfully!")