from django.core.management.base import BaseCommand
from leads.models import TeamMember
from leads.acefone_models import ClickApiKey

class Command(BaseCommand):
    help = 'Setup Click-to-Call API tokens for team members'

    def add_arguments(self, parser):
        parser.add_argument('--token', type=str, help='API token to assign')
        parser.add_argument('--agent-email', type=str, help='Agent email to assign token to')
        parser.add_argument('--global', action='store_true', help='Create global token')

    def handle(self, *args, **options):
        token = options.get('token')
        agent_email = options.get('agent_email')
        is_global = options.get('global')

        if not token:
            self.stdout.write(self.style.ERROR('Token is required'))
            return

        if is_global:
            # Create global token
            api_key, created = ClickApiKey.objects.get_or_create(
                name='Global Click-to-Call Token',
                defaults={
                    'api_token': token,
                    'agent': None,
                    'enabled': True
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS('Global token created successfully'))
            else:
                api_key.api_token = token
                api_key.save()
                self.stdout.write(self.style.SUCCESS('Global token updated successfully'))
        
        elif agent_email:
            # Assign token to specific agent
            try:
                team_member = TeamMember.objects.get(email=agent_email)
                api_key, created = ClickApiKey.objects.get_or_create(
                    agent=team_member,
                    defaults={
                        'name': f'{team_member.name} Click Token',
                        'api_token': token,
                        'enabled': True
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Token assigned to {team_member.name}'))
                else:
                    api_key.api_token = token
                    api_key.save()
                    self.stdout.write(self.style.SUCCESS(f'Token updated for {team_member.name}'))
            except TeamMember.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Team member with email {agent_email} not found'))
        else:
            self.stdout.write(self.style.ERROR('Either --agent-email or --global is required'))