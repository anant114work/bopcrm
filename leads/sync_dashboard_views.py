from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .enhanced_auto_sync import is_sync_running
from .integration_models import MetaConfig, GoogleSheetsConfig
from .sync_log_models import SyncLog
from django.utils import timezone
from datetime import timedelta
import requests

def sync_dashboard(request):
    """Sync status dashboard"""
    # Get sync status
    is_running = is_sync_running()
    
    # Get configurations
    meta_configs = MetaConfig.objects.filter(is_active=True)
    google_configs = GoogleSheetsConfig.objects.filter(is_active=True)
    
    # Get recent sync logs
    recent_logs = SyncLog.objects.all()[:20]
    
    # Get sync stats for last 24 hours
    yesterday = timezone.now() - timedelta(hours=24)
    recent_syncs = SyncLog.objects.filter(started_at__gte=yesterday)
    
    stats = {
        'total_syncs': recent_syncs.count(),
        'successful_syncs': recent_syncs.filter(status='success').count(),
        'failed_syncs': recent_syncs.filter(status='error').count(),
        'total_leads_synced': sum(log.leads_synced for log in recent_syncs),
    }
    
    return render(request, 'leads/sync_dashboard.html', {
        'is_running': is_running,
        'meta_configs': meta_configs,
        'google_configs': google_configs,
        'recent_logs': recent_logs,
        'stats': stats
    })

@csrf_exempt
def manual_sync_all(request):
    """Manually trigger sync for all configurations with detailed logging"""
    from .enhanced_auto_sync import EnhancedAutoSyncService
    from .integration_models import MetaConfig, GoogleSheetsConfig
    
    # Immediate response when button is clicked
    print(f"\n🔄 [BUTTON CLICKED] Manual sync button pressed at {timezone.now()}")
    print(f"🔄 [BUTTON CLICKED] Request method: {request.method}")
    print(f"🔄 [BUTTON CLICKED] User agent: {request.META.get('HTTP_USER_AGENT', 'Unknown')}")
    print(f"🔄 [BUTTON CLICKED] Starting manual sync process...\n")
    
    try:
        print(f"[MANUAL SYNC] ========== STARTING MANUAL SYNC ===========")
        print(f"[MANUAL SYNC] Timestamp: {timezone.now()}")
        
        service = EnhancedAutoSyncService()
        
        # Check configurations
        meta_configs = MetaConfig.objects.filter(is_active=True)
        google_configs = GoogleSheetsConfig.objects.filter(is_active=True)
        
        print(f"[MANUAL SYNC] Configuration Check:")
        print(f"[MANUAL SYNC]   - Meta configs found: {meta_configs.count()}")
        for config in meta_configs:
            print(f"[MANUAL SYNC]     * {config.name} (Page ID: {config.page_id})")
        print(f"[MANUAL SYNC]   - Google configs found: {google_configs.count()}")
        for config in google_configs:
            print(f"[MANUAL SYNC]     * {config.name} ({config.sheet_url[:50]}...)")
        
        if meta_configs.count() == 0 and google_configs.count() == 0:
            print(f"[MANUAL SYNC] ERROR: No active configurations found!")
            return JsonResponse({
                'success': False,
                'error': 'No active Meta or Google configurations found'
            })
        
        # Sync Meta leads
        print(f"[MANUAL SYNC] ========== META SYNC STARTING ===========")
        meta_synced = service.sync_meta_leads()
        print(f"[MANUAL SYNC] Meta sync result: {meta_synced} new leads")
        
        # Sync Google Sheets leads  
        print(f"[MANUAL SYNC] ========== GOOGLE SYNC STARTING ===========")
        google_synced = service.sync_google_sheets_leads()
        print(f"[MANUAL SYNC] Google sync result: {google_synced} new leads")
        
        total_synced = meta_synced + google_synced
        print(f"[MANUAL SYNC] ========== SYNC COMPLETED ===========")
        print(f"[MANUAL SYNC] SUMMARY:")
        print(f"[MANUAL SYNC]   - Meta leads: {meta_synced}")
        print(f"[MANUAL SYNC]   - Google leads: {google_synced}")
        print(f"[MANUAL SYNC]   - Total new leads: {total_synced}")
        print(f"[MANUAL SYNC] =========================================")
        
        return JsonResponse({
            'success': True,
            'message': f'Manual sync completed: {meta_synced} Meta leads, {google_synced} Google leads',
            'meta_synced': meta_synced,
            'google_synced': google_synced,
            'total_synced': total_synced,
            'debug_info': {
                'meta_configs': meta_configs.count(),
                'google_configs': google_configs.count(),
                'timestamp': timezone.now().isoformat()
            }
        })
        
    except Exception as e:
        error_msg = str(e)
        print(f"[MANUAL SYNC ERROR] {error_msg}")
        return JsonResponse({
            'success': False,
            'error': error_msg,
            'debug_info': {
                'timestamp': timezone.now().isoformat()
            }
        })

