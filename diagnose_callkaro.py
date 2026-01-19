#!/usr/bin/env python3
"""
CallKaro AI Diagnostic Script
Checks API configuration and tests call functionality
"""

import requests
import json
from datetime import datetime
import os
import sys

# Add Django setup
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')

import django
django.setup()

from leads.models import Lead

def test_callkaro_api():
    """Test CallKaro AI API with current configuration"""
    
    # API Configuration (same as in views.py)
    api_key = "bc422db39aa327234a911dd901accfcfa975623ee84c65c83aae9c4f844ffdb8"
    
    # Test agents
    agents = {
        "gaur_yamuna": "6923ff797a5d5a94d5a5dfcf",
        "au_realty_1": "692d5b6ad10e948b7bbfc2db", 
        "au_realty_2": "69294d3d2cc1373b1f3a3972"
    }
    
    print(f"\n{'='*60}")
    print(f"CALLKARO AI DIAGNOSTIC - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    print(f"API Key: {api_key[:20]}...")
    print(f"Current Time: {datetime.now().strftime('%H:%M:%S')} IST")
    print(f"Current Date: {datetime.now().strftime('%A, %B %d, %Y')}")
    
    # Test each agent
    for agent_name, agent_id in agents.items():
        print(f"\nTesting Agent: {agent_name} ({agent_id})")
        
        # Test payload (using a test number)
        payload = {
            "to_number": "+919999999999",  # Test number
            "agent_id": agent_id,
            "metadata": {
                "name": "Test User",
                "test": True,
                "timestamp": datetime.now().isoformat()
            },
            "priority": 1
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
            
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   SUCCESS: Call ID = {result.get('call_id', 'N/A')}")
            else:
                print(f"   FAILED: {response.text}")
                
        except Exception as e:
            print(f"   ERROR: {str(e)}")
    
    # Test with recent lead data
    print(f"\nTesting with Recent Lead Data:")
    recent_leads = Lead.objects.filter(phone_number__isnull=False).exclude(phone_number='').order_by('-created_time')[:3]
    
    for lead in recent_leads:
        print(f"\nLead: {lead.full_name} ({lead.phone_number})")
        print(f"   Form: {lead.form_name}")
        print(f"   City: {lead.city}")
        print(f"   Budget: {lead.budget}")
        
        # Determine agent based on form (same logic as views.py)
        form_name = (lead.form_name or '').lower()
        if 'gaur' in form_name or 'yamuna' in form_name:
            agent_id = agents['gaur_yamuna']
            agent_name = 'gaur_yamuna'
        elif 'au' in form_name or 'realty' in form_name:
            agent_id = agents['au_realty_1'] if lead.id % 2 == 0 else agents['au_realty_2']
            agent_name = 'au_realty_1' if lead.id % 2 == 0 else 'au_realty_2'
        else:
            agent_id = agents['au_realty_1']
            agent_name = 'au_realty_1'
        
        print(f"   Selected Agent: {agent_name} ({agent_id})")
        
        # Format phone number
        phone = lead.phone_number
        if not phone.startswith('+'):
            phone = f"+91{phone}" if len(phone) == 10 else f"+{phone}"
        
        print(f"   Formatted Phone: {phone}")
    
    print(f"\n{'='*60}")
    print(f"DIAGNOSTIC COMPLETE")
    print(f"{'='*60}")
    
    # Check for potential issues
    print(f"\nPOTENTIAL ISSUES TO CHECK:")
    print(f"1. Time Restrictions: CallKaro might have calling hour limits")
    print(f"2. Geographic Restrictions: Check if calls to specific regions are blocked")
    print(f"3. Phone Number Format: Ensure +91 prefix is correct")
    print(f"4. Agent Configuration: Agents might be configured with specific schedules")
    print(f"5. Account Limits: Check CallKaro account balance/limits")
    print(f"6. Volume Limits: High call volume might trigger rate limiting")
    
    print(f"\nRECOMMENDATIONS:")
    print(f"1. Check CallKaro dashboard for call logs and status")
    print(f"2. Verify agent configurations in CallKaro portal")
    print(f"3. Test with a known working phone number")
    print(f"4. Check if there are any account notifications from CallKaro")
    print(f"5. Contact CallKaro support if API returns success but calls don't connect")

if __name__ == "__main__":
    test_callkaro_api()