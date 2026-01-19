import requests

api_key = "bc422db39aa327234a911dd901accfcfa975623ee84c65c83aae9c4f844ffdb8"
agent_id = "69609b8f9cd0a3ca06a3792b"

# Test with a sample number
payload = {
    "to_number": "+918527288313",
    "agent_id": agent_id,
    "metadata": {
        "name": "Test User",
        "source": "test_spj_agent",
        "project": "SPJ Vedatam"
    },
    "priority": 1,
    "language": "hi"
}

print(f"Testing SPJ Vedatam Agent")
print(f"Agent ID: {agent_id}")
print(f"To: +918527288313")

response = requests.post(
    "https://api.callkaro.ai/call/outbound",
    json=payload,
    headers={
        "Content-Type": "application/json",
        "X-API-KEY": api_key
    },
    timeout=10
)

print(f"\nStatus: {response.status_code}")
print(f"Response: {response.text}")
