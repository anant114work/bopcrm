from django.core.management.base import BaseCommand
from leads.callkaro_models import CallKaroAgent

class Command(BaseCommand):
    help = 'Add Gaur Chrysalis agent to CallKaro system'

    def handle(self, *args, **options):
        # Create or update Gaur Chrysalis agent
        agent, created = CallKaroAgent.objects.get_or_create(
            agent_id='693bbcbbf874761d1f74ad5c',
            defaults={
                'name': 'Gaur Chrysalis',
                'description': 'AI agent for Gaur Yamuna Chrysalis project lead qualification and conversion',
                'agent_type': 'project_specific',
                'project_name': 'Gaur Yamuna Chrysalis',
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created Gaur Chrysalis agent: {agent.agent_id}')
            )
        else:
            # Update existing agent
            agent.name = 'Gaur Chrysalis'
            agent.description = 'AI agent for Gaur Yamuna Chrysalis project lead qualification and conversion'
            agent.agent_type = 'project_specific'
            agent.project_name = 'Gaur Yamuna Chrysalis'
            agent.is_active = True
            agent.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully updated Gaur Chrysalis agent: {agent.agent_id}')
            )