import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.ai_calling_models import AICallingAgent
from leads.project_models import Project

try:
    agent = AICallingAgent.objects.get(agent_id='69609b8f9cd0a3ca06a3792b')
    project = Project.objects.get(code='gurg123')  # SPJ project
    
    agent.project = project
    agent.save()
    
    print(f"Successfully linked agent '{agent.name}' to project '{project.name}'")
except AICallingAgent.DoesNotExist:
    print("Agent not found")
except Project.DoesNotExist:
    print("Project 'SPJ' not found")
except Exception as e:
    print(f"Error: {e}")
