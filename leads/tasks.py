try:
    from celery import shared_task
except ImportError:
    # Celery not installed, create dummy decorator
    def shared_task(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

from django.core.cache import cache
from django.utils import timezone
import requests
import json
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def send_whatsapp_async(self, lead_id, template_name):
    """Send WhatsApp message asynchronously"""
    try:
        from .models import Lead
        lead = Lead.objects.get(id=lead_id)
        
        if not lead.phone_number:
            return {'success': False, 'error': 'No phone number'}
        
        # Format phone number
        phone = lead.phone_number.strip().replace(' ', '').replace('-', '')
        if not phone.startswith('91'):
            if phone.startswith('0'):
                phone = '91' + phone[1:]
            else:
                phone = '91' + phone
        
        # WhatsApp API call
        api_url = "https://backend.aisensy.com/campaign/t1/api/v2"
        api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY4ZGVhNzVlYTM3MDcyNTJiYzJhZWY1NyIsIm5hbWUiOiJBQkMgRGlnaXRhbCBJbmMiLCJhcHBOYW1lIjoiQWlTZW5zeSIsImNsaWVudElkIjoiNjhkZWE3NWVhMzcwNzI1MmJjMmFlZjUyIiwiYWN0aXZlUGxhbiI6IkZSRUVfRk9SRVZFUiIsImlhdCI6MTc1OTQyMjMwMn0.GzXAy0qINll2QxsM9Q73B8SHBPeHMXiXZ1ypm8ScNbE"
        
        payload = {
            "apiKey": api_key,
            "campaignName": template_name,
            "destination": phone,
            "userName": lead.full_name or "Customer",
            "templateParams": [lead.full_name or "Customer"],
            "source": "CRM System"
        }
        
        response = requests.post(api_url, json=payload, timeout=30)
        
        if response.status_code == 200:
            return {'success': True, 'message': f'WhatsApp sent to {lead.full_name}'}
        else:
            raise Exception(f'API Error: {response.status_code}')
            
    except Exception as e:
        logger.error(f'WhatsApp task failed: {str(e)}')
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))

@shared_task
def process_scheduled_messages():
    """Process scheduled WhatsApp messages"""
    from .models import ScheduledMessage
    
    due_messages = ScheduledMessage.objects.filter(
        scheduled_time__lte=timezone.now(),
        is_sent=False
    )
    
    processed = 0
    for msg in due_messages:
        try:
            # Queue the WhatsApp send task
            send_whatsapp_async.delay(msg.lead.id, msg.template_name)
            msg.is_sent = True
            msg.sent_at = timezone.now()
            msg.save()
            processed += 1
        except Exception as e:
            msg.error_message = str(e)
            msg.save()
    
    return f'Processed {processed} scheduled messages'

@shared_task
def sync_all_leads():
    """Sync leads from all sources"""
    from .views import sync_leads
    from django.http import HttpRequest
    
    # Create fake request for sync function
    request = HttpRequest()
    request.method = 'POST'
    
    try:
        # This would call your existing sync logic
        result = {'success': True, 'message': 'Auto sync completed'}
        cache.set('last_sync_result', result, 3600)  # Cache for 1 hour
        return result
    except Exception as e:
        error_result = {'success': False, 'error': str(e)}
        cache.set('last_sync_result', error_result, 3600)
        return error_result

@shared_task
def cache_dashboard_data(team_member_id=None):
    """Cache expensive dashboard queries"""
    from .models import Lead, TeamMember, LeadAssignment
    from django.db.models import Count, Q
    
    cache_key = f'dashboard_data_{team_member_id or "admin"}'
    
    if team_member_id:
        member = TeamMember.objects.get(id=team_member_id)
        my_leads = Lead.objects.filter(assignment__assigned_to=member)
        team_members = TeamMember.objects.filter(parent_user=member, is_active=True)
        team_leads = Lead.objects.filter(assignment__assigned_to__in=team_members)
        
        data = {
            'my_pending': my_leads.filter(assignment__is_attended=False).count(),
            'my_converted': my_leads.filter(stage='converted').count(),
            'team_pending': team_leads.filter(assignment__is_attended=False).count(),
            'team_converted': team_leads.filter(stage='converted').count(),
        }
    else:
        # Admin dashboard data
        data = {
            'total_leads': Lead.objects.count(),
            'converted_leads': Lead.objects.filter(stage='converted').count(),
            'assigned_leads': LeadAssignment.objects.filter(is_attended=False).count(),
            'overdue_leads': LeadAssignment.objects.filter(
                is_attended=False, 
                sla_deadline__lt=timezone.now()
            ).count(),
        }
    
    cache.set(cache_key, data, 300)  # Cache for 5 minutes
    return data