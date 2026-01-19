#!/usr/bin/env python3
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from django.db import transaction, connection

def fix_sync_lock():
    """Fix database locking during sync operations"""
    try:
        # Close all connections
        connection.close()
        
        # Add transaction timeout settings
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA busy_timeout = 30000")  # 30 second timeout
            cursor.execute("PRAGMA journal_mode = WAL")     # Write-Ahead Logging
        
        print("Database lock fix applied")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    fix_sync_lock()