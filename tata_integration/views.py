from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.utils.dateparse import parse_datetime
from leads.models import Lead
from .models import TataCall, CallNote
from .api_client import TataAPIClient
import json

@method_decorator(csrf_exempt, name='dispatch')
class TataWebhookView(View):
    def get(self, request, webhook_id):
        # Handle GET webhook from Tata
        data = request.GET.dict()
        self._process_webhook_data(data, webhook_id)
        return JsonResponse({'status': 'success'})
    
    def post(self, request, webhook_id):
        # Handle POST webhook from Tata
        data = json.loads(request.body) if request.body else request.POST.dict()
        self._process_webhook_data(data, webhook_id)
        return JsonResponse({'status': 'success'})
    
    def _process_webhook_data(self, data, webhook_id):
        call_id = data.get('call_id') or data.get('$call_id')
        if not call_id:
            return
        
        # Find lead by phone number
        customer_number = data.get('customer_number') or data.get('$customer_number') or data.get('caller_id_number') or data.get('$caller_id_number')
        lead = None
        if customer_number:
            lead = Lead.objects.filter(phone_number__icontains=customer_number.replace('+91', '').replace('+', '')).first()
        
        # Create or update call record
        call_data = {
            'uuid': data.get('uuid') or data.get('$uuid', ''),
            'lead': lead,
            'customer_number': customer_number or '',
            'agent_number': data.get('answered_agent_number') or data.get('$answered_agent_number', ''),
            'agent_name': data.get('answered_agent_name') or data.get('$answered_agent_name', ''),
            'direction': data.get('direction') or data.get('$direction', 'inbound'),
            'status': data.get('call_status') or data.get('$call_status', 'received'),
            'start_stamp': parse_datetime(data.get('start_stamp') or data.get('$start_stamp')) or timezone.now(),
            'end_stamp': parse_datetime(data.get('end_stamp') or data.get('$end_stamp')),
            'duration': int(data.get('duration') or data.get('$duration', 0)),
            'recording_url': data.get('recording_url') or data.get('$recording_url', '')
        }
        
        TataCall.objects.update_or_create(call_id=call_id, defaults=call_data)

@require_http_methods(["GET"])
def get_lead_calls(request, lead_id):
    calls = TataCall.objects.filter(lead_id=lead_id).order_by('-created_at')
    data = [{
        'call_id': call.call_id,
        'agent_name': call.agent_name,
        'status': call.status,
        'duration': call.duration,
        'start_time': call.start_stamp.strftime('%Y-%m-%d %H:%M:%S'),
        'recording_url': call.recording_url
    } for call in calls]
    return JsonResponse({'calls': data})

@csrf_exempt
@require_http_methods(["POST"])
def initiate_call(request):
    data = json.loads(request.body)
    lead_id = data.get('lead_id')
    agent_number = data.get('agent_number')
    
    lead = Lead.objects.get(id=lead_id)
    client = TataAPIClient()
    result = client.initiate_click_to_call(agent_number, lead.phone_number)
    
    return JsonResponse(result or {'success': False})

@csrf_exempt  
@require_http_methods(["POST"])
def add_call_note(request):
    data = json.loads(request.body)
    call_id = data.get('call_id')
    message = data.get('message')
    
    client = TataAPIClient()
    result = client.add_call_note(call_id, message)
    
    # Also save locally
    try:
        call = TataCall.objects.get(call_id=call_id)
        CallNote.objects.create(call=call, message=message)
    except TataCall.DoesNotExist:
        pass
    
    return JsonResponse(result or {'success': False})

def calls_dashboard(request):
    from django.shortcuts import render
    return render(request, 'tata_integration/calls_dashboard.html')

def enhanced_calls_dashboard(request):
    from django.shortcuts import render
    return render(request, 'tata_integration/enhanced_calls_dashboard.html')

def analytics_dashboard(request):
    from django.shortcuts import render
    return render(request, 'tata_integration/analytics.html')

@require_http_methods(["GET"])
def recent_calls_api(request):
    limit = int(request.GET.get('limit', 50))  # Increased default limit
    # Only show calls with valid data
    calls = TataCall.objects.exclude(start_stamp__isnull=True).order_by('-start_stamp')[:limit]
    data = [{
        'customer_number': call.customer_number,
        'agent_name': call.agent_name,
        'department': call.department or 'General',
        'status': call.status,
        'duration': call.duration,
        'start_stamp': call.start_stamp.isoformat() if call.start_stamp else '',
        'start_time': call.start_stamp.strftime('%Y-%m-%d %H:%M:%S') if call.start_stamp else '',
        'recording_url': call.recording_url
    } for call in calls]
    
    # If no calls, show sample data
    if not data:
        data = [{
            'customer_number': 'No calls yet',
            'agent_name': 'Waiting for calls...',
            'department': 'General',
            'status': 'Ready',
            'duration': 0,
            'start_time': 'Webhooks configured'
        }]
    
    return JsonResponse({'calls': data, 'total_in_db': TataCall.objects.count()})

