from django.core.management.base import BaseCommand
from leads.models import Lead
from collections import defaultdict

class Command(BaseCommand):
    help = 'Remove duplicate leads based on phone numbers'

    def handle(self, *args, **options):
        phone_groups = defaultdict(list)
        
        # Group leads by normalized phone number
        for lead in Lead.objects.all():
            if lead.phone_number:
                normalized = lead.phone_number.replace('+91', '').replace('+', '').replace(' ', '').replace('-', '')
                phone_groups[normalized].append(lead)
        
        duplicates_removed = 0
        
        for phone, leads in phone_groups.items():
            if len(leads) > 1:
                # Keep the oldest lead, remove others
                leads.sort(key=lambda x: x.created_time)
                keep_lead = leads[0]
                
                for duplicate_lead in leads[1:]:
                    try:
                        self.stdout.write(f"Removing duplicate: ID {duplicate_lead.id}")
                        duplicate_lead.delete()
                        duplicates_removed += 1
                    except Exception as e:
                        self.stdout.write(f"Error removing duplicate: {str(e)}")
                        continue
        
        self.stdout.write(
            self.style.SUCCESS(f'Cleanup completed: {duplicates_removed} duplicate leads removed')
        )