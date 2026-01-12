#!/usr/bin/env python3
"""
Retry calls that were USER_UNAVAILABLE from Call Karo logs
"""
import requests
import json

def retry_unavailable_calls():
    # Numbers that showed USER_UNAVAILABLE in your logs
    unavailable_numbers = [
        "+917058792708",
        "+919811868611", 
        "+919650296565",
        "+919999710075",
        "+919650189757",
        "+919212109002",
        "+919999715025",
        "+919716881663",
        "+919910487432",
        "+918955351317",
        "+917303511876",
        "+918650284718",
        "+919899302383",
        "+919580659661",
        "+919129784148",
        "+919140980043",
        "+916395068729",
        "+919266283877",
        "+919302160324",
        "+918448734630",
        "+919266462825",
        "+918178896930"
    ]
    
    api_key = "bc422db39aa327234a911dd901accfcfa975623ee84c65c83aae9c4f844ffdb8"
    agent_id = "69294d3d2cc1373b1f3a3972"  # au-reality
    
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": api_key
    }
    
    print("=" * 60)
    print("RETRYING UNAVAILABLE NUMBERS")
    print("=" * 60)
    
    success_count = 0
    failed_count = 0
    
    for phone in unavailable_numbers[:5]:  # Retry first 5 numbers
        payload = {
            "to_number": phone,
            "agent_id": agent_id,
            "metadata": {
                "name": "Retry Call",
                "source": "retry_unavailable",
                "project": "AU Aspire Leisure Valley"
            },
            "priority": 1,
            "language": "hi"
        }
        
        try:
            print(f"\nRetrying: {phone}")
            response = requests.post(
                "https://api.callkaro.ai/call/outbound",
                json=payload,
                headers=headers,
                timeout=10
            )
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                success_count += 1
                print("✅ SUCCESS")
            else:
                failed_count += 1
                print("❌ FAILED")
                
        except Exception as e:
            print(f"ERROR: {e}")
            failed_count += 1
    
    print(f"\n" + "=" * 60)
    print(f"RETRY COMPLETE")
    print(f"Success: {success_count}")
    print(f"Failed: {failed_count}")
    print("=" * 60)

if __name__ == "__main__":
    retry_unavailable_calls()