@csrf_exempt
@require_http_methods(["POST"])
def sync_calls(request):
    """Manual sync endpoint for calls"""
    try:
        # Get parameters from request
        data = json.loads(request.body) if request.body else {}
        days_back = data.get('days_back', 7)
        limit = data.get('limit', 100)
        
        client = TataAPIClient()
        result = client.sync_call_records(days_back=days_back, limit=limit)
        
        # Clean up any invalid calls after sync
        invalid_calls = TataCall.objects.filter(customer_number='', start_stamp__isnull=True)
        deleted_count = invalid_calls.count()
        if deleted_count > 0:
            invalid_calls.delete()
            result['cleaned_invalid'] = deleted_count
        
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'error': str(e), 'message': 'Sync failed'})

@require_http_methods(["GET"])
def sync_status(request):
    """Get auto sync status"""
    from django.conf import settings
    from .scheduler import scheduler
    
    return JsonResponse({
        'auto_sync_enabled': settings.AUTO_SYNC_ENABLED,
        'sync_interval': settings.SYNC_INTERVAL_MINUTES,
        'scheduler_running': scheduler.running,
        'last_sync': 'Check logs for details'
    })

@csrf_exempt
@require_http_methods(["POST"])
def toggle_auto_sync(request):
    """Toggle auto sync on/off"""
    from .scheduler import scheduler
    
    action = json.loads(request.body).get('action')
    
    if action == 'start':
        scheduler.start()
        return JsonResponse({'status': 'started', 'running': scheduler.running})
    elif action == 'stop':
        scheduler.stop()
        return JsonResponse({'status': 'stopped', 'running': scheduler.running})
    
    return JsonResponse({'error': 'Invalid action'})

@require_http_methods(["GET"])
def debug_tata_api(request):
    """Debug endpoint to test Tata API directly"""
    try:
        client = TataAPIClient()
        
        # Test different API endpoints
        active_calls = client.get_active_calls()
        call_records = client.get_call_records(limit=3)  # Get fewer records but show full structure
        
        # Extract field information from call records
        call_fields = []
        sample_call = None
        if call_records and 'results' in call_records and call_records['results']:
            sample_call = call_records['results'][0]
            call_fields = list(sample_call.keys())
        
        return JsonResponse({
            'call_records': call_records['results'][:2] if call_records and 'results' in call_records else call_records,
            'call_fields': call_fields,
            'sample_call': sample_call,
            'total_calls': call_records.get('count', 0) if call_records else 0,
            'token_used': client.token[:50] + '...',
            'base_url': client.BASE_URL
        })
    except Exception as e:
        return JsonResponse({'error': str(e)})

@csrf_exempt
@require_http_methods(["POST"])
def sync_all_tata_data(request):
    """Sync departments, agents, and recordings from Tata"""
    try:
        from .models import TataDepartment, TataAgent, TataRecording
        client = TataAPIClient()
        
        synced_data = {
            'departments': 0,
            'agents': 0,
            'recordings': 0,
            'errors': []
        }
        
        # Sync Departments
        try:
            departments_data = client.get_departments()
            synced_data['departments_raw'] = departments_data  # Debug info
            
            if departments_data and isinstance(departments_data, list):
                for dept_data in departments_data:
                    dept_obj, created = TataDepartment.objects.update_or_create(
                        dept_id=dept_data.get('id'),
                        defaults={
                            'name': dept_data.get('name', ''),
                            'description': dept_data.get('description', ''),
                            'ring_strategy': dept_data.get('ring_strategy', ''),
                            'agent_count': int(dept_data.get('agent_count', 0)),
                            'calls_answered': int(dept_data.get('calls_answered', 0)),
                            'calls_missed': int(dept_data.get('calls_missed', 0)),
                            'use_as_queue': dept_data.get('use_as_queue', False),
                            'queue_timeout': int(dept_data.get('queue_timeout', 90))
                        }
                    )
                    
                    # Sync agents in this department
                    agents_data = dept_data.get('agents', [])
                    for agent_data in agents_data:
                        TataAgent.objects.update_or_create(
                            agent_id=agent_data.get('id'),
                            defaults={
                                'name': agent_data.get('name', ''),
                                'extension_id': agent_data.get('eid', ''),
                                'department': dept_obj,
                                'timeout': int(agent_data.get('timeout', 30))
                            }
                        )
                        synced_data['agents'] += 1
                    
                    if created:
                        synced_data['departments'] += 1
            else:
                synced_data['errors'].append(f'No departments data received: {departments_data}')
        except Exception as e:
            synced_data['errors'].append(f'Departments sync error: {str(e)}')
        
        # Sync Recordings
        try:
            recordings_data = client.get_recordings()
            synced_data['recordings_raw'] = recordings_data  # Debug info
            
            if recordings_data and isinstance(recordings_data, list):
                for rec_data in recordings_data:
                    _, created = TataRecording.objects.update_or_create(
                        recording_id=rec_data.get('id'),
                        defaults={
                            'name': rec_data.get('name', ''),
                            'url': rec_data.get('url', ''),
                            'music_on_hold': rec_data.get('music_on_hold', False),
                            'is_default': rec_data.get('default', False)
                        }
                    )
                    if created:
                        synced_data['recordings'] += 1
            else:
                synced_data['errors'].append(f'No recordings data received: {recordings_data}')
        except Exception as e:
            synced_data['errors'].append(f'Recordings sync error: {str(e)}')
        
        return JsonResponse({
            'message': f"Synced {synced_data['departments']} departments, {synced_data['agents']} agents, {synced_data['recordings']} recordings",
            'data': synced_data,
            'debug': {
                'departments_response': synced_data.get('departments_raw'),
                'recordings_response': synced_data.get('recordings_raw'),
                'errors': synced_data.get('errors', [])
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e), 'message': 'Sync failed'})

