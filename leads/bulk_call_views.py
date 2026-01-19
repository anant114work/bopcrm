from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import Lead, TeamMember, ScheduledCall, CallLog
# from .bulk_calling import bulk_calling_service  # Not needed anymore
import json
import requests

def bulk_call_panel(request):
    """Bulk calling dashboard"""
    # Filter leads based on team member
    team_member_id = request.session.get('team_member_id')
    
    if team_member_id:
        # Team member sees only their assigned leads
        from .models import TeamMember
        try:
            team_member = TeamMember.objects.get(id=team_member_id)
            # Filter leads assigned to this team member through LeadAssignment
            leads = Lead.objects.filter(
                assignment__assigned_to=team_member,
                phone_number__isnull=False
            ).exclude(phone_number='').order_by('-created_time')[:50]
        except TeamMember.DoesNotExist:
            leads = Lead.objects.none()
    else:
        # Admin sees all leads
        from .utils import get_user_leads
        leads = get_user_leads(request).filter(phone_number__isnull=False).exclude(phone_number='').order_by('-created_time')[:50]
    
    return render(request, 'leads/bulk_call_panel.html', {
        'leads': leads,
        'agent_numbers': ['918062451617', '918062451618', '918062451619']
    })

@csrf_exempt
def start_bulk_calling(request):
    """Start bulk calling for selected leads"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'})
    
    try:
        data = json.loads(request.body)
        lead_ids = data.get('lead_ids', [])
        agent_number = data.get('agent_number')
        
        if not lead_ids:
            return JsonResponse({'error': 'No leads selected'})
        
        print(f"[BULK CALL API] Starting bulk call for {len(lead_ids)} leads")
        
        # Check if this is a single call (for individual Call Now buttons)
        if len(lead_ids) == 1:
            # Handle single call - make it immediately
            lead = Lead.objects.get(id=lead_ids[0])
            try:
                url = "https://api.acefone.in/v1/click_to_call_support"
                headers = {"accept": "application/json", "content-type": "application/json"}
                payload = {
                    "customer_number": lead.phone_number, 
                    "api_key": "2449a616-b256-448e-8dd7-3bdf21696f67", 
                    "async": 1
                }
                
                response = requests.post(url, json=payload, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    return JsonResponse({
                        'success': True,
                        'single_call': True,
                        'message': f'Call initiated to {lead.full_name}'
                    })
                else:
                    return JsonResponse({'error': f'Call failed with status {response.status_code}'})
                    
            except Exception as e:
                return JsonResponse({'error': f'Call failed: {str(e)}'})
        
        # Handle bulk calls with 2-minute intervals
        leads = Lead.objects.filter(id__in=lead_ids)
        
        if not leads:
            return JsonResponse({'error': 'No valid leads found'})
        
        # Make first call immediately
        first_lead = leads.first()
        try:
            url = "https://api.acefone.in/v1/click_to_call_support"
            headers = {"accept": "application/json", "content-type": "application/json"}
            payload = {
                "customer_number": first_lead.phone_number, 
                "api_key": "2449a616-b256-448e-8dd7-3bdf21696f67", 
                "async": 1
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                print(f"[BULK CALL] First call initiated: {first_lead.full_name} - {first_lead.phone_number}")
                
                return JsonResponse({
                    'success': True,
                    'bulk_started': True,
                    'current_lead': {
                        'id': first_lead.id,
                        'name': first_lead.full_name,
                        'phone': first_lead.phone_number
                    },
                    'remaining_leads': len(lead_ids) - 1,
                    'total_leads': len(lead_ids),
                    'message': f'Bulk calling started! First call to {first_lead.full_name}. Next call in 2 minutes.'
                })
            else:
                return JsonResponse({'error': f'First call failed with status {response.status_code}'})
                
        except Exception as e:
            return JsonResponse({'error': f'First call failed: {str(e)}'})
        
    except Exception as e:
        return JsonResponse({'error': str(e)})

@csrf_exempt
def handle_scheduled_call(request):
    """Handle the scheduled call that interrupted bulk calling"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'})
    
    try:
        data = json.loads(request.body)
        scheduled_call = data.get('scheduled_call')
        
        success, result = bulk_calling_service.handle_scheduled_call(scheduled_call)
        
        return JsonResponse({
            'success': success,
            'message': 'Scheduled call initiated' if success else f'Failed: {result}'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)})

