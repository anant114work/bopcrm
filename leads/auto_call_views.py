from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import AutoCallConfig, AutoCallLog
from .models import TeamMember
import json

def auto_call_config(request):
    """Auto call configuration page"""
    configs = AutoCallConfig.objects.all()
    team_members = TeamMember.objects.filter(is_active=True)
    recent_logs = AutoCallLog.objects.all()[:20]
    
    return render(request, 'leads/auto_call_config.html', {
        'configs': configs,
        'team_members': team_members,
        'recent_logs': recent_logs
    })

@csrf_exempt
def save_auto_call_config(request):
    """Save auto call configuration"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'})
    
    try:
        data = json.loads(request.body)
        project_name = data.get('project_name', '').strip()
        agent_id = data.get('agent_id')
        
        if not project_name or not agent_id:
            return JsonResponse({'error': 'Project name and agent required'})
        
        agent = TeamMember.objects.get(id=agent_id)
        
        config, created = AutoCallConfig.objects.update_or_create(
            project_name=project_name,
            defaults={
                'mapped_agent': agent,
                'is_active': True
            }
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Auto call configured for {project_name} -> {agent.name}'
        })
        
    except TeamMember.DoesNotExist:
        return JsonResponse({'error': 'Agent not found'})
    except Exception as e:
        return JsonResponse({'error': str(e)})

@csrf_exempt
def test_auto_call(request):
    """Test auto call system"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'})
    
    try:
        data = json.loads(request.body)
        phone = data.get('phone')
        agent_id = data.get('agent_id')
        
        if not phone or not agent_id:
            return JsonResponse({'error': 'Phone and agent required'})
        
        agent = TeamMember.objects.get(id=agent_id)
        
        # Create test call log
        AutoCallLog.objects.create(
            lead_id=1,  # Dummy lead ID
            agent=agent,
            call_id=f'TEST_{phone}',
            status='initiated'
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Test call logged for {phone} -> {agent.name}'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)})

def auto_call_logs(request):
    """Auto call logs API"""
    logs = AutoCallLog.objects.all()[:50]
    
    logs_data = []
    for log in logs:
        logs_data.append({
            'id': log.id,
            'lead_name': log.lead.full_name,
            'lead_phone': log.lead.phone_number,
            'agent_name': log.agent.name,
            'call_id': log.call_id,
            'status': log.get_status_display(),
            'initiated_at': log.initiated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'error_message': log.error_message
        })
    
    return JsonResponse({'logs': logs_data})

@csrf_exempt
def trigger_manual_auto_call(request, lead_id):
    """Manually trigger auto call for a specific lead"""
    from .models import Lead
    from .auto_call_service import trigger_auto_call_for_lead
    
    try:
        lead = Lead.objects.get(id=lead_id)
        print(f"[MANUAL AUTO CALL] Triggering call for lead: {lead.full_name} ({lead.phone_number})")
        
        success, message = trigger_auto_call_for_lead(lead)
        
        return JsonResponse({
            'success': success,
            'message': message,
            'lead_name': lead.full_name,
            'lead_phone': lead.phone_number
        })
        
    except Lead.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Lead not found'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })