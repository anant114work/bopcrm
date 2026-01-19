from django.core.management.base import BaseCommand
from leads.google_ads_sync import GoogleAdsSyncService
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Sync data from Google Ads API'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            default='full',
            choices=['full', 'campaigns', 'leads', 'performance'],
            help='Type of sync to perform'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Number of days back to sync (for leads and performance)'
        )
    
    def handle(self, *args, **options):
        sync_type = options['type']
        days_back = options['days']
        
        self.stdout.write(f'Starting Google Ads sync: {sync_type}')
        
        sync_service = GoogleAdsSyncService()
        
        if sync_type == 'campaigns':
            result = sync_service.sync_campaigns()
            self.stdout.write(
                self.style.SUCCESS('Campaigns synced successfully!') if result 
                else self.style.ERROR('Failed to sync campaigns')
            )
        elif sync_type == 'leads':
            result = sync_service.sync_leads(days_back)
            self.stdout.write(
                self.style.SUCCESS(f'Leads synced successfully! ({days_back} days back)') if result 
                else self.style.ERROR('Failed to sync leads')
            )
        elif sync_type == 'performance':
            result = sync_service.sync_performance(days_back)
            self.stdout.write(
                self.style.SUCCESS(f'Performance data synced successfully! ({days_back} days back)') if result 
                else self.style.ERROR('Failed to sync performance data')
            )
        else:  # full sync
            results = sync_service.full_sync()
            success_count = sum(1 for r in results.values() if r)
            
            self.stdout.write(f'Full sync completed: {success_count}/3 successful')
            for sync_name, success in results.items():
                status = self.style.SUCCESS('✓') if success else self.style.ERROR('✗')
                self.stdout.write(f'{status} {sync_name.capitalize()}')
        
        self.stdout.write('Google Ads sync completed!')