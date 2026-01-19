#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append('d:\\AI-proto\\CRM\\drip')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.integration_models import MetaConfig, GoogleSheetsConfig
from leads.enhanced_auto_sync import EnhancedAutoSyncService

def test_enhanced_sync():
    print("Testing Enhanced Auto Sync Service")
    print("=" * 50)
    
    # Check configurations
    meta_configs = MetaConfig.objects.filter(is_active=True)
    google_configs = GoogleSheetsConfig.objects.filter(is_active=True)
    
    print(f"Active Meta Configurations: {meta_configs.count()}")
    for config in meta_configs:
        print(f"  - {config.name} (Page: {config.page_id})")
    
    print(f"Active Google Sheets Configurations: {google_configs.count()}")
    for config in google_configs:
        print(f"  - {config.name} ({config.sheet_url})")
    
    if meta_configs.count() == 0 and google_configs.count() == 0:
        print("\nNo active configurations found!")
        print("Please add configurations through the integration panel.")
        return
    
    # Test sync
    print("\nTesting manual sync...")
    service = EnhancedAutoSyncService()
    
    try:
        # Test Meta sync
        if meta_configs.count() > 0:
            print("Syncing Meta leads...")
            meta_synced = service.sync_meta_leads()
            print(f"Meta leads synced: {meta_synced}")
        
        # Test Google Sheets sync
        if google_configs.count() > 0:
            print("Syncing Google Sheets leads...")
            google_synced = service.sync_google_sheets_leads()
            print(f"Google Sheets leads synced: {google_synced}")
        
        print("\nSync test completed successfully!")
        
    except Exception as e:
        print(f"Sync test failed: {e}")

if __name__ == '__main__':
    test_enhanced_sync()