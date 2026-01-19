import requests
import json

# Test sending a booking to the proxy server
test_booking = {
    "api_key": "UNC-TEST123456789",
    "booking_id": "BK202511283924",
    "customer_name": "ABHISHEK SINGH",
    "customer_phone": "7701873768",
    "customer_email": "test@example.com",
    "customer_address": "Test Address",
    "nominee_name": "Test Nominee",
    "unit_type": "3BHK",
    "unit_number": "A-101",
    "area": "1200 sq ft",
    "total_amount": "5000000.00",
    "booking_amount": "500000.00",
    "project_name": "Aspire Leisure Valley",
    "project_location": "Test Location",
    "developer": "Test Developer",
    "cp_code": "BH494170",
    "cp_company": "Romil saxena",
    "cp_name": "Business Head",
    "cp_phone": "8888888888",
    "cp_email": "cp@test.com",
    "status": "confirmed",
    "created_at": "2025-01-01T10:00:00Z",
    "booking_source": "web_form"
}

try:
    print("Testing proxy server...")
    
    # Send to proxy server (which should forward to CRM)
    response = requests.post("http://localhost:3000/api/booking-webhook", json=test_booking, timeout=10)
    print(f"Proxy response: {response.status_code} - {response.json()}")
    
    # Check if it reached your CRM
    import os
    import django
    import sys
    
    sys.path.append('.')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
    django.setup()
    
    from leads.booking_models import UnitedNetworkBooking
    count = UnitedNetworkBooking.objects.count()
    print(f"Bookings in CRM after test: {count}")
    
    if count > 0:
        latest = UnitedNetworkBooking.objects.latest('received_at')
        print(f"Latest booking: {latest.booking_id} - {latest.customer_name}")
    
except Exception as e:
    print(f"Error: {e}")