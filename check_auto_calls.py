#!/usr/bin/env python3
"""
Check if auto calls were placed on new leads
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import Lead
from leads.callkaro_models import CallKaroCallLog
from datetime import datetime, timedelta
from django.utils import timezone

def check_auto_calls():
    """Check if auto calls were placed"""
    print("CHECKING AUTO CALLS ON NEW LEADS")
    print("=" * 50)
    
    # Get today's new AU leads
    today = timezone.now().date()
    new_leads = Lead.objects.filter(
        created_time__date=today,
        form_name__icontains='AU'
    ).order_by('-created_time')
    
    print(f"New AU leads today: {new_leads.count()}")
    
    for lead in new_leads:
        print(f"\nLead: {lead.full_name}")
        print(f"Phone: {lead.phone_number}")
        print(f"Form: {lead.form_name}")
        print(f"Created: {lead.created_time}")
        
        # Check if call was made
        call_logs = CallKaroCallLog.objects.filter(
            phone_number=lead.phone_number
        )
        
        if call_logs.exists():
            for call in call_logs:
                print(f"  CALL MADE: {call.status} at {call.created_at}")
                print(f"  Call ID: {call.call_id}")
        else:
            print(f"  NO CALL MADE")
    
    # Check total calls made today
    today_calls = CallKaroCallLog.objects.filter(
        created_at__date=today
    )
    
    print(f"\nTotal calls made today: {today_calls.count()}")
    
    if today_calls.exists():
        print("Recent calls:")
        for call in today_calls.order_by('-created_at')[:5]:
            print(f"  {call.phone_number} - {call.status} - {call.created_at}")

if __name__ == "__main__":
    check_auto_calls()
    print("\nCHECK COMPLETE!")