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

# United Network CRM API Configuration
API_KEY = "UNC-XXXXXXXXXXXXXXXX"  # Replace with actual API key
BASE_URL = "https://myunitednetwork.com/v1"

headers = {
    'x-api-key': API_KEY
}

def fetch_all_bookings():
    """Fetch all real bookings from United Network CRM API"""
    
    print("Fetching real booking data from United Network CRM API...")
    print("=" * 60)
    
    # First, clear fake data
    fake_count = UnitedNetworkBooking.objects.filter(status='imported').count()
    if fake_count > 0:
        UnitedNetworkBooking.objects.filter(status='imported').delete()
        print(f"Cleared {fake_count} fake bookings")
    
    try:
        # Get API status first
        status_response = requests.get(f"{BASE_URL}/status", headers=headers, timeout=10)
        if status_response.status_code == 200:
            status_data = status_response.json()
            total_bookings = status_data.get('total_bookings', 0)
            print(f"API Status: Active")
            print(f"Total bookings available: {total_bookings}")
        else:
            print(f"API Status check failed: {status_response.status_code}")
            return
        
        # Fetch all bookings with pagination
        page = 1
        limit = 50
        all_bookings = []
        
        while True:
            print(f"\nFetching page {page}...")
            
            response = requests.get(
                f"{BASE_URL}/bookings",
                headers=headers,
                params={'page': page, 'limit': limit},
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"Error fetching page {page}: {response.status_code}")
                break
            
            data = response.json()
            bookings = data.get('data', [])
            
            if not bookings:
                break
            
            all_bookings.extend(bookings)
            print(f"Fetched {len(bookings)} bookings from page {page}")
            
            # Check if there are more pages
            if not data.get('has_next', False):
                break
            
            page += 1
        
        print(f"\nTotal bookings fetched: {len(all_bookings)}")
        
        # Save bookings to database
        created_count = 0
        updated_count = 0
        
        for booking_data in all_bookings:
            # Map API response to our model
            booking_record = {
                'api_key': API_KEY,
                'booking_id': booking_data.get('booking_id', ''),
                'customer_name': booking_data.get('customer_name', ''),
                'customer_phone': booking_data.get('customer_phone', ''),
                'customer_email': booking_data.get('customer_email', ''),
                'customer_address': booking_data.get('customer_address', ''),
                'nominee_name': booking_data.get('nominee_name', ''),
                'unit_type': booking_data.get('unit_type', ''),
                'unit_number': booking_data.get('unit_number', ''),
                'area': booking_data.get('unit_size', ''),
                'total_amount': float(booking_data.get('booking_value', 0) or 0),
                'booking_amount': float(booking_data.get('token_amount', 0) or 0),
                'project_name': booking_data.get('project_name', ''),
                'project_location': booking_data.get('project_location', ''),
                'developer': booking_data.get('developer', ''),
                'cp_code': booking_data.get('cp_code', ''),
                'cp_company': booking_data.get('cp_company', ''),
                'cp_name': booking_data.get('cp_name', ''),
                'cp_phone': booking_data.get('cp_phone', ''),
                'cp_email': booking_data.get('cp_email', ''),
                'status': booking_data.get('booking_status', 'active'),
                'booking_source': booking_data.get('booking_source', 'united_network_api'),
                'created_at': booking_data.get('booking_timestamp', '2025-01-01T10:00:00Z'),
                'raw_payload': booking_data
            }
            
            booking, created = UnitedNetworkBooking.objects.update_or_create(
                booking_id=booking_record['booking_id'],
                defaults=booking_record
            )
            
            if created:
                created_count += 1
                print(f"✓ Created: {booking.booking_id} - {booking.customer_name}")
            else:
                updated_count += 1
                print(f"↻ Updated: {booking.booking_id} - {booking.customer_name}")
        
        print(f"\n" + "=" * 60)
        print(f"Import Summary:")
        print(f"Created: {created_count}")
        print(f"Updated: {updated_count}")
        print(f"Total in CRM: {UnitedNetworkBooking.objects.count()}")
        print(f"\nRefresh your dashboard: http://localhost:8000/bookings/")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to United Network CRM API")
        print("Check if the API URL is correct and accessible")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fetch_all_bookings()