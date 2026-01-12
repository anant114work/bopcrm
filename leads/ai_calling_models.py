from django.db import models
from .project_models import Project

class AICallingAgent(models.Model):
    name = models.CharField(max_length=200)
    agent_id = models.CharField(max_length=200, unique=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, related_name='ai_agents')
    system_prompt = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.agent_id})"
    
    class Meta:
        ordering = ['-created_at']
