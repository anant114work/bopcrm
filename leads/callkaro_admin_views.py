from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .callkaro_models import CallKaroAgent, CallKaroConfig

def callkaro_agents_admin(request):
    """Admin page to manage CallKaro agents"""
    agents = CallKaroAgent.objects.all().order_by('-created_at')
    config = CallKaroConfig.objects.filter(is_active=True).first()
    
    return render(request, 'leads/callkaro_agents_admin.html', {
        'agents': agents,
        'config': config
    })

@csrf_exempt
def add_callkaro_agent(request):
    """Add a new CallKaro agent"""
    if request.method == 'POST':
        agent_id = request.POST.get('agent_id', '').strip()
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        
        if not agent_id or not name:
            messages.error(request, 'Agent ID and Name are required')
            return redirect('callkaro_agents_admin')
        
        if CallKaroAgent.objects.filter(agent_id=agent_id).exists():
            messages.error(request, f'Agent with ID "{agent_id}" already exists')
            return redirect('callkaro_agents_admin')
        
        CallKaroAgent.objects.create(
            agent_id=agent_id,
            name=name,
            description=description,
            is_active=True
        )
        
        messages.success(request, f'Agent "{name}" added successfully')
        return redirect('callkaro_agents_admin')
    
    return redirect('callkaro_agents_admin')

@csrf_exempt
def save_callkaro_config(request):
    """Save CallKaro API configuration"""
    if request.method == 'POST':
        api_key = request.POST.get('api_key', '').strip()
        default_agent_id = request.POST.get('default_agent_id', '').strip()
        
        if not api_key:
            messages.error(request, 'API Key is required')
            return redirect('callkaro_agents_admin')
        
        # Deactivate existing configs
        CallKaroConfig.objects.update(is_active=False)
        
        # Create new config
        CallKaroConfig.objects.create(
            api_key=api_key,
            default_agent_id=default_agent_id,
            is_active=True
        )
        
        messages.success(request, 'CallKaro configuration saved successfully')
        return redirect('callkaro_agents_admin')
    
    return redirect('callkaro_agents_admin')

@csrf_exempt
def delete_callkaro_agent(request, agent_id):
    """Delete a CallKaro agent"""
    if request.method == 'POST':
        try:
            agent = CallKaroAgent.objects.get(id=agent_id)
            agent_name = agent.name
            agent.delete()
            messages.success(request, f'Agent "{agent_name}" deleted successfully')
        except CallKaroAgent.DoesNotExist:
            messages.error(request, 'Agent not found')
    
    return redirect('callkaro_agents_admin')