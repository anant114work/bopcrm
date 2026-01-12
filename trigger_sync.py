#!/usr/bin/env python
import requests

def trigger_google_sheets_sync():
    """Trigger the Google Sheets sync via webhook"""
    
    # Replace with your actual Google Apps Script web app URL
    GOOGLE_SCRIPT_URL = 'https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec'
    
    try:
        response = requests.post(
            GOOGLE_SCRIPT_URL,
            json={'action': 'sync_to_crm'},
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"Sync Response: {response.text}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print("You need to:")
        print("1. Deploy your Google Apps Script as a web app")
        print("2. Replace YOUR_SCRIPT_ID with actual script ID")
        print("3. Or run manualSyncToCRM() directly in Google Apps Script")

if __name__ == "__main__":
    trigger_google_sheets_sync()