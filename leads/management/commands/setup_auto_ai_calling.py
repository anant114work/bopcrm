from django.core.management.base import BaseCommand
from leads.models import Lead
from leads.ai_agent_models import AIAgent, AICallLog
from leads.form_mapping_models import FormSourceMapping
from leads.project_models import Project

class Command(BaseCommand):
    help = 'Setup auto AI calling system with sample data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n🤖 Setting up Auto AI Calling System...\n'))
        
        # Check if projects exist
        projects = Project.objects.all()
        if not projects.exists():
            self.stdout.write(self.style.WARNING('⚠️  No projects found. Please create projects first at /projects/'))
            return
        
        self.stdout.write(f'✅ Found {projects.count()} projects')
        
        # Show existing agents
        agents = AIAgent.objects.all()
        self.stdout.write(f'📋 Current AI Agents: {agents.count()}')
        for agent in agents:
            self.stdout.write(f'   - {agent.name} ({agent.agent_id}) → {agent.project.name}')
        
        # Show existing mappings
        mappings = FormSourceMapping.objects.all()
        self.stdout.write(f'\n📋 Current Form Mappings: {mappings.count()}')
        for mapping in mappings:
            self.stdout.write(f'   - {mapping.form_name} → {mapping.project.name}')
        
        # Show call logs stats
        total_calls = AICallLog.objects.count()
        connected_calls = AICallLog.objects.filter(status='connected').count()
        failed_calls = AICallLog.objects.filter(status='failed').count()
        
        self.stdout.write(f'\n📊 Call Statistics:')
        self.stdout.write(f'   Total Calls: {total_calls}')
        self.stdout.write(f'   Connected: {connected_calls}')
        self.stdout.write(f'   Failed: {failed_calls}')
        
        # Show unmapped leads
        unmapped_leads = Lead.objects.exclude(
            id__in=AICallLog.objects.values_list('lead_id', flat=True)
        ).filter(
            phone_number__isnull=False
        ).exclude(
            phone_number=''
        ).count()
        
        self.stdout.write(f'\n📞 Unmapped Leads (not yet called): {unmapped_leads}')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Setup complete!'))
        self.stdout.write('\n📖 Next Steps:')
        self.stdout.write('   1. Go to /ai-agents/ to manage agents and mappings')
        self.stdout.write('   2. Create AI agents for your projects')
        self.stdout.write('   3. Map form names to projects')
        self.stdout.write('   4. New leads will be automatically called!')
        self.stdout.write('\n📚 Documentation: AUTO_AI_CALLING.md\n')
