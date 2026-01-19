#!/usr/bin/env python3
"""
Test the refresh function directly
"""
import sys
import os
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from django.test import Client
from django.urls import reverse
import json

def test_refresh():
    client = Client()
    
    # First set a session with sheet URL
    session = client.session
    session['sheet_url'] = 'https://docs.google.com/spreadsheets/d/1tBO3sEET72uIJbdK2hixCCq4IicAv0eJxScWrnHzqMM/edit'
    session['sheet_name'] = 'Sheet1'
    session.save()
    
    print("Testing refresh with configured sheet...")
    
    # Test the refresh endpoint
    response = client.post('/refresh-google-leads/')
    
    if response.status_code == 200:
        data = json.loads(response.content)
        print(f"Response: {data}")
    else:
        print(f"Failed: {response.status_code}")
        print(response.content.decode())

if __name__ == "__main__":
    test_refresh()