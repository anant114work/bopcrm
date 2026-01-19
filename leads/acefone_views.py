import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import models
from .acefone_client import AcefoneClient
from .acefone_models import DIDNumber, ClickApiKey, CallRecord
from .models import Lead, TeamMember

@csrf_exempt
def fetch_acefone_numbers(request):
    """DID numbers not available with Click-to-Call Support API"""
    return JsonResponse({
        'success': False,
        'error': 'DID number sync not available with Click-to-Call Support API'
    })

@csrf_exempt
def initiate_click_call(request):
    """Initiate click-to-call for leads"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    try:
        # Get user's team member (skip if not authenticated)
        team_member = None
        if request.user.is_authenticated:
            team_member = TeamMember.objects.filter(user=request.user).first()
        
        if not team_member:
            # Use first available team member or create a default one
            team_member = TeamMember.objects.first()
        
        # Parse request data
        data = json.loads(request.body) if request.body else request.POST
        phone = data.get('phone', '').strip()
        lead_name = data.get('lead_name', '').strip()
        lead_id = data.get('lead_id')
        
        if not phone:
            return JsonResponse({'error': 'Phone number required'}, status=400)
        
        # Get lead if provided
        lead = None
        if lead_id:
            lead = Lead.objects.filter(id=lead_id).first()
            if lead:
                lead_name = lead.full_name
                phone = lead.phone_number
        
        # Get agent's API token or use global token
        api_key_entry = ClickApiKey.objects.filter(agent=team_member, enabled=True).first()
        if not api_key_entry:
            # Try global token
            api_key_entry = ClickApiKey.objects.filter(agent=None, enabled=True).first()
        
        if not api_key_entry:
            # Create default token with your provided token
            api_key_entry = ClickApiKey.objects.create(
                name='Default Click Token',
                api_token='2449a616-b256-448e-8dd7-3bdf21696f67',  # Click-to-Call Support API Token
                agent=None,
                enabled=True
            )
        
        # Create call log
        call_log = CallRecord.objects.create(
            agent=team_member,
            lead=lead,
            lead_name=lead_name,
            lead_number=phone,
            status='initiating'
        )
        
        # REAL Click-to-Call Support API (the one that works)
        import requests
        
        url = "https://api.acefone.in/v1/click_to_call_support"
        headers = {
            "accept": "application/json",
            "content-type": "application/json"
        }
        
        payload = {
            "customer_number": phone,
            "api_key": api_key_entry.api_token,
            "async": 1,
            "customer_ring_timeout": 30
        }
        
        try:
            print(f"🔥 CALLING: {phone}")
            print(f"📋 Payload: {payload}")
            print(f"🎯 Expected Agent: Anant Sharma (918062451617)")
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            print(f"📞 API Response: {response.status_code} - {response.text}")
            if response.status_code == 200:
                print("✅ SUCCESS: Anant's phone (918062451617) should ring NOW!")
            else:
                print("❌ FAILED: Call not initiated")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    result = {"success": True, "data": data}
                else:
                    result = {"success": False, "error": data.get('message', 'API returned success=false')}
            else:
                result = {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            print(f"Exception occurred: {e}")
            result = {"success": False, "error": f"Network error: {str(e)}"}
        
        if result.get('success'):
            call_data = result.get('data', {})
            call_log.acefone_call_id = call_data.get('call_id') or call_data.get('id')
            call_log.status = call_data.get('status', 'initiated')
            call_log.started_at = timezone.now()
            call_log.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Call initiated successfully',
                'call_id': call_log.id,
                'data': call_data
            })
        else:
            call_log.status = 'failed'
            call_log.save()
            return JsonResponse({
                'success': False,
                'error': result.get('error', 'Call failed')
            })
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
def call_status_webhook(request):
    """Handle call status updates from Acefone"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    try:
        payload = json.loads(request.body)
        call_id = payload.get('call_id')
        status = payload.get('status')
        duration = payload.get('duration')
        
        if call_id:
            call_log = CallRecord.objects.filter(acefone_call_id=call_id).first()
            if call_log:
                call_log.status = status
                if status in ['completed', 'failed', 'missed']:
                    call_log.ended_at = timezone.now()
                if duration:
                    call_log.duration = duration
                call_log.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def dialer_search(request):
    """Search leads for dialer"""
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    from .models import Lead
    leads = Lead.objects.filter(
        models.Q(full_name__icontains=query) | 
        models.Q(phone_number__icontains=query)
    )[:10]
    
    results = []
    for lead in leads:
        results.append({
            'id': lead.id,
            'name': lead.full_name,
            'phone': lead.phone_number,
            'stage': lead.stage
        })
    
    return JsonResponse({'results': results})

