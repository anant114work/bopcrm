from django.core.management.base import BaseCommand
from leads.project_models import Project
from leads.whatsapp_models import WhatsAppTemplate

class Command(BaseCommand):
    help = 'Setup WhatsApp templates for Gaur Aspire Leisure Park'

    def handle(self, *args, **options):
        try:
            project = Project.objects.get(name__icontains='Gaur Aspire Leisure Park')
        except Project.DoesNotExist:
            self.stdout.write(self.style.ERROR('Gaur Aspire Leisure Park project not found'))
            return

        # Template 1 - Image template
        template1, created1 = WhatsAppTemplate.objects.get_or_create(
            project=project,
            name='gauraspireleisure1',
            defaults={
                'template_type': 'IMAGE',
                'message_text': """Here's a quick glimpse of what makes Aspire Leisure Park truly special:

🏙️ Podium-based premium residences
🌳 8+ acres of lush open green area
🏢 Grand 11 ft ceiling heights for spacious living
🎯 Only 4 apartments per floor – all corner units
🏋️♀️ Lavish clubhouse (75,000+ sq. ft.) with modern amenities
🚗 Free car parking, maintenance & club membership

Every detail is designed to offer you the perfect blend of luxury, space, and serenity""",
                'api_key': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY4ZGVhNzVlYTM3MDcyNTJiYzJhZWY1NyIsIm5hbWUiOiJBQkMgRGlnaXRhbCBJbmMiLCJhcHBOYW1lIjoiQWlTZW5zeSIsImNsaWVudElkIjoiNjhkZWE3NWVhMzcwNzI1MmJjMmFlZjUyIiwiYWN0aXZlUGxhbiI6IkZSRUVfRk9SRVZFUiIsImlhdCI6MTc1OTQyMjMwMn0.GzXAy0qINll2QxsM9Q73B8SHBPeHMXiXZ1ypm8ScNbE',
                'campaign_name': 'gauraspireleisure1',
                'drip_delay_minutes': 0,
                'order': 1
            }
        )

        # Template 2 - Text template with 30 min delay
        template2, created2 = WhatsAppTemplate.objects.get_or_create(
            project=project,
            name='gauraspireleisure2',
            defaults={
                'template_type': 'TEXT',
                'message_text': """🌟 Thank You for Showing Interest! 🌟

Dear {{1}},
We truly appreciate your interest in Aspire Leisure Park – Greater Noida (W) 🏡

Your journey toward owning a luxurious 3+Study or 4+Study residence has just begun, and we're excited to help you find your dream home. ✨""",
                'api_key': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY4ZGVhNzVlYTM3MDcyNTJiYzJhZWY1NyIsIm5hbWUiOiJBQkMgRGlnaXRhbCBJbmMiLCJhcHBOYW1lIjoiQWlTZW5zeSIsImNsaWVudElkIjoiNjhkZWE3NWVhMzcwNzI1MmJjMmFlZjUyIiwiYWN0aXZlUGxhbiI6IkZSRUVfRk9SRVZFUiIsImlhdCI6MTc1OTQyMjMwMn0.GzXAy0qINll2QxsM9Q73B8SHBPeHMXiXZ1ypm8ScNbE',
                'campaign_name': 'gauraspireleisure2',
                'drip_delay_minutes': 30,
                'order': 2
            }
        )

        if created1:
            self.stdout.write(self.style.SUCCESS('Created template: gauraspireleisure1'))
        else:
            self.stdout.write(self.style.WARNING('Template gauraspireleisure1 already exists'))

        if created2:
            self.stdout.write(self.style.SUCCESS('Created template: gauraspireleisure2'))
        else:
            self.stdout.write(self.style.WARNING('Template gauraspireleisure2 already exists'))

        self.stdout.write(self.style.SUCCESS(f'Setup complete for project: {project.name}'))