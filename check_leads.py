import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import Lead

print("="*60)
print("CURRENT DATABASE STATUS")
print("="*60)
print(f"Total Leads: {Lead.objects.count()}")
print(f"Meta Leads: {Lead.objects.filter(source='Meta').count()}")
print(f"Google Leads: {Lead.objects.filter(source='Google Sheets').count()}")
print("="*60)

# Show recent leads
recent = Lead.objects.order_by('-created_time')[:5]
print("\nRecent 5 Leads:")
for lead in recent:
    print(f"  - {lead.full_name} | {lead.phone_number} | {lead.form_name}")

print("\n" + "="*60)
print("DATABASE CHECK COMPLETE")
print("="*60)
