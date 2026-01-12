import requests

# Test United Network CRM API
API_KEY = "UNC-TEST123456789"  # Try with test key first
BASE_URL = "https://myunitednetwork.com/v1"

headers = {
    'x-api-key': API_KEY
}

print("Testing United Network CRM API...")
print("=" * 50)

# Test API Status
try:
    response = requests.get(f"{BASE_URL}/status", headers=headers, timeout=10)
    print(f"API Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✓ API is accessible")
        print(f"Total bookings: {data.get('total_bookings', 'Unknown')}")
        print(f"Service: {data.get('service', 'Unknown')}")
        
        # Test getting bookings
        print("\nTesting bookings endpoint...")
        bookings_response = requests.get(f"{BASE_URL}/bookings?limit=5", headers=headers, timeout=10)
        print(f"Bookings endpoint: {bookings_response.status_code}")
        
        if bookings_response.status_code == 200:
            bookings_data = bookings_response.json()
            print(f"✓ Found {bookings_data.get('count', 0)} bookings in response")
            
            if bookings_data.get('data'):
                first_booking = bookings_data['data'][0]
                print(f"Sample booking: {first_booking.get('booking_id')} - {first_booking.get('customer_name')}")
        else:
            print("❌ Bookings endpoint failed")
            
    else:
        print("❌ API not accessible")
        print(f"Response: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to United Network CRM API")
    print("The API might not be available at https://myunitednetwork.com/v1")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 50)
print("If API is working, update the API key in fetch_real_bookings.py")