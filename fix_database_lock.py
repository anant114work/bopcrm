import sqlite3
import time
from django.db import transaction, connection

def fix_database_lock():
    """Fix database locking by closing idle connections"""
    try:
        # Close all database connections
        connection.close()
        
        # Wait a moment for locks to release
        time.sleep(0.5)
        
        # Force garbage collection of connections
        from django.db import connections
        connections.close_all()
        
        print("Database connections reset successfully")
        return True
        
    except Exception as e:
        print(f"Error fixing database lock: {e}")
        return False

def safe_db_operation(operation_func, max_retries=3):
    """Wrapper for database operations with retry logic"""
    for attempt in range(max_retries):
        try:
            with transaction.atomic():
                return operation_func()
        except Exception as e:
            if "database is locked" in str(e) and attempt < max_retries - 1:
                fix_database_lock()
                time.sleep(1)
                continue
            raise e
    
if __name__ == "__main__":
    fix_database_lock()