#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append('d:\\AI-proto\\CRM\\drip')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import Lead
from leads.integration_models import MetaConfig, GoogleSheetsConfig
from leads.sync_log_models import SyncLog
from datetime import datetime, timedelta
from django.utils import timezone

def quick_check():
    print("=== SYNC STATUS CHECK ===")
    print(f"Time: {datetime.now()}")
    
    # Check configurations
    meta_configs = MetaConfig.objects.filter(is_active=True).count()
    google_configs = GoogleSheetsConfig.objects.filter(is_active=True).count()
    print(f"Active Configs - Meta: {meta_configs}, Google Sheets: {google_configs}")
    
    # Check recent leads
    total_leads = Lead.objects.count()
    google_leads = Lead.objects.filter(source='Google').count()
    meta_leads = Lead.objects.filter(source='Meta').count()
    print(f"Total Leads - All: {total_leads}, Google: {google_leads}, Meta: {meta_leads}")
    
    # Check recent Google leads
    recent_google = Lead.objects.filter(
        source='Google',
        created_time__gte=timezone.now() - timedelta(days=7)
    ).count()
    print(f"Google leads in last 7 days: {recent_google}")
    
    # Check sync logs
    recent_logs = SyncLog.objects.filter(
        started_at__gte=timezone.now() - timedelta(hours=24)
    ).count()
    print(f"Sync attempts in last 24 hours: {recent_logs}")
    
    # Latest sync logs
    latest_logs = SyncLog.objects.all()[:3]
    print("\nLatest sync logs:")
    for log in latest_logs:
        print(f"  {log.sync_type} - {log.config_name}: {log.status} ({log.leads_synced} leads)")

if __name__ == '__main__':
    quick_check()