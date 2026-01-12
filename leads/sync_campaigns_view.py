from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests
from .project_models import Project
from .whatsapp_models import WhatsAppTemplate, WhatsAppCampaign
try:
    from whatsapp_config import AISENSY_API_KEY
except ImportError:
    AISENSY_API_KEY = "your_api_key_here"

@csrf_exempt
def sync_campaigns_data(request):
    if request.method == 'POST':
        try:
            # Get campaigns from AI Sensy API
            campaigns_response = requests.get(
                'https://backend.aisensy.com/campaign/t1/api/v2/campaign',
                headers={
                    'X-AiSensy-API-Key': AISENSY_API_KEY,
                    'Content-Type': 'application/json'
                }
            )
            
            if campaigns_response.status_code != 200:
                return JsonResponse({
                    'success': False,
                    'error': f'Failed to fetch campaigns: {campaigns_response.status_code}'
                })
            
            campaigns_data = campaigns_response.json().get('data', [])
            
            # Get or create AI Sensy project
            project, _ = Project.objects.get_or_create(
                name='AI Sensy Campaigns',
                defaults={'code': 'aisensy_campaigns', 'developer': 'AI Sensy', 'location': 'Digital'}
            )
            
            campaigns_synced = 0
            for campaign_data in campaigns_data:
                # Find matching template
                template_name = campaign_data.get('templateName', campaign_data.get('name', 'Unknown'))
                template = WhatsAppTemplate.objects.filter(name=template_name).first()
                
                if template:
                    WhatsAppCampaign.objects.update_or_create(
                        name=campaign_data.get('name', 'Unknown'),
                        project=project,
                        defaults={
                            'template': template,
                            'status': campaign_data.get('status', 'draft').lower(),
                            'total_leads': campaign_data.get('audience', 0),
                            'messages_sent': campaign_data.get('sent', 0),
                            'messages_delivered': campaign_data.get('delivered', 0),
                            'messages_failed': campaign_data.get('failed', 0)
                        }
                    )
                    campaigns_synced += 1
            
            return JsonResponse({
                'success': True,
                'campaigns_synced': campaigns_synced,
                'message': f'Synced {campaigns_synced} campaigns from AI Sensy'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})