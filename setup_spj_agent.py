import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.ai_calling_models import AICallingAgent

# Create or update SPJ Vedatam agent with correct ID
# Based on call history, SPJ uses a different agent than AU Reality
spj_agent, created = AICallingAgent.objects.get_or_create(
    name='SPJ Vedatam',
    defaults={
        'agent_id': '678091e5e4b0e1e0e0e0e0e0',  # Placeholder - need actual ID
        'phone_number': '917943595082',
        'is_active': True
    }
)

if not created:
    spj_agent.phone_number = '917943595082'
    spj_agent.is_active = True
    spj_agent.save()

print(f"SPJ Agent: {spj_agent.name}")
print(f"Agent ID: {spj_agent.agent_id}")
print(f"Phone: {spj_agent.phone_number}")
print(f"Active: {spj_agent.is_active}")

# Check all agents
print("\nAll agents:")
for agent in AICallingAgent.objects.all():
    print(f"  {agent.name}: {agent.agent_id} ({agent.phone_number})")
