from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .callkaro_models import CallKaroAgent

@login_required
def agent_management(request):
    """Agent management dashboard"""
    agents = CallKaroAgent.objects.all().order_by('-created_at')
    return render(request, 'leads/agent_management.html', {
        'agents': agents
    })

@login_required
@require_http_methods(["POST"])
def add_agent(request):
    """Add new CallKaro agent"""
    try:
        agent = CallKaroAgent.objects.create(
            name=request.POST.get('name'),
            agent_id=request.POST.get('agent_id'),
            agent_type=request.POST.get('agent_type', 'general'),
            project_name=request.POST.get('project_name', ''),
            description=request.POST.get('description', ''),
            is_active=True
        )
        return redirect('agent_management')
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_http_methods(["POST"])
def toggle_agent(request, agent_id):
    """Toggle agent active status"""
    try:
        agent = CallKaroAgent.objects.get(id=agent_id)
        agent.is_active = not agent.is_active
        agent.save()
        return JsonResponse({
            'success': True,
            'is_active': agent.is_active
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_http_methods(["POST"])
def delete_agent(request, agent_id):
    """Delete agent"""
    try:
        agent = CallKaroAgent.objects.get(id=agent_id)
        agent.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
