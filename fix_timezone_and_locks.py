import os
import django
from django.utils import timezone
from django.db import transaction, connection
from datetime import datetime
import time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drip.settings')
django.setup()

def make_aware_datetime(dt_string):
    """Convert string datetime to timezone-aware datetime"""
    if isinstance(dt_string, str):
        try:
            dt = datetime.strptime(dt_string, '%Y-%m-%d %H:%M:%S')
            return timezone.make_aware(dt)
        except:
            return None
    return dt_string

def safe_db_save(model_instance, max_retries=3):
    """Save with database lock retry logic"""
    for attempt in range(max_retries):
        try:
            with transaction.atomic():
                model_instance.save()
                return True
        except Exception as e:
            if "database is locked" in str(e) and attempt < max_retries - 1:
                connection.close()
                time.sleep(0.5)
                continue
            raise e
    return False

def fix_call_timestamps():
    """Fix timezone issues in existing call records"""
    from tata_integration.models import TataCall
    
    calls = TataCall.objects.filter(start_stamp__isnull=False)
    for call in calls:
        if call.start_stamp and not timezone.is_aware(call.start_stamp):
            call.start_stamp = timezone.make_aware(call.start_stamp)
        if call.end_stamp and not timezone.is_aware(call.end_stamp):
            call.end_stamp = timezone.make_aware(call.end_stamp)
        safe_db_save(call)

if __name__ == "__main__":
    fix_call_timestamps()
    print("Fixed timezone issues")