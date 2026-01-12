#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append('d:\\AI-proto\\CRM\\drip')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import Lead, AutoCallConfig, AutoCallLog
from leads.auto_call_service import trigger_auto_call_for_lead
from django.utils import timezone

def test_auto_call():
    print("Testing Auto Call System...")
    
    # Check configurations
    configs = AutoCallConfig.objects.filter(is_active=True)
    print(f"Active auto call configs: {configs.count()}")
    for config in configs:
        print(f"  - {config.project_name} -> {config.mapped_agent.name}")
    
    # Create a test Chrysalis lead
    test_lead = Lead.objects.create(
        lead_id=f"TEST_CHRYSALIS_{int(timezone.now().timestamp())}",
        created_time=timezone.now(),
        full_name="Test Chrysalis Lead",
        phone_number="9999999999",
        email="test@chrysalis.com",
        form_name="Gaur Yamuna - Gaur Chrysalis - Form 1",
        city="Gurgaon",
        budget="1 Cr",
        source="Test"
    )
    
    print(f"\nCreated test lead: {test_lead.full_name}")
    print(f"Form name: {test_lead.form_name}")
    
    # Test auto call trigger
    success, message = trigger_auto_call_for_lead(test_lead)
    
    print(f"\nAuto call result:")
    print(f"Success: {success}")
    print(f"Message: {message}")
    
    # Check call logs
    recent_logs = AutoCallLog.objects.filter(lead=test_lead)
    print(f"\nCall logs for test lead: {recent_logs.count()}")
    for log in recent_logs:
        print(f"  - {log.agent.name}: {log.status} at {log.initiated_at}")
        if log.error_message:
            print(f"    Error: {log.error_message}")

if __name__ == '__main__':
    test_auto_call()