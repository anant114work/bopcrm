#!/usr/bin/env python
"""
Enhanced Meta Sync Startup Script
Automatically starts the high-volume Meta sync service for 2000+ forms
"""
import os
import sys
import django
import time
from datetime import datetime

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.enhanced_meta_sync import meta_sync

def main():
    """Start the enhanced Meta sync service"""
    print("=" * 60)
    print("Enhanced Meta Sync Service")
    print("Optimized for 2000+ forms with minute-by-minute syncing")
    print("=" * 60)
    
    try:
        # Check configuration
        from django.conf import settings
        
        if not hasattr(settings, 'META_ACCESS_TOKEN') or not settings.META_ACCESS_TOKEN:
            print("❌ ERROR: META_ACCESS_TOKEN not configured in settings")
            return
            
        if not hasattr(settings, 'META_PAGE_ID') or not settings.META_PAGE_ID:
            print("❌ ERROR: META_PAGE_ID not configured in settings")
            return
        
        print(f"✓ Meta Access Token: {'*' * 20}{settings.META_ACCESS_TOKEN[-10:]}")
        print(f"✓ Meta Page ID: {settings.META_PAGE_ID}")
        print()
        
        # Start the sync service
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting enhanced Meta sync...")
        result = meta_sync.start_auto_sync()
        
        if result['status'] == 'started':
            print(f"✓ {result['message']}")
            print()
            print("Sync Features:")
            print("• Processes 2000+ forms efficiently")
            print("• Syncs every minute automatically")
            print("• Batch processing to avoid rate limits")
            print("• Real-time logging with success counts")
            print("• Automatic error recovery")
            print()
            print("Press Ctrl+C to stop the sync service")
            print("=" * 60)
            
            # Keep the script running
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Stopping sync service...")
                meta_sync.stop_auto_sync()
                print("✓ Sync service stopped successfully")
                
        elif result['status'] == 'already_running':
            print("⚠️  Sync service is already running")
            print("Use the dashboard to monitor: /leads/enhanced-sync/dashboard/")
            
        else:
            print(f"❌ Failed to start sync: {result}")
            
    except Exception as e:
        print(f"❌ Error starting sync service: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()