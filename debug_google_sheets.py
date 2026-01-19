import os
import sys
import django

# Setup Django
sys.path.append('d:\\AI-proto\\CRM\\drip')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import Lead, GoogleSheet
from django.db.models import Q

print("=== GOOGLE SHEETS DEBUG ===")

# Check Google Sheets configuration
sheets = GoogleSheet.objects.all()
print(f"\nConfigured Google Sheets: {sheets.count()}")
for sheet in sheets:
    print(f"  - {sheet.name} ({sheet.sheet_url[:50]}...)")
    print(f"    Status: {'Active' if sheet.is_active else 'Inactive'}")
    print(f"    Last Synced: {sheet.last_synced or 'Never'}")

# Check Google leads in system
google_leads = Lead.objects.filter(
    Q(lead_id__startswith='GS_') | Q(source='Google Sheets')
).order_by('-created_time')

print(f"\nGoogle Leads in CRM: {google_leads.count()}")
if google_leads.exists():
    print("Recent Google leads:")
    for lead in google_leads[:5]:
        print(f"  - {lead.full_name} ({lead.phone_number}) - {lead.created_time}")
else:
    print("  No Google leads found in CRM")

# Check all recent leads to see if any came from Google Apps Script
recent_leads = Lead.objects.all().order_by('-created_time')[:10]
print(f"\nRecent leads (any source):")
for lead in recent_leads:
    print(f"  - {lead.full_name} ({lead.phone_number}) - Source: {lead.source} - Form: {lead.form_name}")

print(f"\nWebhook URL should be:")
print(f"  http://127.0.0.1:8000/google-sheets-webhook/")

print("=== END DEBUG ===")