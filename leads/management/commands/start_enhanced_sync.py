"""
Django management command to start enhanced Meta sync
Usage: python manage.py start_enhanced_sync
"""
from django.core.management.base import BaseCommand
from leads.enhanced_meta_sync import meta_sync

class Command(BaseCommand):
    help = 'Start enhanced Meta sync service for 2000+ forms'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting Enhanced Meta Sync Service...')
        )
        
        try:
            result = meta_sync.start_auto_sync()
            
            if result['status'] == 'started':
                self.stdout.write(
                    self.style.SUCCESS(f'✓ {result["message"]}')
                )
                self.stdout.write('Press Ctrl+C to stop the service')
                
                # Keep running until interrupted
                try:
                    import time
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    self.stdout.write('\nStopping sync service...')
                    meta_sync.stop_auto_sync()
                    self.stdout.write(
                        self.style.SUCCESS('✓ Sync service stopped')
                    )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Service already running: {result["status"]}')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error starting sync: {str(e)}')
            )