#!/usr/bin/env python3
"""
Call New AU Leads Immediately
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.auto_call_new_leads import auto_call_service

def call_new_au_leads():
    """Call all new AU leads from today"""
    print("CALLING NEW AU LEADS")
    print("=" * 30)
    
    # Call leads from last 24 hours
    results = auto_call_service.call_au_forms_leads(since_minutes=1440)
    
    print(f"Total leads found: {results['total_leads']}")
    print(f"Successful calls: {results['successful_calls']}")
    print(f"Failed calls: {results['failed_calls']}")
    
    print("\nCall Results:")
    for log in results['call_logs']:
        status = "SUCCESS" if log['success'] else "FAILED"
        print(f"  {log['lead_name']} ({log['phone']}) - {status}")
        if log.get('call_id'):
            print(f"    Call ID: {log['call_id']}")
        if log.get('error'):
            print(f"    Error: {log['error']}")

if __name__ == "__main__":
    call_new_au_leads()
    print("\nCALLING COMPLETE!")