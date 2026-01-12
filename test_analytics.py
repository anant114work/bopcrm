#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import Lead
from django.db.models import Count, Q

print("=== ANALYTICS DATA TEST ===")

# Test basic stats
total_leads = Lead.objects.count()
meta_leads = Lead.objects.exclude(lead_id__startswith='GF_').exclude(lead_id__startswith='GS_').count()
google_leads = Lead.objects.filter(Q(lead_id__startswith='GF_') | Q(lead_id__startswith='GS_')).count()

print(f"Total Leads: {total_leads}")
print(f"Meta Leads: {meta_leads}")
print(f"Google Leads: {google_leads}")

# Test project data
project_stats = Lead.objects.values('form_name').annotate(
    count=Count('id')
).filter(count__gt=0).order_by('-count')[:5]

print("\nTop 5 Projects:")
for stat in project_stats:
    print(f"- {stat['form_name']}: {stat['count']} leads")

# Test stage data
stage_stats = Lead.objects.values('stage').annotate(
    count=Count('id')
).filter(count__gt=0).order_by('-count')

print("\nLead Stages:")
for stat in stage_stats:
    print(f"- {stat['stage']}: {stat['count']} leads")

print("\n=== TEST COMPLETE ===")