from django.core.management.base import BaseCommand
from django.utils import timezone
from leads.drip_campaign_models import DripSubscriber, DripMessage, DripMessageLog
from leads.drip_campaign_views import send_drip_message
import time

class Command(BaseCommand):
    help = 'Process pending drip campaign messages'

    def add_arguments(self, parser):
        parser.add_argument(
            '--continuous',
            action='store_true',
            help='Run continuously, checking every 60 seconds',
        )

    def handle(self, *args, **options):
        if options['continuous']:
            self.stdout.write('Starting continuous drip message processing...')
            while True:
                self.process_pending_messages()
                time.sleep(60)  # Wait 60 seconds before next check
        else:
            self.process_pending_messages()

    def process_pending_messages(self):
        """Process all pending drip messages"""
        now = timezone.now()
        
        # Get all subscribers with pending messages
        subscribers_ready = DripSubscriber.objects.filter(
            status='active',
            next_message_at__lte=now
        )
        
        processed_count = 0
        success_count = 0
        
        for subscriber in subscribers_ready:
            next_message = subscriber.get_next_message()
            if next_message:
                self.stdout.write(f'Processing message for {subscriber.phone_number} - Day {next_message.day_number}')
                
                result = send_drip_message(subscriber, next_message)
                processed_count += 1
                
                if result['success']:
                    success_count += 1
                    subscriber.current_day = next_message.day_number
                    subscriber.schedule_next_message()
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Sent Day {next_message.day_number} message to {subscriber.phone_number}')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f'✗ Failed to send message to {subscriber.phone_number}: {result["error"]}')
                    )
        
        if processed_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'Processed {processed_count} messages. {success_count} successful, {processed_count - success_count} failed.')
            )
        else:
            self.stdout.write('No pending messages to process.')