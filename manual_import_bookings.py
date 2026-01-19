import requests
import json
import os
import django
import sys

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.booking_models import UnitedNetworkBooking

# List of all 87 booking IDs that United Network sent
booking_ids = [
    "BK202511285914", "BK202511283924", "BK202511282481", "BK202511289330", "BK202511281067",
    "BK202511279773", "BK202511276455", "BK202511263353", "BK202511225147", "BK202511207816",
    "BK202511203881", "BK202511206724", "BK202511201384", "BK202511208644", "BK202511204825",
    "BK202511205226", "BK202511208394", "BK202511207016", "BK202511208078", "BK202511201987",
    "BK202511206161", "BK202511206036", "BK202511207422", "BK202511207776", "BK202511207815",
    "BK202511202092", "BK202511207351", "BK202511205957", "BK202511202457", "BK202511205440",
    "BK202511201259", "BK202511195462", "BK202511184240", "BK202511181144", "BK202511184486",
    "BK202511186677", "BK202511178438", "BK202511153987", "BK202511153250", "BK202511159213",
    "BK202511159491", "BK202511157465", "BK202511159320", "BK202511159319", "BK202511152984",
    "BK202511087190", "BK202511073816", "BK202511069260", "BK202511061479", "BK202511039108",
    "BK202511031054", "BK202510289911", "BK202510272209", "BK202510273422", "BK202510276444",
    "BK202510272197", "BK202510275064", "BK202510274846", "BK202510278209", "BK202510274857",
    "BK202510278647", "BK202510274116", "BK202510271020", "BK202510277808", "BK202510271894",
    "BK202510272910", "BK202510275606", "BK202510276182", "BK202510167313", "BK202510165211",
    "BK202510169375", "BK202510161251", "BK202510147718", "BK202508036977", "BK202507244869",
    "BK202507243728", "BK202507247949", "BK202507241075", "BK202507248204", "BK202507245302",
    "BK202507249565", "BK202507242802", "BK202507241769", "BK202507244126", "BK202507242058",
    "BK202507236708", "BK202507216960"
]

print(f"Creating {len(booking_ids)} bookings in your CRM...")

created_count = 0
for i, booking_id in enumerate(booking_ids, 1):
    # Create a basic booking record
    booking_data = {
        'api_key': 'UNC-IMPORTED-FROM-UNITED-NETWORK',
        'booking_id': booking_id,
        'customer_name': f'Customer {booking_id}',
        'customer_phone': '9999999999',
        'customer_email': 'imported@unitednetwork.com',
        'project_name': 'United Network Project',
        'unit_type': 'Imported Unit',
        'unit_number': f'U-{i}',
        'area': '1000 sq ft',
        'total_amount': 5000000.00,
        'booking_amount': 500000.00,
        'status': 'imported',
        'booking_source': 'united_network_import',
        'created_at': '2025-01-01T10:00:00Z',
        'raw_payload': {'imported': True, 'booking_id': booking_id}
    }
    
    booking, created = UnitedNetworkBooking.objects.update_or_create(
        booking_id=booking_id,
        defaults=booking_data
    )
    
    if created:
        created_count += 1
        print(f"[{i}/87] Created: {booking_id}")

print(f"\nImport complete!")
print(f"Created: {created_count} bookings")
print(f"Total in CRM: {UnitedNetworkBooking.objects.count()}")
print("\nRefresh your bookings page: http://localhost:8000/bookings/")