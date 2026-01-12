#!/usr/bin/env python3
"""
Test Bulk Call with Fixed Agent ID
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.bulk_call_service import initiate_callkaro_call

def test_callkaro_with_working_agent():
    """Test CallKaro with the AU Reality agent ID"""
    print("TESTING CALLKARO WITH AU REALITY AGENT ID")
    print("=" * 50)
    
    # Use the AU Reality agent ID
    au_reality_agent_id = "69294d3d2cc1373b1f3a3972"
    test_phone = "+919999999999"  # Test number
    
    print(f"Testing with:")
    print(f"  Phone: {test_phone}")
    print(f"  Agent ID: {au_reality_agent_id}")
    
    result = initiate_callkaro_call(test_phone, None, au_reality_agent_id)
    
    print(f"\nResult:")
    print(f"  Success: {result['success']}")
    if result['success']:
        print(f"  Call ID: {result.get('call_id', 'N/A')}")
        print(f"  Response: {result.get('response', {})}")
    else:
        print(f"  Error: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    test_callkaro_with_working_agent()
    print("\nTEST COMPLETE!")