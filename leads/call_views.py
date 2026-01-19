from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Lead, TeamMember
from .acefone_models import DIDNumber, CallRecord
from .acefone_client import AcefoneClient
from .team_auth import team_login_required
import json

@team_login_required
def call_panel(request):
    """Main call panel dashboard"""
    context = {
        'did_numbers': DIDNumber.objects.filter(is_active=True),
        'team_members': TeamMember.objects.filter(is_active=True),
    }
    return render(request, 'leads/call_panel.html', context)

@csrf_exempt
def initiate_call(request):
    """Initiate click-to-call with number masking"""
    if request.method == 'POST':
        data = json.loads(request.body)
        lead_id = data.get('lead_id')
        
        lead = get_object_or_404(Lead, id=lead_id)
        client = AcefoneClient()
        
        # Get team member from session
        team_member_id = request.session.get('team_member_id')
        team_member = None
        if team_member_id:
            try:
                team_member = TeamMember.objects.get(id=team_member_id)
            except TeamMember.DoesNotExist:
                pass
        
        # Get assigned DID number or any available one
        did_number = None
        if team_member:
            did_number = DIDNumber.objects.filter(assigned_user=team_member, is_active=True).first()
        
        if not did_number:
            did_number = DIDNumber.objects.filter(is_active=True).first()
        if not did_number:
            return JsonResponse({'error': 'No DID numbers available'}, status=400)
        
        try:
            # Use direct API call since client method doesn't exist
            import requests
            url = "https://api.acefone.in/v1/click_to_call_support"
            headers = {"accept": "application/json", "content-type": "application/json"}
            payload = {"customer_number": lead.phone_number, "api_key": "2449a616-b256-448e-8dd7-3bdf21696f67", "async": 1}
            response = requests.post(url, json=payload, headers=headers)
            result = {"success": response.status_code == 200, "data": response.json() if response.content else {}}
            
            if result.get('success', True):
                return JsonResponse({'success': True, 'data': result})
            else:
                return JsonResponse({'success': False, 'error': result.get('error')}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Error: {str(e)}'}, status=500)

@team_login_required
def dialer_search(request):
    """Search leads for dialer"""
    query = request.GET.get('q', '')
    leads = Lead.objects.filter(full_name__icontains=query)[:10]
    
    results = []
    for lead in leads:
        results.append({
            'id': lead.id,
            'name': lead.full_name,
            'masked_phone': f"***-***-{lead.phone_number[-4:]}" if lead.phone_number else "No phone",
            'stage': lead.stage
        })
    
    return JsonResponse({'results': results})

@team_login_required
def active_calls_api(request):
    """Get active calls - not available with Click-to-Call Support API"""
    return JsonResponse({'calls': []})

@team_login_required
def call_recordings_api(request):
    """Get call recordings - not available with Click-to-Call Support API"""
    return JsonResponse({'recordings': []})

@csrf_exempt
def add_call_note(request):
    """Add note to call"""
    if request.method == 'POST':
        data = json.loads(request.body)
        call_id = data.get('call_id')
        note = data.get('note')
        
        team_member_id = request.session.get('team_member_id')
        if not team_member_id:
            return JsonResponse({'error': 'No team member found'}, status=400)
        
        team_member = TeamMember.objects.get(id=team_member_id)
        
        client = AcefoneClient()
        result = client.add_call_note(call_id, note, str(team_member.id))
        
        if result:
            return JsonResponse({'success': True})
        return JsonResponse({'error': 'Failed to add note'}, status=500)

@csrf_exempt
def assign_did_number(request):
    """Assign DID number to team member (admin only)"""
    if not request.session.get('is_admin'):
        return JsonResponse({'error': 'Admin access required'}, status=403)
    
    if request.method == 'POST':
        data = json.loads(request.body)
        did_id = data.get('did_id')
        user_id = data.get('user_id')
        
        try:
            did_number = DIDNumber.objects.get(id=did_id)
            if user_id:
                team_member = TeamMember.objects.get(id=user_id)
                did_number.assigned_user = team_member
            else:
                did_number.assigned_user = None
            did_number.save()
            
            return JsonResponse({'success': True})
        except (DIDNumber.DoesNotExist, TeamMember.DoesNotExist):
            return JsonResponse({'error': 'Invalid DID or user'}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def add_did_number(request):
    """Add new DID number (admin only)"""
    if not request.session.get('is_admin'):
        return JsonResponse({'error': 'Admin access required'}, status=403)
    
    if request.method == 'POST':
        data = json.loads(request.body)
        number = data.get('number')
        display_name = data.get('display_name')
        
        if not number or not display_name:
            return JsonResponse({'error': 'Number and display name required'}, status=400)
        
        try:
            did_number = DIDNumber.objects.create(
                number=number,
                display_name=display_name,
                is_active=True
            )
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def initiate_manual_call(request):
    """Initiate manual call with phone number"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    
    try:
        data = json.loads(request.body)
        to_number = data.get('phone_number') or data.get('phone')
        
        if not to_number:
            return JsonResponse({'error': 'Phone number required'}, status=400)
        
        # Get team member and assigned DID
        team_member_id = request.session.get('team_member_id')
        assigned_did = None
        
        if team_member_id:
            try:
                team_member = TeamMember.objects.get(id=team_member_id)
                assigned_did = DIDNumber.objects.filter(assigned_user=team_member, is_active=True).first()
            except TeamMember.DoesNotExist:
                pass
        
        if not assigned_did:
            assigned_did = DIDNumber.objects.filter(is_active=True).first()
        
        if not assigned_did:
            return JsonResponse({'error': 'No DID numbers available'}, status=400)
        
        client = AcefoneClient()
        # Use direct API call since client method doesn't exist
        import requests
        url = "https://api.acefone.in/v1/click_to_call_support"
        headers = {"accept": "application/json", "content-type": "application/json"}
        payload = {"customer_number": to_number, "api_key": "2449a616-b256-448e-8dd7-3bdf21696f67", "async": 1}
        response = requests.post(url, json=payload, headers=headers)
        result = {"success": response.status_code == 200, "data": response.json() if response.content else {}}
        
        if result.get('success', True):
            return JsonResponse({'success': True, 'data': result})
        else:
            return JsonResponse({'success': False, 'error': result.get('error')}, status=400)
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@team_login_required
def lead_queue_api(request):
    """Get leads for the call queue"""
    filter_type = request.GET.get('filter', 'all')
    
    leads = Lead.objects.filter(phone_number__isnull=False).exclude(phone_number='')
    
    if filter_type == 'new':
        leads = leads.filter(stage='New')
    elif filter_type == 'interested':
        leads = leads.filter(stage='Interested')
    elif filter_type == 'hot':
        leads = leads.filter(stage='Hot')
    elif filter_type == 'overdue':
        from django.utils import timezone
        from datetime import timedelta
        overdue_date = timezone.now() - timedelta(days=3)
        leads = leads.filter(created_time__lt=overdue_date)
    
    leads = leads.order_by('-created_time')[:20]
    
    results = []
    for lead in leads:
        results.append({
            'id': lead.id,
            'name': lead.full_name,
            'phone': lead.phone_number,
            'stage': lead.stage,
            'time_ago': lead.created_time.strftime('%m/%d %H:%M')
        })
    
    return JsonResponse({'leads': results})

@team_login_required
def call_stats_api(request):
    """Get call statistics for today"""
    from django.utils import timezone
    from datetime import datetime, timedelta
    
    today = timezone.now().date()
    
    # Since we're using Click-to-Call Support API, we don't have detailed call records
    # Return mock data for now
    return JsonResponse({
        'calls_today': 0,
        'avg_duration': '0m',
        'success_rate': '0%',
        'leads_contacted': 0,
        'completed_calls': 0,
        'missed_calls': 0
    })