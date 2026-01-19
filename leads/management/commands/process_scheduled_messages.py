from django.core.management.base import BaseCommand
from django.utils import timezone
from leads.models import ScheduledMessage
from leads.whatsapp import send_whatsapp_message

class Command(BaseCommand):
    help = 'Process and send scheduled WhatsApp messages'

    def handle(self, *args, **options):
        # Get messages that are due
        due_messages = ScheduledMessage.objects.filter(
            scheduled_time__lte=timezone.now(),
            is_sent=False
        )
        
        sent_count = 0
        failed_count = 0
        
        self.stdout.write(f'Found {due_messages.count()} messages to process')
        
        for msg in due_messages:
            try:
                self.stdout.write(f'Processing message for {msg.lead.full_name} ({msg.lead.phone_number})')
                success, message = send_whatsapp_message(msg.lead, msg.template_name)
                
                if success:
                    msg.is_sent = True
                    msg.sent_at = timezone.now()
                    sent_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Sent to {msg.lead.full_name}')
                    )
                else:
                    msg.error_message = message
                    failed_count += 1
                    self.stdout.write(
                        self.style.ERROR(f'Failed to send to {msg.lead.full_name}: {message}')
                    )
                    
                msg.save()
                
            except Exception as e:
                msg.error_message = str(e)
                msg.save()
                failed_count += 1
                self.stdout.write(
                    self.style.ERROR(f'Error sending to {msg.lead.full_name}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Processing complete: {sent_count} sent, {failed_count} failed'
            )
        )