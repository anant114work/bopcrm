from django.core.management.base import BaseCommand
from django.utils import timezone
from leads.models import Lead
import time

class Command(BaseCommand):
    help = 'Create test leads for admin verification'

    def handle(self, *args, **options):
        test_leads = [
            {
                'lead_id': f'TEST_{int(time.time())}_1',
                'full_name': 'John Doe',
                'email': 'john.doe@example.com',
                'phone_number': '9876543210',
                'form_name': 'Test Form 1',
                'city': 'Mumbai',
                'budget': '50L-1Cr',
                'configuration': '2BHK',
                'created_time': timezone.now(),
            },
            {
                'lead_id': f'TEST_{int(time.time())}_2',
                'full_name': 'Jane Smith',
                'email': 'jane.smith@example.com',
                'phone_number': '9876543211',
                'form_name': 'Test Form 2',
                'city': 'Delhi',
                'budget': '1Cr-2Cr',
                'configuration': '3BHK',
                'created_time': timezone.now(),
            },
            {
                'lead_id': f'TEST_{int(time.time())}_3',
                'full_name': 'Mike Johnson',
                'email': 'mike.johnson@example.com',
                'phone_number': '9876543212',
                'form_name': 'Migsun Projects',
                'city': 'Noida',
                'budget': '75L-1Cr',
                'configuration': '2BHK',
                'created_time': timezone.now(),
            }
        ]
        
        created_count = 0
        for lead_data in test_leads:
            lead, created = Lead.objects.get_or_create(
                lead_id=lead_data['lead_id'],
                defaults=lead_data
            )
            if created:
                created_count += 1
                self.stdout.write(f'Created lead: {lead.full_name}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} test leads')
        )