from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Avg
from .models import TataCall
from .api_client import TataAPIClient
from django.utils.dateparse import parse_datetime
from django.utils import timezone

@require_http_methods(["GET"])
def calls_analytics_api(request):
    calls = TataCall.objects.all()
    
    # Basic stats
    total_calls = calls.count()
    answered_calls = calls.filter(status='answered').count()
    missed_calls = calls.filter(status='missed').count()
    avg_duration = calls.aggregate(avg=Avg('duration'))['avg'] or 0
    
    # Status distribution
    status_data = {
        'answered': answered_calls,
        'missed': missed_calls
    }
    
    # Agent distribution
    agent_data = {}
    agent_stats = calls.values('agent_name').annotate(count=Count('id')).order_by('-count')[:10]
    for stat in agent_stats:
        agent_name = stat['agent_name'] or 'Unknown'
        agent_data[agent_name] = stat['count']
    
    # Recent calls
    recent_calls = calls.order_by('-created_at')[:50]
    calls_data = [{
        'customer_number': call.customer_number,
        'agent_name': call.agent_name,
        'status': call.status,
        'duration': call.duration,
        'start_time': call.start_stamp.strftime('%m/%d %H:%M')
    } for call in recent_calls]
    
    return JsonResponse({
        'total': total_calls,
        'answered': answered_calls,
        'missed': missed_calls,
        'avgDuration': int(avg_duration),
        'statusData': status_data,
        'agentData': agent_data,
        'calls': calls_data
    })

@csrf_exempt
@require_http_methods(["POST"])
def sync_all_calls(request):
    from leads.models import Lead
    
    client = TataAPIClient()
    # Get more calls - last 7 days
    from datetime import datetime, timedelta
    to_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
    
    call_data = client.get_call_records(from_date, to_date, 500)
    
    if not call_data or 'results' not in call_data:
        return JsonResponse({'success': False, 'error': 'No call data received'})
    
    synced_count = 0
    for call in call_data['results']:
        try:
            customer_number = call.get('client_number', '').replace('+91', '').replace('+', '')
            lead = None
            if customer_number:
                lead = Lead.objects.filter(phone_number__icontains=customer_number).first()
            
            call_obj, created = TataCall.objects.get_or_create(
                call_id=call['call_id'],
                defaults={
                    'uuid': call.get('uuid', ''),
                    'lead': lead,
                    'customer_number': call.get('client_number', ''),
                    'agent_number': call.get('agent_number', ''),
                    'agent_name': call.get('agent_name', ''),
                    'direction': call.get('direction', 'inbound'),
                    'status': call.get('status', 'completed'),
                    'start_stamp': timezone.make_aware(parse_datetime(call['date'] + ' ' + call['time'])) if parse_datetime(call['date'] + ' ' + call['time']) else timezone.now(),
                    'end_stamp': timezone.make_aware(parse_datetime(call.get('end_stamp', call['date'] + ' ' + call['time']))) if call.get('end_stamp') and parse_datetime(call.get('end_stamp')) else None,
                    'duration': call.get('call_duration', 0),
                    'recording_url': call.get('recording_url', '')
                }
            )
            if created:
                synced_count += 1
        except Exception as e:
            continue
    
    return JsonResponse({
        'success': True,
        'message': f'Synced {synced_count} calls from last 7 days',
        'total_calls': TataCall.objects.count()
    })