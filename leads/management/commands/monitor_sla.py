from django.core.management.base import BaseCommand
from leads.assignment import RoundRobinAssigner

class Command(BaseCommand):
    help = 'Monitor and reassign overdue leads'

    def handle(self, *args, **options):
        assigner = RoundRobinAssigner()
        reassigned_count = assigner.reassign_overdue_leads()
        
        self.stdout.write(
            self.style.SUCCESS(f'Reassigned {reassigned_count} overdue leads')
        )