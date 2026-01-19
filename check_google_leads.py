#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append('d:\\AI-proto\\CRM\\drip')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import Lead

def check_google_leads():
    print("Checking Google leads...")
    
    # Count by source
    total_leads = Lead.objects.count()
    google_leads = Lead.objects.filter(source='Google').count()
    meta_leads = Lead.objects.filter(source='Meta').count()
    
    print(f"Total leads: {total_leads}")
    print(f"Google leads: {google_leads}")
    print(f"Meta leads: {meta_leads}")
    
    # Show recent Google leads
    recent_google = Lead.objects.filter(source='Google').order_by('-created_time')[:5]
    print(f"\nRecent Google leads ({recent_google.count()}):")
    for lead in recent_google:
        print(f"- {lead.full_name} | {lead.phone_number} | {lead.source}")
    
    # Check if any leads have "Gaur Yamuna" in form name
    gaur_leads = Lead.objects.filter(form_name__icontains='Gaur Yamuna').count()
    print(f"\nLeads with 'Gaur Yamuna' in form: {gaur_leads}")

if __name__ == '__main__':
    check_google_leads()