@csrf_exempt
def resume_bulk_calling(request):
    """Resume bulk calling after handling scheduled call"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'})
    
    try:
        data = json.loads(request.body)
        lead_ids = data.get('lead_ids', [])
        start_index = data.get('start_index', 0)
        agent_number = data.get('agent_number')
        
        result = bulk_calling_service.resume_bulk_calling(lead_ids, start_index, agent_number)
        
        return JsonResponse({
            'success': True,
            'result': result,
            'message': 'Bulk calling resumed'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)})

@csrf_exempt
def schedule_callback(request):
    """Schedule a callback for a lead"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'})
    
    try:
        data = json.loads(request.body)
        lead_id = data.get('lead_id')
        schedule_datetime = data.get('schedule_datetime')
        
        lead = Lead.objects.get(id=lead_id)
        team_member_id = request.session.get('team_member_id')
        team_member = TeamMember.objects.get(id=team_member_id)
        
        from datetime import datetime
        from django.utils import timezone
        dt = datetime.fromisoformat(schedule_datetime)
        dt = timezone.make_aware(dt)
        
        # Store scheduled call in database
        from .models import ScheduledCall
        scheduled_call = ScheduledCall.objects.create(
            lead=lead,
            team_member=team_member,
            scheduled_datetime=dt,
            phone_number=lead.phone_number,
            status='pending'
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Callback scheduled for {lead.full_name} at {schedule_datetime}'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)})

@csrf_exempt
def test_acefone_api(request):
    """Test Acefone API with exact same parameters as bulk calling"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'})
    
    try:
        data = json.loads(request.body)
        test_phone = data.get('phone_number', '9999929832')
        
        # Use exact same logic as bulk calling
        import requests
        
        # Format phone number exactly like bulk calling does
        dest = test_phone.strip()
        if len(dest) == 10:
            dest = "91" + dest
        
        url = "https://api.acefone.in/v1/click_to_call"
        
        payload = {
            "agent_number": "918062451619",
            "destination_number": dest,
            "caller_id": "918062451620",
            "async": "1",
            "call_timeout": 120
        }
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Bearer 2449a616-b256-448e-8dd7-3bdf21696f67"  # Click-to-Call Support API Token
        }
        
        print(f"[API TEST] Testing Acefone API")
        print(f"[API TEST] URL: {url}")
        print(f"[API TEST] Payload: {payload}")
        print(f"[API TEST] Headers: {headers}")
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        print(f"[API TEST] Response Status: {response.status_code}")
        print(f"[API TEST] Response Body: {response.text}")
        
        return JsonResponse({
            'success': response.status_code == 200,
            'status_code': response.status_code,
            'response_body': response.text,
            'payload_sent': payload,
            'headers_sent': headers
        })
        
    except Exception as e:
        print(f"[API TEST ERROR] {str(e)}")
        return JsonResponse({'error': str(e)})

@csrf_exempt
def continue_bulk_calling(request):
    """Continue bulk calling with next lead after 3-minute interval"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'})
    
    try:
        data = json.loads(request.body)
        lead_ids = data.get('lead_ids', [])
        current_index = data.get('current_index', 0)
        
        if current_index >= len(lead_ids):
            return JsonResponse({
                'success': True,
                'completed': True,
                'message': 'All calls completed!'
            })
        
        # Get next lead
        next_lead_id = lead_ids[current_index]
        next_lead = Lead.objects.get(id=next_lead_id)
        
        # Make call
        url = "https://api.acefone.in/v1/click_to_call_support"
        headers = {"accept": "application/json", "content-type": "application/json"}
        payload = {
            "customer_number": next_lead.phone_number, 
            "api_key": "2449a616-b256-448e-8dd7-3bdf21696f67", 
            "async": 1
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            remaining = len(lead_ids) - current_index - 1
            return JsonResponse({
                'success': True,
                'current_lead': {
                    'id': next_lead.id,
                    'name': next_lead.full_name,
                    'phone': next_lead.phone_number
                },
                'current_index': current_index + 1,
                'remaining_leads': remaining,
                'completed': remaining == 0,
                'message': f'Called {next_lead.full_name}. {remaining} leads remaining.'
            })
        else:
            return JsonResponse({'error': f'Call failed with status {response.status_code}'})
            
    except Exception as e:
        return JsonResponse({'error': str(e)})

@csrf_exempt
def check_scheduled_calls(request):
    """Check for scheduled calls that are due now"""
    from django.utils import timezone
    from datetime import timedelta
    
    try:
        # Get calls scheduled for now (within 1 minute window)
        now = timezone.now()
        window_start = now - timedelta(minutes=1)
        window_end = now + timedelta(minutes=1)
        
        from .models import ScheduledCall
        due_calls = ScheduledCall.objects.filter(
            scheduled_datetime__range=(window_start, window_end),
            status='pending'
        )
        
        executed_calls = []
        pending_calls = []
        
        for call in due_calls:
            # Check if there's active bulk calling for this team member
            if is_bulk_calling_active(call.team_member):
                # Don't execute, add to pending list for user confirmation
                pending_calls.append({
                    'id': call.id,
                    'name': call.lead.full_name,
                    'phone': call.phone_number,
                    'team_member_id': call.team_member.id,
                    'scheduled_time': call.scheduled_datetime.strftime('%H:%M')
                })
            else:
                # Execute the call normally
                success = execute_scheduled_call(call)
                if success:
                    call.status = 'completed'
                    call.executed_at = now
                    executed_calls.append({
                        'name': call.lead.full_name,
                        'phone': call.phone_number,
                        'id': call.id
                    })
                else:
                    call.status = 'failed'
                call.save()
        
        return JsonResponse({
            'scheduled_calls': executed_calls,
            'pending_calls': pending_calls
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)})

def execute_scheduled_call(scheduled_call):
    """Execute a scheduled call via API"""
    try:
        url = "https://api.acefone.in/v1/click_to_call_support"
        headers = {"accept": "application/json", "content-type": "application/json"}
        payload = {
            "customer_number": scheduled_call.phone_number, 
            "api_key": "2449a616-b256-448e-8dd7-3bdf21696f67", 
            "async": 1
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        # Log the call
        from .models import CallLog
        CallLog.objects.create(
            lead=scheduled_call.lead,
            team_member=scheduled_call.team_member,
            phone_number=scheduled_call.phone_number,
            call_type='scheduled',
            status='initiated' if response.status_code == 200 else 'failed'
        )
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"[SCHEDULED CALL ERROR] {str(e)}")
        return False
def is_bulk_calling_active(team_member):
    """Check if team member has active bulk calling session"""
    from django.core.cache import cache
    cache_key = f'bulk_calling_{team_member.id}'
    return cache.get(cache_key, False)

@csrf_exempt
def handle_scheduled_interrupt(request):
    """Handle scheduled call that interrupted bulk calling"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'})
    
    try:
        data = json.loads(request.body)
        call_id = data.get('call_id')
        action = data.get('action')  # 'execute' or 'skip'
        
        from .models import ScheduledCall
        scheduled_call = ScheduledCall.objects.get(id=call_id)
        
        if action == 'execute':
            # Execute the scheduled call
            success = execute_scheduled_call(scheduled_call)
            if success:
                scheduled_call.status = 'completed'
                scheduled_call.executed_at = timezone.now()
                message = f'Scheduled call executed for {scheduled_call.lead.full_name}'
            else:
                scheduled_call.status = 'failed'
                message = f'Scheduled call failed for {scheduled_call.lead.full_name}'
            scheduled_call.save()
            
            return JsonResponse({
                'success': True,
                'action': 'executed',
                'message': message
            })
        else:
            # Skip the call - reschedule for later
            from datetime import timedelta
            scheduled_call.scheduled_datetime = timezone.now() + timedelta(minutes=15)
            scheduled_call.save()
            
            return JsonResponse({
                'success': True,
                'action': 'skipped',
                'message': f'Scheduled call postponed by 15 minutes for {scheduled_call.lead.full_name}'
            })
        
    except ScheduledCall.DoesNotExist:
        return JsonResponse({'error': 'Scheduled call not found'})
    except Exception as e:
        return JsonResponse({'error': str(e)})
@csrf_exempt
def set_bulk_calling_state(request):
    """Set bulk calling active state for team member"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'})
    
    try:
        data = json.loads(request.body)
        is_active = data.get('is_active', False)
        
        team_member_id = request.session.get('team_member_id')
        if team_member_id:
            from django.core.cache import cache
            cache_key = f'bulk_calling_{team_member_id}'
            if is_active:
                cache.set(cache_key, True, 3600)  # 1 hour timeout
            else:
                cache.delete(cache_key)
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'error': str(e)})