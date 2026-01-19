import os
import django
import sys

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.booking_models import UnitedNetworkBooking

# Clear all test bookings
count = UnitedNetworkBooking.objects.count()
UnitedNetworkBooking.objects.all().delete()

print(f"Cleared {count} test bookings from database")
print("Database is now empty and ready for real United Network CRM data")