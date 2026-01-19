from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

# Your CRM endpoints
CRM_BASE_URL = "http://localhost:8000"
BOOKING_WEBHOOK_URL = f"{CRM_BASE_URL}/api/booking-webhook/"
BULK_BOOKINGS_URL = f"{CRM_BASE_URL}/api/bulk-bookings/"

@app.route('/')
def home():
    return jsonify({
        'status': 'United Network CRM Proxy Running',
        'forwarding_to': CRM_BASE_URL,
        'endpoints': {
            'individual_bookings': '/api/booking-webhook',
            'bulk_bookings': '/api/bulk-bookings'
        }
    })

@app.route('/api/booking-webhook', methods=['POST'])
def forward_booking():
    try:
        # Get data from United Network CRM
        data = request.get_json()
        print(f"\n=== RECEIVED BOOKING FROM UNITED NETWORK ===")
        print(f"Booking ID: {data.get('booking_id', 'Unknown')}")
        print(f"Customer: {data.get('customer_name', 'Unknown')}")
        print(f"Project: {data.get('project_name', 'Unknown')}")
        print(f"Amount: ₹{data.get('total_amount', 'Unknown')}")
        print(f"API Key: {data.get('api_key', 'Unknown')}")
        print(f"Full Data: {data}")
        print("=" * 50)
        
        # Forward to your CRM
        response = requests.post(BOOKING_WEBHOOK_URL, json=data, timeout=10)
        print(f"Forwarded to CRM: Status {response.status_code}")
        
        # Return United Network's expected response
        return jsonify({
            'success': True,
            'booking_id': data.get('booking_id'),
            'message': 'Booking received and forwarded'
        })
        
    except Exception as e:
        print(f"Error forwarding booking: {e}")
        return jsonify({'error': 'Failed to process booking'}), 500

@app.route('/api/bulk-bookings', methods=['POST'])
def forward_bulk_bookings():
    try:
        # Get bulk data from United Network CRM
        data = request.get_json()
        bookings_count = len(data.get('bookings', []))
        print(f"\n=== RECEIVED BULK BOOKINGS FROM UNITED NETWORK ===")
        print(f"Total Bookings: {bookings_count}")
        print(f"API Key: {data.get('api_key', 'Unknown')}")
        print(f"Type: {data.get('type', 'Unknown')}")
        if bookings_count > 0:
            first_booking = data.get('bookings', [])[0]
            print(f"First Booking: {first_booking.get('booking_id', 'Unknown')} - {first_booking.get('customer_name', 'Unknown')}")
        print("=" * 50)
        
        # Forward to your CRM
        response = requests.post(BULK_BOOKINGS_URL, json=data, timeout=30)
        print(f"Forwarded bulk to CRM: Status {response.status_code}")
        
        # Return United Network's expected response
        return jsonify({
            'success': True,
            'total_received': bookings_count,
            'message': 'Bulk bookings received and forwarded'
        })
        
    except Exception as e:
        print(f"Error forwarding bulk bookings: {e}")
        return jsonify({'error': 'Failed to process bulk bookings'}), 500

@app.route('/api/bookings')
def show_bookings():
    try:
        # Get bookings from your CRM
        response = requests.get(f"{CRM_BASE_URL}/bookings/api/")
        return response.json()
    except:
        return jsonify({'error': 'Cannot connect to CRM'})

if __name__ == '__main__':
    print("Starting United Network CRM Proxy Server")
    print("Listening on: http://localhost:3000")
    print("Forwarding to: http://localhost:8000")
    print("=" * 50)
    app.run(host='0.0.0.0', port=3000, debug=True)