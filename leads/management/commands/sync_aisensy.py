from django.core.management.base import BaseCommand
import requests
from leads.models import Project
from leads.whatsapp_models import WhatsAppTemplate, WhatsAppCampaign
try:
    from whatsapp_config import AISENSY_API_KEY
except ImportError:
    AISENSY_API_KEY = "your_api_key_here"

class Command(BaseCommand):
    help = 'Sync templates and campaigns from AI Sensy'

    def handle(self, *args, **options):
        self.sync_templates()
        self.sync_campaigns()

    def sync_templates(self):
        try:
            # Get templates from AI Sensy API
            response = requests.get(
                'https://backend.aisensy.com/campaign/t1/api/v2/templates',
                headers={'Authorization': f'Bearer {AISENSY_API_KEY}'}
            )
            
            if response.status_code == 200:
                templates = response.json()
                
                for template_data in templates:
                    # Get or create default project
                    project, _ = Project.objects.get_or_create(
                        name='AI Sensy Templates',
                        defaults={'code': 'aisensy', 'developer': 'AI Sensy', 'location': 'Digital'}
                    )
                    
                    # Create or update template
                    template, created = WhatsAppTemplate.objects.update_or_create(
                        name=template_data.get('name', 'Unknown'),
                        project=project,
                        defaults={
                            'template_type': 'TEXT',
                            'message_text': template_data.get('body', ''),
                            'api_key': AISENSY_API_KEY,
                            'campaign_name': template_data.get('name', 'Unknown'),
                            'is_active': True
                        }
                    )
                    
                    action = 'Created' if created else 'Updated'
                    self.stdout.write(f'{action} template: {template.name}')
                    
            else:
                self.stdout.write(f'Failed to fetch templates: {response.status_code}')
                
        except Exception as e:
            self.stdout.write(f'Error syncing templates: {e}')

    def sync_campaigns(self):
        try:
            # Get campaigns from AI Sensy API
            response = requests.get(
                'https://backend.aisensy.com/campaign/t1/api/v2/campaigns',
                headers={'Authorization': f'Bearer {AISENSY_API_KEY}'}
            )
            
            if response.status_code == 200:
                campaigns = response.json()
                
                for campaign_data in campaigns:
                    # Get project
                    project, _ = Project.objects.get_or_create(
                        name='AI Sensy Campaigns',
                        defaults={'code': 'aisensy_campaigns', 'developer': 'AI Sensy', 'location': 'Digital'}
                    )
                    
                    # Get template
                    template_name = campaign_data.get('templateName', 'Unknown')
                    template = WhatsAppTemplate.objects.filter(name=template_name).first()
                    
                    if template:
                        # Create or update campaign
                        campaign, created = WhatsAppCampaign.objects.update_or_create(
                            name=campaign_data.get('name', 'Unknown'),
                            project=project,
                            defaults={
                                'template': template,
                                'status': campaign_data.get('status', 'draft').lower(),
                                'messages_sent': campaign_data.get('sent', 0),
                                'messages_delivered': campaign_data.get('delivered', 0),
                                'messages_failed': campaign_data.get('failed', 0)
                            }
                        )
                        
                        action = 'Created' if created else 'Updated'
                        self.stdout.write(f'{action} campaign: {campaign.name}')
                        
            else:
                self.stdout.write(f'Failed to fetch campaigns: {response.status_code}')
                
        except Exception as e:
            self.stdout.write(f'Error syncing campaigns: {e}')