from django.core.management.base import BaseCommand
from django.utils import timezone
from leads.models import ScheduledMessage

class Command(BaseCommand):
    help = 'Process scheduled follow-up messages'

    def handle(self, *args, **options):
        now = timezone.now()
        pending_messages = ScheduledMessage.objects.filter(
            scheduled_time__lte=now,
            is_sent=False
        )
        
        for message in pending_messages:
            try:
                # Process follow-up message
                followup_text = self.get_followup_message(message.template_name)
                
                # Here you would send the actual WhatsApp message
                # For now, just mark as sent
                message.is_sent = True
                message.sent_at = now
                message.save()
                
                self.stdout.write(
                    self.style.SUCCESS(f'Sent follow-up: {message.template_name}')
                )
                
            except Exception as e:
                message.error_message = str(e)
                message.save()
                self.stdout.write(
                    self.style.ERROR(f'Failed to send follow-up: {e}')
                )
    
    def get_followup_message(self, template_name):
        followup_messages = {
            'gauraspireleisurepark1_followup': 'Hi! Just following up on Gaura Spire Leisure Park. Are you still interested in scheduling a site visit? 🏡',
            'gauraspireleisurepark2_followup': 'Hello! Hope you had a chance to review our project details. Would you like to discuss any specific requirements? 📞'
        }
        return followup_messages.get(template_name, 'Follow-up message')