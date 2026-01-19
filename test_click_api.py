import requests
import json

# Test Click-to-Call Support API
url = "https://api.acefone.in/v1/click-to-call/support"
token = "33362aae-b70b-4e94-b91c-5a6a9fc1701a"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

payload = {
    "agent_number": "918062451617",
    "customer_number": "919876543210"  # Test number
}

print("Testing Click-to-Call Support API...")
print(f"URL: {url}")
print(f"Headers: {headers}")
print(f"Payload: {payload}")

try:
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Text: {response.text}")
    
    if response.content:
        try:
            data = response.json()
            print(f"Response JSON: {json.dumps(data, indent=2)}")
        except:
            print("Response is not valid JSON")
    
except Exception as e:
    print(f"Error: {e}")