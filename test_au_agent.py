#!/usr/bin/env python3
"""
Test only the au-reality agent that's working
"""
import requests
import json

def test_au_agent():
    api_key = "bc422db39aa327234a911dd901accfcfa975623ee84c65c83aae9c4f844ffdb8"
    agent_id = "69294d3d2cc1373b1f3a3972"  # au-reality agent
    
    # Test with a real number from your logs
    test_phone = "+919129784148"  # This was successfully called earlier
    
    payload = {
        "to_number": test_phone,
        "agent_id": agent_id,
        "metadata": {
            "source": "test_call",
            "project": "AU Aspire Leisure Valley",
            "test": True
        },
        "priority": 1
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": api_key
    }
    
    print("=" * 60)
    print("TESTING AU-REALITY AGENT")
    print("=" * 60)
    print(f"Agent ID: {agent_id}")
    print(f"Phone: {test_phone}")
    print(f"API Key: {api_key[:20]}...")
    print("=" * 60)
    
    try:
        response = requests.post(
            "https://api.callkaro.ai/call/outbound",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            api_response = response.json()
            call_sid = api_response.get('call_sid')
            print(f"\nSUCCESS!")
            print(f"Call SID: {call_sid}")
            print(f"Message: {api_response.get('message')}")
            print(f"\nCheck your Call Karo dashboard for call ID: {call_sid}")
            return True
        else:
            print(f"\nFAILED: {response.text}")
            return False
            
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        return False

if __name__ == "__main__":
    test_au_agent()