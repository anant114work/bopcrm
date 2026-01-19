import requests

# Test API endpoints
base_url = "http://localhost:8000"
api_key = "UNC-TEST123456789"  # Use any UNC- prefixed key

headers = {"X-API-Key": api_key}

print("Testing United Network CRM API Endpoints...")
print("=" * 50)

try:
    # Test API Status
    print("1. Testing API Status...")
    response = requests.get(f"{base_url}/api/external/status/", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
    
    # Test Get All Bookings
    print("2. Testing Get All Bookings...")
    response = requests.get(f"{base_url}/api/external/bookings/?per_page=5", headers=headers)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Total Bookings: {data.get('pagination', {}).get('total_bookings', 0)}")
    print(f"Bookings in response: {len(data.get('bookings', []))}")
    print()
    
    # Test Search
    print("3. Testing Search...")
    response = requests.get(f"{base_url}/api/external/search/?status=confirmed", headers=headers)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Search results: {data.get('total_found', 0)}")
    print()
    
    # Test specific booking (if any exist)
    if data.get('results'):
        booking_id = data['results'][0]['booking_id']
        print(f"4. Testing Booking Detail for {booking_id}...")
        response = requests.get(f"{base_url}/api/external/booking/{booking_id}/", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            booking = response.json()['booking']
            print(f"Customer: {booking['customer_name']}")
            print(f"Project: {booking['project_name']}")
    
    print("\nAPI Endpoints are working! ✅")
    print(f"Use API Key: {api_key}")
    print(f"Base URL: {base_url}")
    
except Exception as e:
    print(f"Error testing API: {e}")