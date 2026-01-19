from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
import random
import requests
from .project_models import Project
from .whatsapp_models import WhatsAppTemplate, WhatsAppMessage
from .models import Lead
try:
    from whatsapp_config import AISENSY_API_KEY, AISENSY_API_URL
except ImportError:
    AISENSY_API_KEY = "your_api_key_here"
    AISENSY_API_URL = "https://backend.aisensy.com/campaign/t1/api/v2"

def project_bulk_whatsapp(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    # Get both WhatsApp templates and Drip campaigns
    templates = WhatsAppTemplate.objects.filter(project=project)
    
    # Get drip campaigns for this project
    from .drip_campaign_models import DripCampaign
    drip_campaigns = DripCampaign.objects.filter(project=project, status='active')
    
    leads = project.get_leads().filter(phone_number__isnull=False).exclude(phone_number='')
    
    # Check if user is admin (superuser or admin role)
    is_team_member = request.session.get('is_team_member', False)
    team_member_name = request.session.get('team_member_name', '')
    is_admin = (request.user.is_superuser or 
                team_member_name == 'ADMIN USER' or 
                (hasattr(request.user, 'team_member') and request.user.team_member.role == 'Admin'))
    
    # Only filter if user is team member AND not admin
    if is_team_member and not is_admin:
        team_member_id = request.session.get('team_member_id')
        if team_member_id:
            from .models import TeamMember
            try:
                team_member = TeamMember.objects.get(id=team_member_id)
                team_members = team_member.get_all_team_members()
                team_member_ids = [tm.id for tm in team_members]
                leads = leads.filter(assignment__assigned_to__id__in=team_member_ids)
            except TeamMember.DoesNotExist:
                leads = leads.none()
    
    leads_with_phone = leads.count()
    
    return render(request, 'leads/project_bulk_whatsapp.html', {
        'project': project,
        'templates': templates,
        'drip_campaigns': drip_campaigns,
        'leads': leads,
        'leads_with_phone': leads_with_phone
    })

@csrf_exempt
def send_bulk_whatsapp(request, project_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        template_id = data.get('template_id')
        send_to_all = data.get('send_to_all', False)
        lead_ids = data.get('lead_ids', [])
        
        # Check if it's a drip campaign or template
        if template_id and template_id.startswith('drip_'):
            # Handle drip campaign subscription
            campaign_id = template_id.replace('drip_', '')
            from .drip_campaign_models import DripCampaign, DripSubscriber
            from django.utils import timezone
            
            campaign = get_object_or_404(DripCampaign, id=campaign_id)
            project = get_object_or_404(Project, id=project_id)
            
            if send_to_all:
                leads = project.get_leads().filter(phone_number__isnull=False).exclude(phone_number='')
            else:
                leads = Lead.objects.filter(id__in=lead_ids, phone_number__isnull=False).exclude(phone_number='')
            
            subscribed_count = 0
            already_subscribed = 0
            
            for lead in leads:
                # Check if already subscribed
                if DripSubscriber.objects.filter(campaign=campaign, lead=lead).exists():
                    already_subscribed += 1
                    continue
                
                # Subscribe lead to drip campaign
                subscriber = DripSubscriber.objects.create(
                    campaign=campaign,
                    lead=lead,
                    phone_number=lead.phone_number,
                    first_name=lead.full_name or 'User',
                    status='active',
                    current_day=0,
                    next_message_at=timezone.now()
                )
                subscribed_count += 1
            
            return JsonResponse({
                'success': True,
                'message': f'Subscribed {subscribed_count} leads to {campaign.name}',
                'subscribed_count': subscribed_count,
                'already_subscribed': already_subscribed
            })
        
        # Handle regular WhatsApp template
        template_id = template_id.replace('template_', '') if template_id and template_id.startswith('template_') else template_id
        
        project = get_object_or_404(Project, id=project_id)
        template = get_object_or_404(WhatsAppTemplate, id=template_id)
        
        if send_to_all:
            leads = project.get_leads().filter(phone_number__isnull=False).exclude(phone_number='')
        else:
            leads = Lead.objects.filter(id__in=lead_ids, phone_number__isnull=False).exclude(phone_number='')
        
        # Check if user is admin (superuser or admin role)
        is_team_member = request.session.get('is_team_member', False)
        team_member_name = request.session.get('team_member_name', '')
        is_admin = (request.user.is_superuser or 
                    team_member_name == 'ADMIN USER' or 
                    (hasattr(request.user, 'team_member') and request.user.team_member.role == 'Admin'))
        
        # Only filter if user is team member AND not admin
        if is_team_member and not is_admin:
            team_member_id = request.session.get('team_member_id')
            if team_member_id:
                from .models import TeamMember
                try:
                    team_member = TeamMember.objects.get(id=team_member_id)
                    team_members = team_member.get_all_team_members()
                    team_member_ids = [tm.id for tm in team_members]
                    leads = leads.filter(assignment__assigned_to__id__in=team_member_ids)
                except TeamMember.DoesNotExist:
                    leads = leads.none()
        
        sent_count = 0
        failed_count = 0
        
        for lead in leads:
            try:
                # Get project image
                project_image_url = ''
                project_images = project.images.all()
                if project_images:
                    random_image = random.choice(project_images)
                    project_image_url = request.build_absolute_uri(random_image.image.url)
                
                # Build payload
                payload = {
                    "apiKey": template.api_key,
                    "campaignName": template.campaign_name,
                    "destination": f"91{lead.phone_number.replace('+91', '').replace('+', '')}",
                    "userName": "CRM System",
                    "templateParams": [lead.full_name or 'User'],
                    "source": lead.form_name or lead.source or "CRM System",
                    "media": {
                        "url": project_image_url,
                        "filename": "project_image"
                    } if project_image_url else {},
                    "buttons": [],
                    "carouselCards": [],
                    "location": {},
                    "attributes": {},
                    "paramsFallbackValue": {"FirstName": lead.full_name or "user"}
                }
                
                # Send message
                response = requests.post(
                    AISENSY_API_URL,
                    json=payload,
                    headers={'Content-Type': 'application/json'}
                )
                
                # Create message record
                WhatsAppMessage.objects.create(
                    template=template,
                    lead=lead,
                    phone_number=lead.phone_number,
                    recipient_name=lead.full_name,
                    final_message_text=template.message_text,
                    media_url=project_image_url,
                    status='sent' if response.status_code == 200 else 'failed',
                    sent_at=timezone.now(),
                    api_response=response.json() if response.status_code == 200 else {}
                )
                
                if response.status_code == 200:
                    sent_count += 1
                else:
                    failed_count += 1
                    
            except Exception as e:
                failed_count += 1
        
        return JsonResponse({
            'success': True,
            'message': f'Sent {sent_count} messages successfully. {failed_count} failed.',
            'sent_count': sent_count,
            'failed_count': failed_count
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})