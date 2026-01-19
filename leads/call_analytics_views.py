from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from datetime import date, timedelta
from django.db.models import Count, Q
from .models import CallLog, Lead
from .project_models import Project

def call_analytics_by_source(request, project_id=None):
    """Analytics view showing call statistics by lead source"""
    
    # Date filtering
    today = date.today()
    date_filter = request.GET.get('date', 'today')
    
    if date_filter == 'today':
        start_date = today
        end_date = today
    elif date_filter == 'week':
        start_date = today - timedelta(days=7)
        end_date = today
    elif date_filter == 'month':
        start_date = today - timedelta(days=30)
        end_date = today
    else:
        start_date = today
        end_date = today
    
    # Base queryset
    calls_query = CallLog.objects.filter(
        initiated_at__date__range=[start_date, end_date]
    )
    
    # Project filtering
    project = None
    if project_id:
        project = get_object_or_404(Project, id=project_id)
        # Filter calls by project leads
        project_lead_ids = project.get_leads().values_list('id', flat=True)
        calls_query = calls_query.filter(lead_id__in=project_lead_ids)
    
    # Call statistics by source
    meta_calls = calls_query.filter(lead__source='Meta')
    google_calls = calls_query.filter(lead__source='Google Sheets')
    
    # Call type breakdown
    meta_stats = {
        'total': meta_calls.count(),
        'auto_daily_all': meta_calls.filter(call_type='auto_daily_all').count(),
        'auto_daily_meta': meta_calls.filter(call_type='auto_daily_meta').count(),
        'manual': meta_calls.filter(call_type='manual').count(),
        'bulk': meta_calls.filter(call_type='bulk').count(),
    }
    
    google_stats = {
        'total': google_calls.count(),
        'auto_daily_all': google_calls.filter(call_type='auto_daily_all').count(),
        'auto_daily_google': google_calls.filter(call_type='auto_daily_google').count(),
        'manual': google_calls.filter(call_type='manual').count(),
        'bulk': google_calls.filter(call_type='bulk').count(),
    }
    
    # Daily breakdown for charts
    daily_meta = []
    daily_google = []
    
    current_date = start_date
    while current_date <= end_date:
        meta_count = meta_calls.filter(initiated_at__date=current_date).count()
        google_count = google_calls.filter(initiated_at__date=current_date).count()
        
        daily_meta.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'count': meta_count
        })
        daily_google.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'count': google_count
        })
        
        current_date += timedelta(days=1)
    
    # Recent calls by source
    recent_meta_calls = meta_calls.select_related('lead').order_by('-initiated_at')[:10]
    recent_google_calls = google_calls.select_related('lead').order_by('-initiated_at')[:10]
    
    context = {
        'project': project,
        'date_filter': date_filter,
        'start_date': start_date,
        'end_date': end_date,
        'meta_stats': meta_stats,
        'google_stats': google_stats,
        'daily_meta': daily_meta,
        'daily_google': daily_google,
        'recent_meta_calls': recent_meta_calls,
        'recent_google_calls': recent_google_calls,
        'total_calls': calls_query.count(),
    }
    
    return render(request, 'leads/call_analytics_by_source.html', context)

def call_report_api(request, project_id=None):
    """API endpoint for call statistics"""
    
    today = date.today()
    date_filter = request.GET.get('date', 'today')
    
    if date_filter == 'today':
        start_date = today
        end_date = today
    elif date_filter == 'week':
        start_date = today - timedelta(days=7)
        end_date = today
    elif date_filter == 'month':
        start_date = today - timedelta(days=30)
        end_date = today
    else:
        start_date = today
        end_date = today
    
    calls_query = CallLog.objects.filter(
        initiated_at__date__range=[start_date, end_date]
    )
    
    if project_id:
        project = get_object_or_404(Project, id=project_id)
        project_lead_ids = project.get_leads().values_list('id', flat=True)
        calls_query = calls_query.filter(lead_id__in=project_lead_ids)
    
    # Source breakdown
    source_stats = calls_query.values('lead__source').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Call type breakdown
    call_type_stats = calls_query.values('call_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    return JsonResponse({
        'source_stats': list(source_stats),
        'call_type_stats': list(call_type_stats),
        'total_calls': calls_query.count(),
        'date_range': f"{start_date} to {end_date}"
    })