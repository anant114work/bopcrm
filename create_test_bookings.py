import os
import django
import sys
from datetime import datetime, timedelta
from django.utils import timezone

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.booking_models import UnitedNetworkBooking

# Create test booking data
test_bookings = [
    {
        'api_key': 'UNC-ABC123456789',
        'booking_id': 'BK202501011234',
        'customer_name': 'John Doe',
        'customer_phone': '9876543210',
        'customer_email': 'john@example.com',
        'customer_address': '123 Main Street, Delhi',
        'nominee_name': 'Jane Doe',
        'unit_type': '3BHK',
        'unit_number': 'A-101',
        'area': '1200 sq ft',
        'total_amount': 5000000.00,
        'booking_amount': 500000.00,
        'project_name': 'Dream Residency',
        'project_location': 'Sector 62, Noida',
        'developer': 'ABC Developers',
        'cp_code': 'CP123456',
        'cp_company': 'XYZ Properties',
        'cp_name': 'Channel Partner Name',
        'cp_phone': '9876543210',
        'cp_email': 'cp@example.com',
        'status': 'confirmed',
        'booking_source': 'web_form',
        'created_at': timezone.now() - timedelta(hours=2),
        'raw_payload': {'test': 'data'}
    },
    {
        'api_key': 'UNC-DEF987654321',
        'booking_id': 'BK202501011235',
        'customer_name': 'Priya Sharma',
        'customer_phone': '9123456789',
        'customer_email': 'priya@example.com',
        'customer_address': '456 Park Avenue, Mumbai',
        'nominee_name': 'Raj Sharma',
        'unit_type': '2BHK',
        'unit_number': 'B-205',
        'area': '950 sq ft',
        'total_amount': 3500000.00,
        'booking_amount': 350000.00,
        'project_name': 'Luxury Heights',
        'project_location': 'Bandra West, Mumbai',
        'developer': 'Premium Builders',
        'cp_code': 'CP789012',
        'cp_company': 'Elite Realty',
        'cp_name': 'Amit Kumar',
        'cp_phone': '9988776655',
        'cp_email': 'amit@eliterealty.com',
        'status': 'pending',
        'booking_source': 'mobile_app',
        'created_at': timezone.now() - timedelta(hours=5),
        'raw_payload': {'test': 'data2'}
    },
    {
        'api_key': 'UNC-GHI456789123',
        'booking_id': 'BK202501011236',
        'customer_name': 'Rajesh Gupta',
        'customer_phone': '9555444333',
        'customer_email': 'rajesh@example.com',
        'customer_address': '789 Business District, Gurgaon',
        'nominee_name': 'Sunita Gupta',
        'unit_type': '4BHK',
        'unit_number': 'C-301',
        'area': '1800 sq ft',
        'total_amount': 8500000.00,
        'booking_amount': 850000.00,
        'project_name': 'Executive Towers',
        'project_location': 'Golf Course Road, Gurgaon',
        'developer': 'Metro Constructions',
        'cp_code': 'CP345678',
        'cp_company': 'Prime Properties',
        'cp_name': 'Neha Singh',
        'cp_phone': '9777888999',
        'cp_email': 'neha@primeproperties.com',
        'status': 'requested',
        'booking_source': 'web_form',
        'created_at': timezone.now() - timedelta(days=1),
        'raw_payload': {'test': 'data3'}
    }
]

print("Creating test booking data...")

for booking_data in test_bookings:
    booking, created = UnitedNetworkBooking.objects.get_or_create(
        booking_id=booking_data['booking_id'],
        defaults=booking_data
    )
    if created:
        print(f"Created booking: {booking.booking_id} - {booking.customer_name}")
    else:
        print(f"Booking already exists: {booking.booking_id}")

print(f"\nTotal bookings in database: {UnitedNetworkBooking.objects.count()}")
print("Test data creation complete!")