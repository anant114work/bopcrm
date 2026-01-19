from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .enhanced_auto_sync import start_enhanced_sync, stop_enhanced_sync, is_sync_running
from .integration_models import MetaConfig, GoogleSheetsConfig

@csrf_exempt
def start_auto_sync(request):
    """Start enhanced automatic lead sync for Meta and Google Sheets"""
    if is_sync_running():
        return JsonResponse({'message': 'Auto sync already running'})
    
    # Check if we have any active configurations
    meta_count = MetaConfig.objects.filter(is_active=True).count()
    google_count = GoogleSheetsConfig.objects.filter(is_active=True).count()
    
    if meta_count == 0 and google_count == 0:
        return JsonResponse({
            'success': False,
            'message': 'No active Meta or Google Sheets configurations found'
        })
    
    success = start_enhanced_sync()
    
    if success:
        return JsonResponse({
            'success': True,
            'message': f'Enhanced auto sync started - monitoring {meta_count} Meta configs and {google_count} Google Sheets'
        })
    else:
        return JsonResponse({
            'success': False,
            'message': 'Failed to start auto sync'
        })

@csrf_exempt
def stop_auto_sync(request):
    """Stop automatic lead sync"""
    success = stop_enhanced_sync()
    
    return JsonResponse({
        'success': success,
        'message': 'Auto sync stopped' if success else 'Auto sync was not running'
    })

def auto_sync_status_api(request):
    """Get auto sync status with configuration details"""
    running = is_sync_running()
    meta_count = MetaConfig.objects.filter(is_active=True).count()
    google_count = GoogleSheetsConfig.objects.filter(is_active=True).count()
    
    return JsonResponse({
        'running': running,
        'message': 'Enhanced auto sync is running' if running else 'Enhanced auto sync is stopped',
        'meta_configs': meta_count,
        'google_configs': google_count,
        'total_configs': meta_count + google_count
    })