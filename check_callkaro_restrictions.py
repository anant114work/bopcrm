#!/usr/bin/env python3
"""
Check CallKaro AI for time restrictions and account status
"""

import requests
import json
from datetime import datetime, time
import os
import sys

def check_callkaro_restrictions():
    """Check for potential CallKaro restrictions"""
    
    api_key = "bc422db39aa327234a911dd901accfcfa975623ee84c65c83aae9c4f844ffdb8"
    
    print(f"\n{'='*60}")
    print(f"CALLKARO RESTRICTION CHECKER")
    print(f"{'='*60}")
    
    current_time = datetime.now()
    current_hour = current_time.hour
    
    print(f"Current Time: {current_time.strftime('%H:%M:%S')} IST")
    print(f"Current Hour: {current_hour}")
    
    # Check if it's within typical business hours
    if 9 <= current_hour <= 21:
        print("[OK] Within typical business hours (9 AM - 9 PM)")
    else:
        print("[WARNING] Outside typical business hours (9 AM - 9 PM)")
        print("  This might be why calls aren't connecting!")
    
    # Test with a simple API call to check account status
    print(f"\nTesting API with minimal payload...")
    
    payload = {
        "to_number": "+919999999999",  # Test number
        "agent_id": "692d5b6ad10e948b7bbfc2db",  # AU Realty Agent 1
        "metadata": {
            "test": True,
            "time_check": current_time.isoformat()
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": api_key
    }
    
    try:
        response = requests.post(
            "https://api.callkaro.ai/call/outbound",
            json=payload,
            headers=headers,
            timeout=10
        )
        
        print(f"API Response Status: {response.status_code}")
        print(f"API Response Body: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            
            # Check the response structure
            if 'call_sid' in result and 'status' in result:
                if result['status'] == 'done':
                    print("[OK] API accepts calls but status is 'done' immediately")
                    print("  This suggests calls are being queued but not executed")
                    print("  Possible reasons:")
                    print("  - Time restrictions on CallKaro side")
                    print("  - Agent is configured with specific calling hours")
                    print("  - Account has calling restrictions")
                else:
                    print(f"Status: {result['status']}")
            
            if 'call_id' in result:
                print(f"Call ID: {result['call_id']}")
            else:
                print("[WARNING] No call_id in response - calls might not be actually placed")
        
        else:
            print(f"[ERROR] API Error: {response.text}")
    
    except Exception as e:
        print(f"[ERROR] Request Error: {str(e)}")
    
    print(f"\n{'='*60}")
    print(f"RECOMMENDATIONS:")
    print(f"{'='*60}")
    
    if current_hour < 9 or current_hour > 21:
        print("1. [TIME] WAIT FOR BUSINESS HOURS: Try calling between 9 AM - 9 PM IST")
    
    print("2. [CHECK] CALLKARO DASHBOARD:")
    print("   - Login to CallKaro portal")
    print("   - Check call logs and status")
    print("   - Verify agent configurations")
    print("   - Check account balance/limits")
    
    print("3. [TEST] TEST WITH KNOWN NUMBER:")
    print("   - Try calling your own number to test")
    
    print("4. [AGENT] AGENT CONFIGURATION:")
    print("   - Agents might have specific calling schedules")
    print("   - Check if agents are active during current time")
    
    print("5. [SUPPORT] CONTACT SUPPORT:")
    print("   - If API returns success but no calls connect")
    print("   - Ask about time restrictions and account limits")

if __name__ == "__main__":
    check_callkaro_restrictions()