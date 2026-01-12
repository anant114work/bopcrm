import requests

# Test which agent your token calls
url = "https://api.acefone.in/v1/click_to_call_support"
token = "33362aae-b70b-4e94-b91c-5a6a9fc1701a"

headers = {
    "accept": "application/json",
    "content-type": "application/json"
}

payload = {
    "customer_number": "919876543210",  # Test number
    "api_key": token,
    "async": 1
}

print("Testing which agent receives calls...")
response = requests.post(url, json=payload, headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 200:
    print("\n✅ Call initiated successfully!")
    print("🔍 Check your call logs to see which agent received this call")
    print("📞 Expected: Anant Sharma (919180624516)")
    print("📞 Actual: Check the call records in your Acefone dashboard")
else:
    print(f"\n❌ Call failed: {response.text}")