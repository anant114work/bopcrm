import requests
import json

# Test the webhook with your actual lead data
webhook_url = "http://127.0.0.1:8000/google-sheets-webhook/"

# Sample lead from your data
test_lead = {
    "name": "Anil Kumar",
    "phone": "7015837345", 
    "email": "anilparbhuwala1@gmail.com",
    "unit_size": "2 BHK",
    "project_name": "AU Aspire Form",
    "ip": "192.168.1.1",
    "timestamp": "19/11/2025 17:11:25"
}

print("Testing webhook with your lead data...")
print(f"URL: {webhook_url}")
print(f"Data: {test_lead}")

try:
    response = requests.post(
        webhook_url,
        json=test_lead,
        headers={'Content-Type': 'application/json'},
        timeout=10
    )
    
    print(f"\nResponse Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("✅ Webhook is working!")
    else:
        print("❌ Webhook failed")
        
except Exception as e:
    print(f"❌ Error: {e}")