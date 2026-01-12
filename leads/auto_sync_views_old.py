import threading
import time
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .views import sync_leads
from django.test import RequestFactory

# Auto sync service
auto_sync_thread = None
auto_sync_running = False

@csrf_exempt
def start_auto_sync(request):
    """Start automatic lead sync"""
    global auto_sync_thread, auto_sync_running
    
    if auto_sync_running:
        return JsonResponse({'message': 'Auto sync already running'})
    
    def sync_loop():
        global auto_sync_running
        auto_sync_running = True
        
        while auto_sync_running:
            try:
                # Call existing sync_leads function
                factory = RequestFactory()
                sync_request = factory.post('/sync/')
                sync_leads(sync_request)
                time.sleep(300)  # 5 minutes
            except Exception as e:
                print(f'Auto sync error: {e}')
                time.sleep(60)
    
    auto_sync_thread = threading.Thread(target=sync_loop, daemon=True)
    auto_sync_thread.start()
    
    return JsonResponse({
        'success': True,
        'message': 'Auto sync started - syncing every 5 minutes'
    })

@csrf_exempt
def stop_auto_sync(request):
    """Stop automatic lead sync"""
    global auto_sync_running
    auto_sync_running = False
    
    return JsonResponse({
        'success': True,
        'message': 'Auto sync stopped'
    })

def auto_sync_status_api(request):
    """Get auto sync status"""
    return JsonResponse({
        'running': auto_sync_running,
        'message': 'Auto sync is running' if auto_sync_running else 'Auto sync is stopped'
    })