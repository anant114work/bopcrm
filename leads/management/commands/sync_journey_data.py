from django.core.management.base import BaseCommand
from leads.models import Lead
from leads.journey_models import LeadJourney, DuplicatePhoneTracker
from leads.whatsapp_models import WhatsAppMessage
from tata_integration.models import TataCall

class Command(BaseCommand):
    help = 'Sync existing data to journey tracking and duplicate detection'

    def handle(self, *args, **options):
        self.sync_lead_journeys()
        self.sync_duplicate_phones()
        
    def sync_lead_journeys(self):
        # Create journey entries for existing leads
        for lead in Lead.objects.all():
            # Form submission entry
            LeadJourney.objects.get_or_create(
                lead=lead,
                journey_type='form_submission',
                title=f'Form submitted: {lead.form_name}',
                description=f'Lead created from {lead.form_name}',
                source_type='meta' if 'meta' in lead.form_name.lower() else 'google',
                created_at=lead.created_time
            )
            
            # WhatsApp messages
            for msg in WhatsAppMessage.objects.filter(lead=lead):
                LeadJourney.objects.get_or_create(
                    lead=lead,
                    journey_type='whatsapp_message',
                    title=f'WhatsApp sent: {msg.template.name if msg.template else "Unknown"}',
                    description=msg.final_message_text[:100],
                    created_at=msg.sent_at or msg.created_at
                )
        
        self.stdout.write('Journey entries synced')
    
    def sync_duplicate_phones(self):
        # Track duplicate phone numbers
        phone_counts = {}
        
        # Count Meta leads
        for lead in Lead.objects.exclude(phone_number=''):
            phone = lead.phone_number
            if phone not in phone_counts:
                phone_counts[phone] = {'meta': [], 'google': [], 'ivr': []}
            phone_counts[phone]['meta'].append(lead)
        
        # Count IVR calls
        for call in TataCall.objects.all():
            phone = call.customer_number
            if phone not in phone_counts:
                phone_counts[phone] = {'meta': [], 'google': [], 'ivr': []}
            phone_counts[phone]['ivr'].append(call)
        
        # Create duplicate trackers
        for phone, data in phone_counts.items():
            total = len(data['meta']) + len(data['google']) + len(data['ivr'])
            if total > 1:  # Only track if duplicates exist
                tracker, created = DuplicatePhoneTracker.objects.get_or_create(
                    phone_number=phone
                )
                
                # Add meta leads
                for lead in data['meta']:
                    tracker.meta_leads.add(lead)
                
                # Add IVR calls
                ivr_data = []
                for call in data['ivr']:
                    ivr_data.append({
                        'call_id': call.id,
                        'date': call.start_stamp.isoformat() if call.start_stamp else None,
                        'duration': call.duration,
                        'status': call.status
                    })
                tracker.ivr_calls = ivr_data
                tracker.save()
        
        self.stdout.write('Duplicate tracking synced')