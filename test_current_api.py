#!/usr/bin/env python3
"""
Test current API with gauraspireleisure2 template
"""
import requests
import json

# AI Sensy Configuration
AISENSY_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY4ZGVhNzVlYTM3MDcyNTJiYzJhZWY1NyIsIm5hbWUiOiJBQkMgRGlnaXRhbCBJbmMiLCJhcHBOYW1lIjoiQWlTZW5zeSIsImNsaWVudElkIjoiNjhkZWE3NWVhMzcwNzI1MmJjMmFlZjUyIiwiYWN0aXZlUGxhbiI6IkZSRUVfRk9SRVZFUiIsImlhdCI6MTc1OTQyMjMwMn0.GzXAy0qINll2QxsM9Q73B8SHBPeHMXiXZ1ypm8ScNbE"
AISENSY_API_URL = "https://backend.aisensy.com/campaign/t1/api/v2"

def test_gauraspireleisure2():
    """Test gauraspireleisure2 with correct parameters"""
    
    payload = {
        "apiKey": AISENSY_API_KEY,
        "campaignName": "gauraspireleisure2",
        "destination": "918882443789",
        "userName": "Ritesh Kothiyal",
        "templateParams": ["Ritesh Kothiyal"],  # This should be the correct format
        "source": "CRM_Test",
        "buttons": [],
        "carouselCards": [],
        "location": {},
        "attributes": {},
        "paramsFallbackValue": {"FirstName": "Ritesh Kothiyal"},
        "media": {}
    }
    
    print("Testing gauraspireleisure2 with correct parameters:")
    print(json.dumps(payload, indent=2))
    
    try:
        response = requests.post(
            AISENSY_API_URL,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            print("SUCCESS: gauraspireleisure2 is working!")
            return True
        else:
            print(f"FAILED: {response.text}")
            return False
            
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    test_gauraspireleisure2()