from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
import json

from .models import Lead
from .ai_agent_models import AIAgent, AICallLog
from .form_mapping_models import FormSourceMapping
from .project_models import Project
from .auto_ai_call_service import AutoAICallService

def ai_agent_dashboard(request):
    """Dashboard for AI agent management"""
    agents = AIAgent.objects.select_related('project').all()
    mappings = FormSourceMapping.objects.select_related('project').filter(is_active=True)
    projects = Project.objects.filter(status='Active')
    
    # Recent call logs
    recent_calls = AICallLog.objects.select_related('lead', 'agent').order_by('-initiated_at')[:20]
    
    # Stats
    today = timezone.now().date()
    stats = {
        'total_agents': agents.count(),
        'active_agents': agents.filter(is_active=True).count(),
        'total_mappings': mappings.count(),
        'calls_today': AICallLog.objects.filter(initiated_at__date=today).count(),
        'calls_success': AICallLog.objects.filter(initiated_at__date=today, status='connected').count(),
    }
    
    return render(request, 'leads/ai_agent_dashboard.html', {
        'agents': agents,
        'mappings': mappings,
        'projects': projects,
        'recent_calls': recent_calls,
        'stats': stats
    })

@csrf_exempt
def create_ai_agent(request):
    """Create new AI agent"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            agent = AIAgent.objects.create(
                name=data['name'],
                agent_id=data['agent_id'],
                project_id=data['project_id'],
                is_active=data.get('is_active', True)
            )
            
            return JsonResponse({
                'success': True,
                'message': f'AI Agent {agent.name} created successfully',
                'agent_id': agent.id
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'POST required'}, status=405)

@csrf_exempt
def update_ai_agent(request, agent_id):
    """Update AI agent"""
    if request.method == 'POST':
        try:
            agent = get_object_or_404(AIAgent, id=agent_id)
            data = json.loads(request.body)
            
            agent.name = data.get('name', agent.name)
            agent.agent_id = data.get('agent_id', agent.agent_id)
            agent.project_id = data.get('project_id', agent.project_id)
            agent.is_active = data.get('is_active', agent.is_active)
            agent.save()
            
            return JsonResponse({
                'success': True,
                'message': f'AI Agent {agent.name} updated successfully'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'POST required'}, status=405)

@csrf_exempt
def delete_ai_agent(request, agent_id):
    """Delete AI agent"""
    if request.method == 'POST':
        try:
            agent = get_object_or_404(AIAgent, id=agent_id)
            agent_name = agent.name
            agent.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'AI Agent {agent_name} deleted successfully'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'POST required'}, status=405)

@csrf_exempt
def create_form_mapping(request):
    """Create form to project mapping"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            mapping = FormSourceMapping.objects.create(
                form_name=data['form_name'],
                project_id=data['project_id'],
                is_active=data.get('is_active', True)
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Form mapping created: {mapping.form_name} → {mapping.project.name}',
                'mapping_id': mapping.id
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'POST required'}, status=405)

@csrf_exempt
def delete_form_mapping(request, mapping_id):
    """Delete form mapping"""
    if request.method == 'POST':
        try:
            mapping = get_object_or_404(FormSourceMapping, id=mapping_id)
            form_name = mapping.form_name
            mapping.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Form mapping deleted: {form_name}'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'POST required'}, status=405)

@csrf_exempt
def trigger_auto_call_for_lead(request, lead_id):
    """Manually trigger auto AI call for a specific lead"""
    if request.method == 'POST':
        try:
            lead = get_object_or_404(Lead, id=lead_id)
            service = AutoAICallService()
            result = service.process_new_lead(lead)
            
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'POST required'}, status=405)

@csrf_exempt
def process_unmapped_leads(request):
    """Process all unmapped leads (leads without AI calls)"""
    if request.method == 'POST':
        try:
            # Get leads without AI call logs
            unmapped_leads = Lead.objects.exclude(
                id__in=AICallLog.objects.values_list('lead_id', flat=True)
            ).filter(
                phone_number__isnull=False
            ).exclude(
                phone_number=''
            ).order_by('-created_time')[:50]  # Process 50 at a time
            
            service = AutoAICallService()
            results = service.process_batch(unmapped_leads)
            
            return JsonResponse({
                'success': True,
                'results': results
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'POST required'}, status=405)

def call_logs_view(request):
    """View all AI call logs"""
    logs = AICallLog.objects.select_related('lead', 'agent', 'agent__project').order_by('-initiated_at')
    
    # Filters
    status_filter = request.GET.get('status')
    project_filter = request.GET.get('project')
    date_filter = request.GET.get('date')
    
    if status_filter:
        logs = logs.filter(status=status_filter)
    
    if project_filter:
        logs = logs.filter(agent__project_id=project_filter)
    
    if date_filter:
        from datetime import datetime
        date = datetime.strptime(date_filter, '%Y-%m-%d').date()
        logs = logs.filter(initiated_at__date=date)
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(logs, 50)
    page = request.GET.get('page')
    logs = paginator.get_page(page)
    
    projects = Project.objects.filter(status='Active')
    
    return render(request, 'leads/ai_call_logs.html', {
        'logs': logs,
        'projects': projects,
        'status_filter': status_filter,
        'project_filter': project_filter,
        'date_filter': date_filter
    })

def ai_call_analytics(request):
    """Analytics for AI calls"""
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    
    # Daily stats for last 7 days
    daily_stats = []
    for i in range(7):
        date = today - timedelta(days=i)
        stats = AICallLog.objects.filter(initiated_at__date=date).aggregate(
            total=Count('id'),
            connected=Count('id', filter=Q(status='connected')),
            failed=Count('id', filter=Q(status='failed'))
        )
        daily_stats.append({
            'date': date.strftime('%Y-%m-%d'),
            'total': stats['total'],
            'connected': stats['connected'],
            'failed': stats['failed']
        })
    
    # Project-wise stats
    project_stats = AICallLog.objects.filter(
        initiated_at__date__gte=week_ago
    ).values(
        'agent__project__name'
    ).annotate(
        total=Count('id'),
        connected=Count('id', filter=Q(status='connected'))
    ).order_by('-total')
    
    # Agent performance
    agent_stats = AICallLog.objects.filter(
        initiated_at__date__gte=week_ago
    ).values(
        'agent__name', 'agent__project__name'
    ).annotate(
        total=Count('id'),
        connected=Count('id', filter=Q(status='connected'))
    ).order_by('-total')
    
    return render(request, 'leads/ai_call_analytics.html', {
        'daily_stats': daily_stats,
        'project_stats': project_stats,
        'agent_stats': agent_stats
    })

@csrf_exempt
def test_form_mapping(request):
    """Test form mapping for a lead"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            form_name = data.get('form_name')
            
            if not form_name:
                return JsonResponse({'error': 'form_name required'}, status=400)
            
            # Try to find mapping
            service = AutoAICallService()
            
            # Create a temporary lead object for testing
            class TempLead:
                def __init__(self, form_name):
                    self.form_name = form_name
            
            temp_lead = TempLead(form_name)
            project = service._find_project_for_lead(temp_lead)
            
            if project:
                agent = service._get_agent_for_project(project)
                return JsonResponse({
                    'success': True,
                    'project': {
                        'id': project.id,
                        'name': project.name
                    },
                    'agent': {
                        'id': agent.id,
                        'name': agent.name,
                        'agent_id': agent.agent_id
                    } if agent else None
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'No mapping found for this form'
                })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'POST required'}, status=405)
