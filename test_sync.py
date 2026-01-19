#!/usr/bin/env python
"""
Simple test script to check if the sync endpoint is working
"""
import requests
import json

def test_sync_endpoint():
    url = "http://localhost:8000/sync-gaur-acp/"
    
    try:
        response = requests.post(url, 
                               headers={'Content-Type': 'application/json'},
                               timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
            print(f"Message: {data.get('message')}")
            print(f"Forms found: {data.get('gaur_forms_found', [])}")
            print(f"Total synced: {data.get('total_synced', 0)}")
        
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to Django server. Make sure it's running on localhost:8000")
    except requests.exceptions.Timeout:
        print("ERROR: Request timed out")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_sync_endpoint()