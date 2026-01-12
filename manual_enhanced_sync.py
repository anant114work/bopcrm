#!/usr/bin/env python
"""
Manual Enhanced Meta Sync - Get leads from 16th onwards
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.enhanced_meta_sync import meta_sync
from datetime import datetime

print("Enhanced Meta Sync - Manual Trigger")
print("=" * 50)

# Test token first
status = meta_sync.get_sync_status()
print(f"Sync Status: {status}")

# Run manual sync
print("\nStarting manual sync...")
result = meta_sync.sync_all_forms()

print(f"\nSync Results:")
print(f"  Success: {result['success']}")
print(f"  Synced Leads: {result['synced_leads']}")
print(f"  Forms Processed: {result['forms_processed']}")
print(f"  Total Forms: {result.get('total_forms', 0)}")

if not result['success']:
    print(f"  Error: {result.get('error', 'Unknown error')}")

print("=" * 50)