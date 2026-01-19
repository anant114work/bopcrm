import requests
import json

print("Testing the complete pipeline...")
print("=" * 50)

# Step 1: Test if proxy is running
try:
    response = requests.get("http://localhost:3000/", timeout=5)
    print("Proxy server is running")
    print(f"Status: {response.json()}")
except:
    print("Proxy server is NOT running")
    print("Run: python united_network_proxy.py")
    exit()

# Step 2: Test if CRM is running
try:
    response = requests.get("http://localhost:8000/bookings/", timeout=5)
    print("CRM server is running")
except:
    print("CRM server is NOT running")
    print("Run: python manage.py runserver")
    exit()

# Step 3: Test the pipeline with a booking
test_booking = {
    "api_key": "UNC-PIPELINE-TEST",
    "booking_id": "BK-PIPELINE-TEST",
    "customer_name": "Pipeline Test Customer",
    "customer_phone": "9999999999",
    "customer_email": "test@pipeline.com",
    "project_name": "Pipeline Test Project",
    "unit_type": "Test Unit",
    "unit_number": "T-001",
    "area": "1000 sq ft",
    "total_amount": "1000000.00",
    "booking_amount": "100000.00",
    "status": "test",
    "created_at": "2025-01-01T10:00:00Z",
    "booking_source": "pipeline_test"
}

print("\nTesting pipeline with test booking...")

try:
    # Send to proxy (port 3000)
    response = requests.post("http://localhost:3000/api/booking-webhook", 
                           json=test_booking, timeout=10)
    
    if response.status_code == 200:
        print("Proxy received and forwarded booking")
        
        # Check if it reached CRM database
        import os
        import django
        import sys
        
        sys.path.append('.')
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
        django.setup()
        
        from leads.booking_models import UnitedNetworkBooking
        
        if UnitedNetworkBooking.objects.filter(booking_id="BK-PIPELINE-TEST").exists():
            print("Booking saved in CRM database")
            print("PIPELINE IS WORKING!")
            print("\nNow ask United Network CRM to resend all 86 bookings to localhost:3000")
        else:
            print("Booking NOT saved in CRM database")
    else:
        print(f"Proxy failed: {response.status_code}")
        
except Exception as e:
    print(f"Pipeline test failed: {e}")

print("\n" + "=" * 50)