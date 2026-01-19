import requests
import json

# Test PBX Click-to-Call API (the correct one for your account)
url = "https://api.acefone.in/v1/click_to_call"

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "Authorization": "Bearer 33362aae-b70b-4e94-b91c-5a6a9fc1701a"
}

payload = {
    "agent_number": "919180624516",  # Anant's actual phone number
    "destination_number": "918527288313",  # Customer number
    "async": "1"
}

print("TESTING PBX CLICK-TO-CALL API")
print(f"URL: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")
print("=" * 50)

try:
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")
    
    if response.status_code == 200:
        print("\nSUCCESS! Anant's phone should ring!")
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
print("If successful, Anant's phone (+919180624516) should ring!")