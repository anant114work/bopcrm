import requests
import json

# Test REAL Click-to-Call Support API
url = "https://api.acefone.in/v1/click_to_call_support"

# Your credentials
api_key = "33362aae-b70b-4e94-b91c-5a6a9fc1701a"
test_customer_number = "918527288313"  # Real test number

headers = {
    "accept": "application/json",
    "content-type": "application/json"
}

payload = {
    "customer_number": test_customer_number,
    "api_key": api_key,
    "async": 1,
    "customer_ring_timeout": 30
}

print("TESTING REAL CLICK-TO-CALL SUPPORT API")
print(f"URL: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")
print("=" * 50)

try:
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Text: {response.text}")
    
    if response.status_code == 200:
        print("\nSUCCESS! Call should be initiated!")
        try:
            data = response.json()
            print(f"Response JSON: {json.dumps(data, indent=2)}")
        except:
            print("Response is not JSON")
    else:
        print(f"\nFAILED! Status: {response.status_code}")
        
except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "=" * 50)
print("If successful, your agent phone should ring!")