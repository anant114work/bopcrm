#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from tata_integration.models import TataCall
from datetime import datetime

# Delete calls with no customer number and same timestamp (fake data)
fake_calls = TataCall.objects.filter(
    customer_number='',
    start_stamp__date=datetime(2025, 10, 13).date(),
    start_stamp__time=datetime.strptime('11:35:05', '%H:%M:%S').time()
)

print(f"Found {fake_calls.count()} fake calls to delete")
deleted_count = fake_calls.count()
fake_calls.delete()
print(f"Deleted {deleted_count} fake calls")

# Also delete any calls without customer numbers
no_number_calls = TataCall.objects.filter(customer_number='')
print(f"Found {no_number_calls.count()} calls without customer numbers")
no_number_deleted = no_number_calls.count()
no_number_calls.delete()
print(f"Deleted {no_number_deleted} calls without customer numbers")

print("Cleanup completed!")