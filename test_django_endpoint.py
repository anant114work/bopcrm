#!/usr/bin/env python3
"""
Test Django endpoint directly
"""
import requests
import json

def test_django_endpoint():
    # Test the call-single-lead endpoint
    url = "http://localhost:8000/projects/20/call-single-lead/"
    
    payload = {
        "lead_id": 5711  # Real lead ID
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print("=" * 60)
    print("TESTING DJANGO CALL ENDPOINT")
    print("=" * 60)
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("=" * 60)
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            print("\nSUCCESS: Django endpoint is working!")
            return True
        else:
            print(f"\nFAILED: Django returned {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("\nERROR: Cannot connect to Django server. Is it running on localhost:8000?")
        return False
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        return False

if __name__ == "__main__":
    test_django_endpoint()