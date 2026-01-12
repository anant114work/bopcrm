from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from leads.models import Lead
from .models import TataCall
from .api_client import TataAPIClient

@csrf_exempt
@require_http_methods(["POST"])
def sync_calls_from_tata(request):
    client = TataAPIClient()
    call_data = client.sync_call_records()
    
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
        'message': f'Synced {synced_count} calls from Tata',
        'total_calls': TataCall.objects.count()
    })