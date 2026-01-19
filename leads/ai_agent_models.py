from django.db import models
from .project_models import Project

class AIAgent(models.Model):
    """AI calling agents for different projects"""
    name = models.CharField(max_length=100)
    agent_id = models.CharField(max_length=100, unique=True, help_text="Call Karo AI agent ID")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='ai_agents')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.project.name}"
    
    class Meta:
        ordering = ['project__name', 'name']

class AICallLog(models.Model):
    """Log of all AI calls made to prevent duplicates"""
    STATUS_CHOICES = [
        ('initiated', 'Initiated'),
        ('connected', 'Connected'),
        ('failed', 'Failed'),
        ('no_answer', 'No Answer'),
    ]
    
    lead = models.ForeignKey('Lead', on_delete=models.CASCADE, related_name='ai_call_logs')
    agent = models.ForeignKey(AIAgent, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='initiated')
    call_id = models.CharField(max_length=100, blank=True)
    initiated_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.lead.full_name} - {self.agent.name} ({self.status})"
    
    class Meta:
        ordering = ['-initiated_at']
        indexes = [
            models.Index(fields=['lead', 'status']),
            models.Index(fields=['phone_number', 'initiated_at']),
        ]
