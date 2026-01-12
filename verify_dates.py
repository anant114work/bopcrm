#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import Lead

def verify_google_sheets_dates():
    """Verify that Google Sheets leads have correct dates"""
    print("Verifying Google Sheets lead dates...")
    
    # Get all Google Sheets leads
    google_leads = Lead.objects.filter(source='Google Sheets').order_by('created_time')
    
    print(f"Found {google_leads.count()} Google Sheets leads")
    print("\nFirst 10 leads with their dates:")
    print("-" * 80)
    
    for lead in google_leads[:10]:
        original_timestamp = lead.extra_fields.get('original_timestamp', 'N/A')
        print(f"{lead.full_name:<25} {lead.phone_number:<15} {lead.created_time.strftime('%d/%m/%Y %H:%M:%S'):<20} Original: {original_timestamp}")
    
    print("\nLast 10 leads with their dates:")
    print("-" * 80)
    
    for lead in google_leads.reverse()[:10]:
        original_timestamp = lead.extra_fields.get('original_timestamp', 'N/A')
        print(f"{lead.full_name:<25} {lead.phone_number:<15} {lead.created_time.strftime('%d/%m/%Y %H:%M:%S'):<20} Original: {original_timestamp}")
    
    # Check date range
    if google_leads.exists():
        earliest = google_leads.first()
        latest = google_leads.last()
        print(f"\nDate range:")
        print(f"Earliest: {earliest.created_time.strftime('%d/%m/%Y %H:%M:%S')} - {earliest.full_name}")
        print(f"Latest: {latest.created_time.strftime('%d/%m/%Y %H:%M:%S')} - {latest.full_name}")

if __name__ == "__main__":
    verify_google_sheets_dates()