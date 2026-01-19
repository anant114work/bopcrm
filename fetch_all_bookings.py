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

def fetch_bookings_from_united_network():
    """Fetch all bookings from United Network CRM test receiver"""
    try:
        # Try to get bookings from their test receiver
        response = requests.get("http://localhost:3000/api/bookings", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            bookings = data.get('bookings', [])
            
            print(f"Found {len(bookings)} bookings from United Network CRM")
            
            created_count = 0
            updated_count = 0
            
            for booking_data in bookings:
                # Create booking in your CRM
                booking, created = UnitedNetworkBooking.objects.update_or_create(
                    booking_id=booking_data.get('booking_id'),
                    defaults={
                        'api_key': booking_data.get('api_key', 'UNC-IMPORTED'),
                        'customer_name': booking_data.get('customer_name', ''),
                        'customer_phone': booking_data.get('customer_phone', ''),
                        'customer_email': booking_data.get('customer_email', ''),
                        'customer_address': booking_data.get('customer_address', ''),
                        'nominee_name': booking_data.get('nominee_name', ''),
                        'unit_type': booking_data.get('unit_type', ''),
                        'unit_number': booking_data.get('unit_number', ''),
                        'area': booking_data.get('area', ''),
                        'total_amount': float(booking_data.get('total_amount', 0) or 0),
                        'booking_amount': float(booking_data.get('booking_amount', 0) or 0),
                        'project_name': booking_data.get('project_name', ''),
                        'project_location': booking_data.get('project_location', ''),
                        'developer': booking_data.get('developer', ''),
                        'cp_code': booking_data.get('cp_code', ''),
                        'cp_company': booking_data.get('cp_company', ''),
                        'cp_name': booking_data.get('cp_name', ''),
                        'cp_phone': booking_data.get('cp_phone', ''),
                        'cp_email': booking_data.get('cp_email', ''),
                        'status': booking_data.get('status', 'imported'),
                        'booking_source': booking_data.get('booking_source', 'import'),
                        'created_at': booking_data.get('created_at', '2025-01-01T10:00:00Z'),
                        'raw_payload': booking_data
                    }
                )
                
                if created:
                    created_count += 1
                    print(f"Created: {booking.booking_id} - {booking.customer_name}")
                else:
                    updated_count += 1
                    print(f"Updated: {booking.booking_id} - {booking.customer_name}")
            
            print(f"\nImport complete!")
            print(f"Created: {created_count}")
            print(f"Updated: {updated_count}")
            print(f"Total bookings in CRM: {UnitedNetworkBooking.objects.count()}")
            
        else:
            print(f"Failed to fetch bookings: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("Cannot connect to United Network CRM at localhost:3000")
        print("Make sure their test receiver is running")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fetch_bookings_from_united_network()