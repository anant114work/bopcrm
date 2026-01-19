"""
Enhanced sync control views for managing high-volume Meta form syncing
"""
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import timedelta
from .enhanced_meta_sync import start_enhanced_sync, stop_enhanced_sync, get_sync_status, manual_sync_now
from .sync_log_models import SyncLog
from .models import Lead
from django.db import models
import json

@csrf_exempt
@require_http_methods(["POST"])
def start_auto_sync(request):
    """Start the enhanced auto sync service"""
    try:
        result = start_enhanced_sync()
        return JsonResponse({
            'success': True,
            'message': result.get('message', 'Auto sync started'),
            'status': result.get('status')
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@csrf_exempt
@require_http_methods(["POST"])
def stop_auto_sync(request):
    """Stop the enhanced auto sync service"""
    try:
        result = stop_enhanced_sync()
        return JsonResponse({
            'success': True,
            'message': 'Auto sync stopped',
            'status': result.get('status')
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@require_http_methods(["GET"])
def sync_status(request):
    """Get current sync status and statistics"""
    try:
        status = get_sync_status()
        
        # Get recent sync logs
        recent_logs = SyncLog.objects.filter(
            sync_type='meta_auto'
        ).order_by('-sync_time')[:10]
        
        # Calculate today's stats
        today = timezone.now().date()
        today_leads = Lead.objects.filter(created_time__date=today).count()
        
        # Get last 24 hours sync performance
        last_24h = timezone.now() - timedelta(hours=24)
        recent_syncs = SyncLog.objects.filter(
            sync_type='meta_auto',
            sync_time__gte=last_24h
        )
        
        total_synced_24h = sum(log.leads_synced for log in recent_syncs)
        avg_forms_processed = sum(log.forms_processed for log in recent_syncs) / max(len(recent_syncs), 1)
        
        return JsonResponse({
            'success': True,
            'status': {
                'running': status['running'],
                'last_sync': status['last_sync'],
                'total_forms': status['total_forms'],
                'today_leads': today_leads,
                'last_24h_synced': total_synced_24h,
                'avg_forms_processed': round(avg_forms_processed, 1),
                'recent_logs': [
                    {
                        'sync_time': log.sync_time.strftime('%H:%M:%S'),
                        'leads_synced': log.leads_synced,
                        'forms_processed': log.forms_processed,
                        'success': log.success
                    } for log in recent_logs
                ]
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@csrf_exempt
@require_http_methods(["POST"])
def manual_sync(request):
    """Trigger manual sync of all forms"""
    try:
        result = manual_sync_now()
        
        return JsonResponse({
            'success': result['success'],
            'message': f"Manual sync completed. Synced {result['synced_leads']} leads from {result['forms_processed']} forms",
            'synced_leads': result['synced_leads'],
            'forms_processed': result['forms_processed'],
            'total_forms': result.get('total_forms', 0)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

def sync_dashboard(request):
    """Render the sync control dashboard"""
    try:
        # Get current status
        status = get_sync_status()
        
        # Get today's stats
        today = timezone.now().date()
        today_leads = Lead.objects.filter(created_time__date=today).count()
        
        # Get recent sync performance
        recent_logs = SyncLog.objects.filter(
            sync_type='meta_auto'
        ).order_by('-sync_time')[:20]
        
        # Calculate hourly breakdown for today
        hourly_stats = []
        for hour in range(24):
            hour_start = timezone.now().replace(hour=hour, minute=0, second=0, microsecond=0)
            hour_end = hour_start + timedelta(hours=1)
            
            hour_leads = Lead.objects.filter(
                created_time__gte=hour_start,
                created_time__lt=hour_end
            ).count()
            
            hourly_stats.append({
                'hour': f"{hour:02d}:00",
                'leads': hour_leads
            })
        
        context = {
            'sync_running': status['running'],
            'last_sync': status['last_sync'],
            'total_forms': status['total_forms'],
            'today_leads': today_leads,
            'recent_logs': recent_logs,
            'hourly_stats': hourly_stats
        }
        
        return render(request, 'leads/sync_dashboard.html', context)
        
    except Exception as e:
        return render(request, 'leads/sync_dashboard.html', {
            'error': str(e),
            'sync_running': False,
            'today_leads': 0,
            'recent_logs': [],
            'hourly_stats': []
        })

@require_http_methods(["GET"])
def sync_analytics(request):
    """Get detailed sync analytics"""
    try:
        # Get date range from request
        days = int(request.GET.get('days', 7))
        start_date = timezone.now() - timedelta(days=days)
        
        # Daily breakdown
        daily_stats = []
        for i in range(days):
            date = (timezone.now() - timedelta(days=i)).date()
            
            day_leads = Lead.objects.filter(created_time__date=date).count()
            day_syncs = SyncLog.objects.filter(
                sync_type='meta_auto',
                sync_time__date=date
            )
            
            total_synced = sum(log.leads_synced for log in day_syncs)
            sync_count = day_syncs.count()
            
            daily_stats.append({
                'date': date.strftime('%Y-%m-%d'),
                'leads': day_leads,
                'synced': total_synced,
                'sync_runs': sync_count
            })
        
        # Form performance (top forms by lead count)
        top_forms = Lead.objects.filter(
            created_time__gte=start_date
        ).values('form_name').annotate(
            lead_count=models.Count('id')
        ).order_by('-lead_count')[:20]
        
        return JsonResponse({
            'success': True,
            'analytics': {
                'daily_stats': daily_stats,
                'top_forms': list(top_forms),
                'period_days': days
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })