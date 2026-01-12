#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append('d:\\AI-proto\\CRM\\drip')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.enhanced_auto_sync import EnhancedAutoSyncService
from leads.models import Lead

def manual_sync():
    print("Starting manual sync...")
    
    # Count leads before sync
    before_count = Lead.objects.count()
    google_before = Lead.objects.filter(source='Google').count()
    meta_before = Lead.objects.filter(source='Meta').count()
    
    print(f"Before sync - Total: {before_count}, Google: {google_before}, Meta: {meta_before}")
    
    # Run sync
    service = EnhancedAutoSyncService()
    
    try:
        meta_synced = service.sync_meta_leads()
        google_synced = service.sync_google_sheets_leads()
        
        # Count leads after sync
        after_count = Lead.objects.count()
        google_after = Lead.objects.filter(source='Google').count()
        meta_after = Lead.objects.filter(source='Meta').count()
        
        print(f"After sync - Total: {after_count}, Google: {google_after}, Meta: {meta_after}")
        print(f"Synced - Meta: {meta_synced}, Google: {google_synced}")
        print(f"New leads added: {after_count - before_count}")
        
    except Exception as e:
        print(f"Sync failed: {e}")

if __name__ == '__main__':
    manual_sync()