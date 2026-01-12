from django.core.management.base import BaseCommand
from leads.booking_source_models import BookingSourceCategory, BookingSource

class Command(BaseCommand):
    help = 'Setup initial booking source categories and sources'

    def handle(self, *args, **options):
        # Create categories
        direct_category, _ = BookingSourceCategory.objects.get_or_create(name='Direct')
        broker_category, _ = BookingSourceCategory.objects.get_or_create(name='Broker')
        
        # Direct sources
        direct_sources = [
            'Newspaper',
            'Pamphlet',
            'Activity',
            'Marketing (Meta)',
            'Marketing (Google)',
            'Website',
            'Walk-in',
            'Referral',
            'Social Media',
            'Radio',
            'TV Advertisement'
        ]
        
        for source_name in direct_sources:
            BookingSource.objects.get_or_create(
                category=direct_category,
                name=source_name
            )
        
        # Broker sources
        broker_sources = [
            'Channel Partner',
            'Real Estate Agent',
            'Property Consultant',
            'Broker Network',
            'Third Party'
        ]
        
        for source_name in broker_sources:
            BookingSource.objects.get_or_create(
                category=broker_category,
                name=source_name
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {len(direct_sources)} direct sources and {len(broker_sources)} broker sources'
            )
        )