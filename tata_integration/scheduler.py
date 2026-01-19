import threading
import time
from django.conf import settings
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)

class AutoSyncScheduler:
    def __init__(self):
        self.running = False
        self.thread = None
        
    def start(self):
        if not settings.AUTO_SYNC_ENABLED:
            logger.info("Auto sync is disabled")
            return
            
        if self.running:
            logger.info("Auto sync already running")
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        logger.info(f"Auto sync started with {settings.SYNC_INTERVAL_MINUTES} minute intervals")
        
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        logger.info("Auto sync stopped")
        
    def _run_scheduler(self):
        while self.running:
            try:
                logger.info("Running auto sync...")
                call_command('auto_sync')
                logger.info("Auto sync completed")
            except Exception as e:
                logger.error(f"Auto sync error: {str(e)}")
                
            # Wait for the specified interval
            time.sleep(settings.SYNC_INTERVAL_MINUTES * 60)

# Global scheduler instance
scheduler = AutoSyncScheduler()