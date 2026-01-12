import requests

try:
    # Check if proxy is running
    response = requests.get("http://localhost:3000/", timeout=5)
    print("Proxy server status:", response.json())
    
    # Check if CRM is running
    crm_response = requests.get("http://localhost:8000/bookings/api/", timeout=5)
    print("CRM bookings API:", crm_response.json())
    
except Exception as e:
    print(f"Error checking servers: {e}")