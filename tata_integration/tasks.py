from celery import shared_task
from django.core.management import call_command
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

@shared_task
def auto_sync_all():
    """Auto sync task for Tata IVR, Google, and Meta leads"""
    try:
        call_command('auto_sync')
        logger.info(f'Auto sync completed at {timezone.now()}')
        return 'Auto sync completed successfully'
    except Exception as e:
        logger.error(f'Auto sync failed: {str(e)}')
        return f'Auto sync failed: {str(e)}'

@shared_task
def sync_tata_calls():
    """Sync only Tata IVR calls"""
    from .api_client import TataAPIClient
    try:
        client = TataAPIClient()
        result = client.sync_call_records()
        logger.info(f'Tata calls sync: {result.get("message", "Completed")}')
        return result
    except Exception as e:
        logger.error(f'Tata sync failed: {str(e)}')
        return {'error': str(e)}