@require_http_methods(["GET"])
def export_calls(request):
    """Export calls to CSV"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="calls_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Date', 'Time', 'Customer Number', 'Agent Name', 'Department', 'Duration (s)', 'Status', 'Recording URL'])
    
    calls = TataCall.objects.exclude(start_stamp__isnull=True).order_by('-start_stamp')
    for call in calls:
        writer.writerow([
            call.start_stamp.strftime('%Y-%m-%d') if call.start_stamp else '',
            call.start_stamp.strftime('%H:%M:%S') if call.start_stamp else '',
            call.customer_number,
            call.agent_name,
            call.department,
            call.duration,
            call.status,
            call.recording_url
        ])
    
    return response

@csrf_exempt
@require_http_methods(["POST"])
def sync_historical_meta(request):
    """Sync historical Meta leads (months old)"""
    try:
        from leads.meta_sync import sync_meta_leads
        from datetime import datetime, timedelta
        
        # Sync last 3 months of Meta leads
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        
        result = sync_meta_leads(start_date, end_date)
        return JsonResponse({
            'message': f'Historical Meta sync completed: {result.get("synced", 0)} leads',
            'result': result
        })
    except Exception as e:
        return JsonResponse({'error': str(e), 'message': 'Historical sync failed'})

@require_http_methods(["GET"])
def export_leads(request):
    """Export leads to CSV with optional source filter"""
    import csv
    from django.http import HttpResponse
    from leads.models import Lead
    
    source_filter = request.GET.get('source')
    
    response = HttpResponse(content_type='text/csv')
    filename = "leads_export.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    writer = csv.writer(response)
    writer.writerow(['Name', 'Phone', 'Email', 'Form Name', 'Budget', 'City', 'Configuration', 'Preferred Time', 'Created Date', 'Stage'])
    
    leads = Lead.objects.all().order_by('-created_time')
    
    # If source_filter is 'meta', export all leads (since we don't have a source field)
    # The user can filter manually if needed
    
    for lead in leads:
        writer.writerow([
            lead.full_name,
            lead.phone_number,
            lead.email,
            lead.form_name,
            lead.budget,
            lead.city,
            lead.configuration,
            lead.preferred_time,
            lead.created_time.strftime('%Y-%m-%d %H:%M:%S'),
            lead.stage
        ])
    
    return response

@require_http_methods(["GET"])
def tata_data_dashboard(request):
    """Dashboard showing all Tata data"""
    from django.shortcuts import render
    from django.db import connection
    
    # Check if tables exist
    table_names = connection.introspection.table_names()
    tables_exist = all(table in table_names for table in [
        'tata_integration_tatadepartment',
        'tata_integration_tataagent', 
        'tata_integration_tatarecording'
    ])
    
    if not tables_exist:
        context = {
            'departments': [],
            'agents': [],
            'recordings': [],
            'total_calls': TataCall.objects.count() if 'tata_integration_tatacall' in table_names else 0,
            'recent_calls': TataCall.objects.all().order_by('-created_at')[:10] if 'tata_integration_tatacall' in table_names else [],
            'need_migration': True
        }
    else:
        from .models import TataDepartment, TataAgent, TataRecording
        context = {
            'departments': TataDepartment.objects.all().prefetch_related('tataagent_set'),
            'agents': TataAgent.objects.all().select_related('department'),
            'recordings': TataRecording.objects.all(),
            'total_calls': TataCall.objects.count(),
            'recent_calls': TataCall.objects.all().order_by('-created_at')[:10],
            'need_migration': False
        }
    
    return render(request, 'tata_integration/tata_data_dashboard.html', context)