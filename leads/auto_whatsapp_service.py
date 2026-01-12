import requests
import random
from django.utils import timezone
from .whatsapp_models import WhatsAppMessage
try:
    from whatsapp_config import AISENSY_API_URL
except ImportError:
    AISENSY_API_URL = "https://backend.aisensy.com/campaign/t1/api/v2"

def send_auto_whatsapp_to_lead(lead, campaign, request=None):
    """Send automatic WhatsApp message to a lead"""
    if not lead.phone_number:
        return False
    
    template = campaign.template
    project = campaign.project
    
    # Check if already sent
    if WhatsAppMessage.objects.filter(lead=lead, template=template).exists():
        return False
    
    try:
        # Get project image
        project_image_url = ''
        project_images = project.images.all()
        if project_images:
            random_image = random.choice(list(project_images))
            if request:
                project_image_url = request.build_absolute_uri(random_image.image.url)
            else:
                project_image_url = random_image.image.url
        
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
            headers={'Content-Type': 'application/json'},
            timeout=10
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
        
        return response.status_code == 200
    except Exception as e:
        # Log failed attempt
        WhatsAppMessage.objects.create(
            template=template,
            lead=lead,
            phone_number=lead.phone_number,
            recipient_name=lead.full_name,
            final_message_text=template.message_text,
            status='failed',
            sent_at=timezone.now(),
            api_response={'error': str(e)}
        )
        return False

def trigger_auto_campaigns_for_lead(lead):
    """Trigger all active auto campaigns for a lead's project"""
    from .auto_whatsapp_models import AutoWhatsAppCampaign
    from .form_mapping_views import get_project_by_form
    
    # Get project for this lead
    project = get_project_by_form(lead.form_name)
    if not project:
        return 0
    
    # Get active campaigns for this project
    campaigns = AutoWhatsAppCampaign.objects.filter(
        project=project,
        is_active=True
    )
    
    sent_count = 0
    for campaign in campaigns:
        if campaign.delay_minutes == 0:
            # Send immediately
            if send_auto_whatsapp_to_lead(lead, campaign):
                sent_count += 1
        else:
            # Schedule for later (you can implement scheduling here)
            pass
    
    return sent_count