def sync_logs_api(request):
    """API to get sync logs"""
    logs = SyncLog.objects.all()[:50]
    
    logs_data = []
    for log in logs:
        logs_data.append({
            'id': log.id,
            'sync_type': log.get_sync_type_display(),
            'config_name': log.config_name,
            'status': log.get_status_display(),
            'leads_synced': log.leads_synced,
            'error_message': log.error_message,
            'started_at': log.started_at.strftime('%Y-%m-%d %H:%M:%S'),
            'completed_at': log.completed_at.strftime('%Y-%m-%d %H:%M:%S') if log.completed_at else None
        })
    
    return JsonResponse({'logs': logs_data})

@csrf_exempt
def test_sync_button(request):
    """Simple test endpoint to verify button clicks are working"""
    print(f"\n🎆 [TEST BUTTON] Button test clicked at {timezone.now()}")
    print(f"🎆 [TEST BUTTON] This proves the button is working!")
    print(f"🎆 [TEST BUTTON] Request received successfully\n")
    
    return JsonResponse({
        'success': True,
        'message': 'Button test successful! Check console for logs.',
        'timestamp': timezone.now().isoformat()
    })

def force_sync_now(request):
    """Force an immediate sync cycle to show console output"""
    from .enhanced_auto_sync import EnhancedAutoSyncService, is_sync_running
    
    print(f"\n⚡ [FORCE SYNC] Immediate sync requested at {timezone.now()}")
    print(f"⚡ [FORCE SYNC] Auto-sync running: {is_sync_running()}")
    
    try:
        service = EnhancedAutoSyncService()
        
        print(f"⚡ [FORCE SYNC] Starting immediate sync cycle...")
        
        # Force Meta sync
        meta_synced = service.sync_meta_leads()
        
        # Force Google sync  
        google_synced = service.sync_google_sheets_leads()
        
        total = meta_synced + google_synced
        
        print(f"⚡ [FORCE SYNC] Immediate sync completed: {total} total leads")
        print(f"⚡ [FORCE SYNC] ================================\n")
        
        return JsonResponse({
            'success': True,
            'message': f'Force sync completed: {meta_synced} Meta, {google_synced} Google leads',
            'meta_synced': meta_synced,
            'google_synced': google_synced,
            'total_synced': total
        })
        
    except Exception as e:
        print(f"⚡ [FORCE SYNC ERROR] {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@csrf_exempt
def check_missing_leads(request):
    """Check for missing leads from Facebook campaigns"""
    from .enhanced_auto_sync import EnhancedAutoSyncService
    from .integration_models import MetaConfig
    from leads.models import Lead
    from datetime import datetime, timedelta
    
    print(f"\n🔍 [LEAD CHECK] Checking for missing Facebook leads...")
    
    try:
        service = EnhancedAutoSyncService()
        total_facebook_leads = 0
        total_crm_leads = Lead.objects.filter(source='Meta').count()
        
        print(f"🔍 [LEAD CHECK] Current CRM Meta leads: {total_crm_leads}")
        
        for meta_config in MetaConfig.objects.filter(is_active=True):
            print(f"🔍 [LEAD CHECK] Checking config: {meta_config.name}")
            
            # Get forms
            forms_url = f'https://graph.facebook.com/v23.0/{meta_config.page_id}/leadgen_forms'
            forms_response = requests.get(forms_url, params={'access_token': meta_config.access_token})
            
            if forms_response.status_code == 200:
                forms_data = forms_response.json()
                
                for form in forms_data.get('data', []):
                    form_id = form['id']
                    form_name = form.get('name', 'Unknown Form')
                    
                    # Get ALL leads from this form (not just recent)
                    leads_url = f'https://graph.facebook.com/v23.0/{form_id}/leads'
                    leads_response = requests.get(leads_url, params={
                        'access_token': meta_config.access_token,
                        'fields': 'id,created_time,field_data',
                        'limit': 500  # Get more leads
                    })
                    
                    if leads_response.status_code == 200:
                        leads_data = leads_response.json()
                        facebook_count = len(leads_data.get('data', []))
                        total_facebook_leads += facebook_count
                        
                        # Check how many exist in CRM
                        facebook_lead_ids = [lead['id'] for lead in leads_data.get('data', [])]
                        existing_in_crm = Lead.objects.filter(lead_id__in=facebook_lead_ids).count()
                        missing = facebook_count - existing_in_crm
                        
                        print(f"🔍 [LEAD CHECK] Form: {form_name}")
                        print(f"🔍 [LEAD CHECK]   - Facebook leads: {facebook_count}")
                        print(f"🔍 [LEAD CHECK]   - In CRM: {existing_in_crm}")
                        print(f"🔍 [LEAD CHECK]   - Missing: {missing}")
        
        print(f"🔍 [LEAD CHECK] SUMMARY:")
        print(f"🔍 [LEAD CHECK]   - Total Facebook leads: {total_facebook_leads}")
        print(f"🔍 [LEAD CHECK]   - Total CRM leads: {total_crm_leads}")
        print(f"🔍 [LEAD CHECK]   - Missing leads: {total_facebook_leads - total_crm_leads}")
        
        return JsonResponse({
            'success': True,
            'facebook_leads': total_facebook_leads,
            'crm_leads': total_crm_leads,
            'missing_leads': total_facebook_leads - total_crm_leads,
            'message': f'Found {total_facebook_leads - total_crm_leads} missing leads'
        })
        
    except Exception as e:
        print(f"🔍 [LEAD CHECK ERROR] {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })