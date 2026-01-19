#!/usr/bin/env python3
"""
Direct test of Call Karo AI API
"""
import requests
import json

def test_callkaro_api():
    api_key = "bc422db39aa327234a911dd901accfcfa975623ee84c65c83aae9c4f844ffdb8"
    agent_id = "69294d3d2cc1373b1f3a3972"  # AU Realty Agent 2
    
    # Test with a valid Indian number format
    test_phone = "+917011628053"
    
    payload = {
        "to_number": test_phone,
        "agent_id": agent_id,
        "metadata": {
            "source": "direct_test",
            "project": "Test Call",
            "test": True
        },
        "priority": 1
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": api_key
    }
    
    print("=" * 60)
    print("DIRECT CALL KARO AI API TEST")
    print("=" * 60)
    print(f"API Key: {api_key[:20]}...")
    print(f"Agent ID: {agent_id}")
    print(f"Phone: {test_phone}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("=" * 60)
    
    try:
        response = requests.post(
            "https://api.callkaro.ai/call/outbound",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            print("\nSUCCESS: Call Karo AI API is working!")
            return True
        else:
            print(f"\nFAILED: API returned {response.status_code}")
            return False
            
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        return False

if __name__ == "__main__":
    test_callkaro_api()