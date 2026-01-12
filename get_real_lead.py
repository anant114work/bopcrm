#!/usr/bin/env python3
"""
Get a real lead ID from the database
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append('d:\\AI-proto\\CRM\\drip')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import Lead

def get_real_lead():
    try:
        # Get a lead with phone number
        lead = Lead.objects.filter(phone_number__isnull=False).exclude(phone_number='').first()
        
        if lead:
            print(f"Found lead:")
            print(f"ID: {lead.id}")
            print(f"Name: {lead.full_name}")
            print(f"Phone: {lead.phone_number}")
            print(f"Source: {lead.source}")
            return lead.id
        else:
            print("No leads with phone numbers found")
            return None
            
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    get_real_lead()