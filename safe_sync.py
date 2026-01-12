from fix_database_lock import safe_db_operation, fix_database_lock

def safe_sync_calls():
    """Safely sync calls with database lock handling"""
    def sync_operation():
        # Your existing sync logic here
        # This is just a wrapper to prevent locks
        pass
    
    try:
        # Fix any existing locks first
        fix_database_lock()
        
        # Run sync with retry logic
        return safe_db_operation(sync_operation)
        
    except Exception as e:
        print(f"Sync failed: {e}")
        return False

if __name__ == "__main__":
    safe_sync_calls()