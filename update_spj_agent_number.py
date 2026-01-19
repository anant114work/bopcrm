import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.ai_calling_models import AICallingAgent

try:
    agent = AICallingAgent.objects.get(agent_id='69609b8f9cd0a3ca06a3792b')
    
    # Update to new agent ID with new phone number
    agent.agent_id = '917943595082'
    agent.save()
    
    print(f"Successfully updated agent '{agent.name}' phone number to: {agent.agent_id}")
except AICallingAgent.DoesNotExist:
    print("Agent not found")
except Exception as e:
    print(f"Error: {e}")
