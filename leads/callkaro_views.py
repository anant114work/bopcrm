import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib import messages
from .models import Lead, TeamMember
from .callkaro_models import CallKaroConfig, CallKaroAgent, CallKaroCampaign, CallKaroCallLog
from .callkaro_client import CallKaroClient
from .team_auth import team_login_required

@team_login_required
def callkaro_config_page(request):
    """Call Karo AI configuration page"""
    config = CallKaroConfig.objects.first()
    agents = CallKaroAgent.objects.filter(is_active=True)
    
    context = {
        'config': config,
        'agents': agents,
        'team_members': TeamMember.objects.filter(is_active=True)
    }
    return render(request, 'leads/callkaro_config.html', context)

@csrf_exempt
def save_callkaro_config(request):
    """Save Call Karo AI configuration"""
    if request.method == 'POST':
        data = json.loads(request.body)
        api_key = data.get('api_key')
        default_agent_id = data.get('default_agent_id')
        
        if not api_key or not default_agent_id:
            return JsonResponse({'error': 'API key and default agent ID required'}, status=400)
        
        config, created = CallKaroConfig.objects.get_or_create(defaults={
            'api_key': api_key,
            'default_agent_id': default_agent_id,
            'is_active': True
        })
        
        if not created:
            config.api_key = api_key
            config.default_agent_id = default_agent_id
            config.is_active = True
            config.save()
        
        return JsonResponse({'success': True, 'message': 'Configuration saved successfully'})
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def add_callkaro_agent(request):
    """Add new Call Karo AI agent"""
    if request.method == 'POST':
        data = json.loads(request.body)
        agent_id = data.get('agent_id')
        name = data.get('name')
        description = data.get('description', '')
        team_member_id = data.get('team_member_id')
        
        if not agent_id or not name:
            return JsonResponse({'error': 'Agent ID and name required'}, status=400)
        
        # Check if agent already exists
        if CallKaroAgent.objects.filter(agent_id=agent_id).exists():
            return JsonResponse({'error': 'Agent with this ID already exists'}, status=400)
        
        agent = CallKaroAgent.objects.create(
            agent_id=agent_id,
            name=name,
            description=description,
            is_active=True
        )
        
        if team_member_id:
            try:
                team_member = TeamMember.objects.get(id=team_member_id)
                agent.assigned_team_member = team_member
                agent.save()
            except TeamMember.DoesNotExist:
                pass
        
        return JsonResponse({'success': True, 'message': 'Agent added successfully'})
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def initiate_callkaro_call(request):
    """Initiate call using Call Karo AI"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            lead_id = data.get('lead_id')
            phone_number = data.get('phone_number')
            agent_id = data.get('agent_id')
            
            # Get lead if provided
            lead = None
            if lead_id:
                lead = get_object_or_404(Lead, id=lead_id)
                phone_number = lead.phone_number
            
            if not phone_number:
                return JsonResponse({'error': 'Phone number required'}, status=400)
            
            # Get Call Karo configuration
            config = CallKaroConfig.objects.filter(is_active=True).first()
            if not config:
                return JsonResponse({'error': 'Call Karo not configured'}, status=400)
            
            # Get agent
            if not agent_id:
                agent_id = config.default_agent_id
            
            try:
                agent = CallKaroAgent.objects.get(agent_id=agent_id, is_active=True)
            except CallKaroAgent.DoesNotExist:
                return JsonResponse({'error': 'Invalid agent ID'}, status=400)
            
            # Get team member
            team_member_id = request.session.get('team_member_id')
            if not team_member_id:
                return JsonResponse({'error': 'Team member not found'}, status=400)
            
            team_member = get_object_or_404(TeamMember, id=team_member_id)
            
            # Prepare metadata
            metadata = {}
            if lead:
                metadata = {
                    'name': lead.full_name,
                    'email': lead.email,
                    'city': lead.city,
                    'form_name': lead.form_name,
                    'stage': lead.stage,
                    'lead_id': str(lead.id)
                }
            
            # Initialize Call Karo client
            client = CallKaroClient(api_key=config.api_key)
            
            # Make the call
            result = client.initiate_outbound_call(
                to_number=phone_number,
                agent_id=agent_id,
                metadata=metadata,
                priority=data.get('priority', 0)
            )
            
            if result['success']:
                call_data = result['data']
                
                # Create call log
                call_log = CallKaroCallLog.objects.create(
                    call_id=call_data.get('call_id', f"ck_{timezone.now().timestamp()}"),
                    lead=lead,
                    phone_number=phone_number,
                    agent=agent,
                    initiated_by=team_member,
                    status='initiated',
                    metadata=metadata,
                    priority=data.get('priority', 0)
                )
                
                return JsonResponse({
                    'success': True,
                    'message': 'Call initiated successfully with AI agent',
                    'call_id': call_log.call_id,
                    'data': call_data
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': result['error']
                }, status=400)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def create_callkaro_campaign(request):
    """Create new Call Karo AI campaign"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            agent_id = data.get('agent_id')
            
            if not name:
                return JsonResponse({'error': 'Campaign name required'}, status=400)
            
            # Get Call Karo configuration
            config = CallKaroConfig.objects.filter(is_active=True).first()
            if not config:
                return JsonResponse({'error': 'Call Karo not configured'}, status=400)
            
            # Get agent
            if not agent_id:
                agent_id = config.default_agent_id
            
            try:
                agent = CallKaroAgent.objects.get(agent_id=agent_id, is_active=True)
            except CallKaroAgent.DoesNotExist:
                return JsonResponse({'error': 'Invalid agent ID'}, status=400)
            
            # Get team member
            team_member_id = request.session.get('team_member_id')
            if not team_member_id:
                return JsonResponse({'error': 'Team member not found'}, status=400)
            
            team_member = get_object_or_404(TeamMember, id=team_member_id)
            
            # Initialize Call Karo client
            client = CallKaroClient(api_key=config.api_key)
            
            # Create campaign
            result = client.create_campaign(name=name, agent_id=agent_id)
            
            if result['success']:
                campaign_data = result['data']
                batch_id = campaign_data.get('batch_id')
                
                # Save campaign locally
                campaign = CallKaroCampaign.objects.create(
                    name=name,
                    batch_id=batch_id,
                    agent=agent,
                    created_by=team_member,
                    status='active'
                )
                
                return JsonResponse({
                    'success': True,
                    'message': 'Campaign created successfully',
                    'batch_id': batch_id,
                    'campaign_id': campaign.id
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': result['error']
                }, status=400)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def schedule_campaign_call(request):
    """Schedule call as part of campaign"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            batch_id = data.get('batch_id')
            lead_id = data.get('lead_id')
            phone_number = data.get('phone_number')
            agent_id = data.get('agent_id')
            
            if not batch_id:
                return JsonResponse({'error': 'Campaign batch ID required'}, status=400)
            
            # Get campaign
            try:
                campaign = CallKaroCampaign.objects.get(batch_id=batch_id)
            except CallKaroCampaign.DoesNotExist:
                return JsonResponse({'error': 'Campaign not found'}, status=400)
            
            # Get lead if provided
            lead = None
            if lead_id:
                lead = get_object_or_404(Lead, id=lead_id)
                phone_number = lead.phone_number
            
            if not phone_number:
                return JsonResponse({'error': 'Phone number required'}, status=400)
            
            # Get Call Karo configuration
            config = CallKaroConfig.objects.filter(is_active=True).first()
            if not config:
                return JsonResponse({'error': 'Call Karo not configured'}, status=400)
            
            # Use campaign agent if no agent specified
            if not agent_id:
                agent_id = campaign.agent.agent_id
            
            # Get team member
            team_member_id = request.session.get('team_member_id')
            team_member = get_object_or_404(TeamMember, id=team_member_id)
            
            # Prepare metadata
            metadata = {}
            if lead:
                metadata = {
                    'name': lead.full_name,
                    'email': lead.email,
                    'city': lead.city,
                    'form_name': lead.form_name,
                    'stage': lead.stage,
                    'lead_id': str(lead.id),
                    'campaign': campaign.name
                }
            
            # Initialize Call Karo client
            client = CallKaroClient(api_key=config.api_key)
            
            # Schedule campaign call
            result = client.schedule_campaign_call(
                to_number=phone_number,
                batch_id=batch_id,
                agent_id=agent_id,
                metadata=metadata,
                **{k: v for k, v in data.items() if k in [
                    'schedule_at', 'min_trigger_time', 'max_trigger_time',
                    'carry_over', 'number_of_retries', 'gap_between_retries', 'priority'
                ]}
            )
            
            if result['success']:
                call_data = result['data']
                
                # Create call log
                call_log = CallKaroCallLog.objects.create(
                    call_id=call_data.get('call_id', f"ck_camp_{timezone.now().timestamp()}"),
                    lead=lead,
                    phone_number=phone_number,
                    agent=campaign.agent,
                    campaign=campaign,
                    initiated_by=team_member,
                    status='scheduled',
                    metadata=metadata,
                    scheduled_at=data.get('schedule_at'),
                    priority=data.get('priority', 0)
                )
                
                # Update campaign stats
                campaign.total_calls += 1
                campaign.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Call scheduled successfully in campaign',
                    'call_id': call_log.call_id,
                    'data': call_data
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': result['error']
                }, status=400)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@team_login_required
def callkaro_dashboard(request):
    """Call Karo AI dashboard"""
    # Get recent calls
    recent_calls = CallKaroCallLog.objects.select_related('lead', 'agent', 'campaign').order_by('-created_at')[:20]
    
    # Get campaigns
    campaigns = CallKaroCampaign.objects.select_related('agent', 'created_by').order_by('-created_at')[:10]
    
    # Get agents
    agents = CallKaroAgent.objects.filter(is_active=True)
    
    # Get stats
    from django.db.models import Count
    from datetime import timedelta
    
    today = timezone.now().date()
    stats = {
        'total_calls_today': CallKaroCallLog.objects.filter(created_at__date=today).count(),
        'completed_calls_today': CallKaroCallLog.objects.filter(
            created_at__date=today, 
            status='completed'
        ).count(),
        'active_campaigns': CallKaroCampaign.objects.filter(status='active').count(),
        'total_agents': agents.count()
    }
    
    context = {
        'recent_calls': recent_calls,
        'campaigns': campaigns,
        'agents': agents,
        'stats': stats
    }
    
    return render(request, 'leads/callkaro_dashboard.html', context)

@csrf_exempt
def callkaro_webhook(request):
    """Handle webhooks from Call Karo AI"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            call_id = data.get('call_id')
            status = data.get('status')
            duration = data.get('duration')
            
            if call_id:
                try:
                    call_log = CallKaroCallLog.objects.get(call_id=call_id)
                    call_log.status = status
                    
                    if status in ['completed', 'failed', 'missed']:
                        call_log.ended_at = timezone.now()
                        
                        # Update campaign stats
                        if call_log.campaign and status == 'completed':
                            call_log.campaign.completed_calls += 1
                            call_log.campaign.save()
                    
                    if duration:
                        call_log.duration = duration
                    
                    call_log.save()
                    
                except CallKaroCallLog.DoesNotExist:
                    pass
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def callkaro_agents_api(request):
    """API to get available Call Karo AI agents"""
    try:
        agents = CallKaroAgent.objects.filter(is_active=True).values(
            'agent_id', 'name', 'description'
        )
        return JsonResponse({
            'success': True,
            'agents': list(agents)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)