@csrf_exempt
def lead_queue_api(request):
    """Get lead queue for dialer"""
    filter_type = request.GET.get('filter', 'all')
    
    from .models import Lead, TeamMember
    from django.utils import timezone
    from datetime import timedelta
    
    # Get user's team member
    team_member = None
    if request.user.is_authenticated:
        team_member = TeamMember.objects.filter(user=request.user).first()
    
    # Base query
    leads = Lead.objects.all()
    
    # Filter by assignment if team member exists
    if team_member:
        leads = leads.filter(assignment__assigned_to=team_member)
    
    # Apply filters
    if filter_type == 'new':
        leads = leads.filter(stage='new')
    elif filter_type == 'interested':
        leads = leads.filter(stage='interested')
    elif filter_type == 'hot':
        leads = leads.filter(stage='hot')
    elif filter_type == 'overdue':
        yesterday = timezone.now() - timedelta(days=1)
        leads = leads.filter(assignment__sla_deadline__lt=timezone.now(), assignment__is_attended=False)
    elif filter_type == 'recent':
        leads = leads.filter(created_time__gte=timezone.now() - timedelta(hours=24))
    
    leads = leads.order_by('-created_time')[:20]
    
    results = []
    for lead in leads:
        time_ago = timezone.now() - lead.created_time
        if time_ago.days > 0:
            time_str = f"{time_ago.days}d ago"
        elif time_ago.seconds > 3600:
            time_str = f"{time_ago.seconds // 3600}h ago"
        else:
            time_str = f"{time_ago.seconds // 60}m ago"
        
        results.append({
            'id': lead.id,
            'name': lead.full_name,
            'phone': lead.phone_number,
            'stage': lead.stage,
            'time_ago': time_str
        })
    
    return JsonResponse({'leads': results})

@csrf_exempt
def call_history_api(request):
    """Get call history for dialer"""
    from django.utils import timezone
    from datetime import timedelta
    
    # Get user's team member
    team_member = None
    if request.user.is_authenticated:
        team_member = TeamMember.objects.filter(user=request.user).first()
    
    calls = CallRecord.objects.all()
    if team_member:
        calls = calls.filter(agent=team_member)
    
    calls = calls.order_by('-created_at')[:10]
    
    results = []
    for call in calls:
        time_ago = timezone.now() - call.created_at
        if time_ago.days > 0:
            time_str = f"{time_ago.days}d ago"
        elif time_ago.seconds > 3600:
            time_str = f"{time_ago.seconds // 3600}h ago"
        else:
            time_str = f"{time_ago.seconds // 60}m ago"
        
        results.append({
            'id': call.id,
            'lead_name': call.lead_name,
            'status': call.status,
            'duration': call.duration,
            'time_ago': time_str
        })
    
    return JsonResponse({'calls': results})

@csrf_exempt
def call_stats_api(request):
    """Get call statistics for dialer"""
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Count, Avg
    
    # Get user's team member
    team_member = None
    if request.user.is_authenticated:
        team_member = TeamMember.objects.filter(user=request.user).first()
    
    today = timezone.now().date()
    calls_today = CallRecord.objects.filter(created_at__date=today)
    
    if team_member:
        calls_today = calls_today.filter(agent=team_member)
    
    total_calls = calls_today.count()
    completed_calls = calls_today.filter(status='completed').count()
    missed_calls = calls_today.filter(status__in=['missed', 'failed']).count()
    
    # Calculate average duration
    avg_duration_seconds = calls_today.filter(duration__isnull=False).aggregate(
        avg=Avg('duration')
    )['avg'] or 0
    
    avg_duration_minutes = int(avg_duration_seconds // 60) if avg_duration_seconds else 0
    
    # Calculate success rate
    success_rate = int((completed_calls / total_calls * 100)) if total_calls > 0 else 0
    
    # Count unique leads contacted
    leads_contacted = calls_today.filter(lead__isnull=False).values('lead').distinct().count()
    
    return JsonResponse({
        'calls_today': total_calls,
        'completed_calls': completed_calls,
        'missed_calls': missed_calls,
        'avg_duration': f"{avg_duration_minutes}m",
        'success_rate': f"{success_rate}%",
        'leads_contacted': leads_contacted
    })