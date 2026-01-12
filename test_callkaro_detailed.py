#!/usr/bin/env python3
"""
Detailed Call Karo AI API test with full debugging
"""
import requests
import json

def test_callkaro_detailed():
    api_key = "bc422db39aa327234a911dd901accfcfa975623ee84c65c83aae9c4f844ffdb8"
    
    # Test different agent IDs
    agents = {
        "au-reality": "69294d3d2cc1373b1f3a3972",
        "gaur-yamuna": "6923ff797a5d5a94d5a5dfcf", 
        "au-reality-2": "692d5b6ad10e948b7bbfc2db"
    }
    
    # Test with your own number first
    test_phone = "+917943595065"  # Your number from the logs
    
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": api_key
    }
    
    print("=" * 80)
    print("DETAILED CALL KARO AI API TEST")
    print("=" * 80)
    
    # Test 1: Check API status
    try:
        status_response = requests.get("https://api.callkaro.ai/status", headers=headers, timeout=10)
        print(f"API Status Check: {status_response.status_code}")
        if status_response.status_code == 200:
            print(f"Status Response: {status_response.text}")
    except Exception as e:
        print(f"Status check failed: {e}")
    
    print("-" * 80)
    
    # Test 2: Try each agent
    for agent_name, agent_id in agents.items():
        print(f"\nTesting Agent: {agent_name} ({agent_id})")
        
        payload = {
            "to_number": test_phone,
            "agent_id": agent_id,
            "metadata": {
                "source": "api_test",
                "test": True,
                "agent_name": agent_name
            },
            "priority": 1
        }
        
        try:
            response = requests.post(
                "https://api.callkaro.ai/call/outbound",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                call_sid = result.get('call_sid')
                print(f"Call SID: {call_sid}")
                
                # Try to get call status
                if call_sid:
                    try:
                        status_response = requests.get(
                            f"https://api.callkaro.ai/call/{call_sid}",
                            headers=headers,
                            timeout=10
                        )
                        print(f"Call Status Check: {status_response.status_code}")
                        print(f"Call Status: {status_response.text}")
                    except Exception as e:
                        print(f"Status check failed: {e}")
            
        except Exception as e:
            print(f"Error: {e}")
        
        print("-" * 40)
    
    # Test 3: Check account info
    try:
        account_response = requests.get("https://api.callkaro.ai/account", headers=headers, timeout=10)
        print(f"\nAccount Info: {account_response.status_code}")
        if account_response.status_code == 200:
            print(f"Account: {account_response.text}")
    except Exception as e:
        print(f"Account check failed: {e}")

if __name__ == "__main__":
    test_callkaro_detailed()