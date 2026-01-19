from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Avg, Q
from datetime import datetime, timedelta
from .models import TataCall
from leads.models import Lead

@require_http_methods(["GET"])
def analytics_filtered_api(request):
    agent_filter = request.GET.get('agent', '')
    project_filter = request.GET.get('project', '')
    days = int(request.GET.get('days', 7))
    
    # Date filter
    start_date = datetime.now() - timedelta(days=days)
    calls = TataCall.objects.filter(start_stamp__gte=start_date)
    
    # Agent filter
    if agent_filter:
        calls = calls.filter(agent_name=agent_filter)
    
    # Project filter (via lead)
    if project_filter:
        calls = calls.filter(lead__form_name=project_filter)
    
    # Stats
    total_calls = calls.count()
    answered_calls = calls.filter(status='answered').count()
    missed_calls = calls.filter(status='missed').count()
    avg_duration = calls.aggregate(avg=Avg('duration'))['avg'] or 0
    
    # Agent data - properly grouped
    agent_data = {}
    agent_stats = calls.exclude(agent_name__isnull=True).exclude(agent_name='').values('agent_name').annotate(count=Count('id')).order_by('-count')[:10]
    for stat in agent_stats:
        agent_name = stat['agent_name'].strip() if stat['agent_name'] else 'Unknown'
        if agent_name in agent_data:
            agent_data[agent_name] += stat['count']
        else:
            agent_data[agent_name] = stat['count']
    
    # Get all agents and projects for filters (clean duplicates)
    all_agents = list(TataCall.objects.exclude(agent_name__isnull=True).exclude(agent_name='').values_list('agent_name', flat=True).distinct().order_by('agent_name'))
    all_projects = list(Lead.objects.exclude(form_name__isnull=True).exclude(form_name='').values_list('form_name', flat=True).distinct().order_by('form_name'))
    
    return JsonResponse({
        'total': total_calls,
        'answered': answered_calls,
        'missed': missed_calls,
        'avgDuration': int(avg_duration),
        'agentData': agent_data,
        'agents': all_agents,
        'projects': all_projects
    })