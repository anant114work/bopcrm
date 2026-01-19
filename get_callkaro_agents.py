import requests

api_key = "bc422db39aa327234a911dd901accfcfa975623ee84c65c83aae9c4f844ffdb8"

response = requests.get(
    "https://api.callkaro.ai/agent",
    headers={
        "X-API-KEY": api_key
    }
)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    agents = response.json()
    print(f"\nTotal agents: {len(agents)}\n")
    for agent in agents:
        print(f"Name: {agent.get('name')}")
        print(f"ID: {agent.get('_id')}")
        print(f"Phone: {agent.get('phone_number')}")
        print("-" * 60)
else:
    print(f"Error: {response.text}")
