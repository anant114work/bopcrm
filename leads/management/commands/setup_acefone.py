from django.core.management.base import BaseCommand
from leads.acefone_models import AcefoneConfig, DIDNumber
from leads.models import TeamMember

class Command(BaseCommand):
    help = 'Setup Acefone configuration'

    def handle(self, *args, **options):
        # Create Acefone config
        config, created = AcefoneConfig.objects.get_or_create(
            defaults={
                'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIyMjI3MDciLCJjciI6ZmFsc2UsImlzcyI6Imh0dHBzOi8vY29uc29sZS5hY2Vmb25lLmluL3Rva2VuL2dlbmVyYXRlIiwiaWF0IjoxNzYzMDk4NjQxLCJleHAiOjIwNjMwOTg2NDEsIm5iZiI6MTc2MzA5ODY0MSwianRpIjoiVHVkREI5bTVGVUFFYzBwNSJ9.v3kNbsK7AiOp42pwVPLkSyBsiN3GwOlzRJtMaoyMi6c',
                'base_url': 'https://api.acefone.in/v1',
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Created Acefone configuration'))
        
        self.stdout.write(self.style.SUCCESS('Acefone setup completed!'))