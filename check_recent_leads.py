#!/usr/bin/env python
import os
import sys
import django

sys.path.append('d:\\AI-proto\\CRM\\drip')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import Lead
from datetime import datetime, timedelta
from django.utils import timezone

# Check recent leads
print("=== RECENT LEADS ANALYSIS ===")
print(f"Current time: {timezone.now()}")

# Get leads from last 7 days
week_ago = timezone.now() - timedelta(days=7)
recent_leads = Lead.objects.filter(created_time__gte=week_ago).order_by('-created_time')

print(f"\nLeads in last 7 days: {recent_leads.count()}")

# Check daily breakdown
for i in range(7):
    day_start = timezone.now() - timedelta(days=i)
    day_end = day_start + timedelta(days=1)
    day_leads = Lead.objects.filter(created_time__gte=day_start.replace(hour=0, minute=0, second=0), 
                                   created_time__lt=day_end.replace(hour=0, minute=0, second=0))
    print(f"{day_start.strftime('%Y-%m-%d')}: {day_leads.count()} leads")

# Check most recent leads
print(f"\n=== MOST RECENT 10 LEADS ===")
latest_leads = Lead.objects.all().order_by('-created_time')[:10]
for lead in latest_leads:
    source = "Google" if lead.lead_id.startswith('GF_') or lead.lead_id.startswith('GS_') else "Meta"
    print(f"{lead.created_time.strftime('%Y-%m-%d %H:%M')} - {lead.full_name} ({source})")

# Check if sync is working
print(f"\n=== SYNC STATUS ===")
print(f"Total leads: {Lead.objects.count()}")
print(f"Meta leads: {Lead.objects.exclude(lead_id__startswith='GF_').exclude(lead_id__startswith='GS_').count()}")
print(f"Google leads: {Lead.objects.filter(lead_id__startswith='GF_').count() + Lead.objects.filter(lead_id__startswith='GS_').count()}")