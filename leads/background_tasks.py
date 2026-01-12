import threading
import time
from django.utils import timezone
from .models import ScheduledMessage
from .whatsapp import send_whatsapp_message

class MessageProcessor:
    def __init__(self):
        self.running = False
        self.thread = None
        self.last_sync = 0
    
    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._process_loop, daemon=True)
            self.thread.start()
    
    def stop(self):
        self.running = False
    
    def _process_loop(self):
        while self.running:
            try:
                self._auto_sync_leads()
            except Exception as e:
                print(f"Background task error: {e}")
            time.sleep(60)  # Check every minute
    
    def _auto_sync_leads(self):
        """Auto sync leads every 5 minutes"""
        current_time = time.time()
        if current_time - self.last_sync >= 300:  # 5 minutes
            try:
                from .views import sync_leads, refresh_google_leads
                from django.http import HttpRequest
                
                # Create dummy request
                request = HttpRequest()
                request.method = 'POST'
                
                # Sync Meta leads
                sync_leads(request)
                print("Auto-synced Meta leads")
                
                # Sync Google leads
                refresh_google_leads(request)
                print("Auto-synced Google leads")
                
                self.last_sync = current_time
            except Exception as e:
                print(f"Auto sync error: {e}")
    

    


# Global processor instance
processor = MessageProcessor()