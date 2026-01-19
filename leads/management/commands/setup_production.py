from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from leads.models import ZohoConfig
import os

class Command(BaseCommand):
    help = 'Setup production environment'

    def handle(self, *args, **options):
        self.stdout.write('Setting up production environment...')
        
        # Create superuser if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
            self.stdout.write(self.style.SUCCESS('Created admin user'))
        
        # Create Zoho config if environment variables exist
        zoho_client_id = os.getenv('ZOHO_CLIENT_ID')
        zoho_client_secret = os.getenv('ZOHO_CLIENT_SECRET')
        zoho_redirect_uri = os.getenv('ZOHO_REDIRECT_URI')
        
        if zoho_client_id and zoho_client_secret and zoho_redirect_uri:
            config, created = ZohoConfig.objects.get_or_create(
                defaults={
                    'client_id': zoho_client_id,
                    'client_secret': zoho_client_secret,
                    'redirect_uri': zoho_redirect_uri,
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS('Created Zoho configuration'))
        
        self.stdout.write(self.style.SUCCESS('Production setup complete!'))