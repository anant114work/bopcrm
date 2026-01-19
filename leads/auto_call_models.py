from django.db import models
from .models import TeamMember

class AutoCallConfig(models.Model):
    project_name = models.CharField(max_length=100, help_text="Project name to trigger calls for (e.g., 'Chrysalis')")
    is_active = models.BooleanField(default=True)
    mapped_agent = models.ForeignKey(TeamMember, on_delete=models.CASCADE, help_text="Agent to receive calls")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.project_name} -> {self.mapped_agent.name}"
    
    class Meta:
        unique_together = ['project_name', 'mapped_agent']

class AutoCallLog(models.Model):
    STATUS_CHOICES = [
        ('initiated', 'Call Initiated'),
        ('connected', 'Call Connected'),
        ('failed', 'Call Failed'),
        ('no_answer', 'No Answer'),
    ]
    
    lead = models.ForeignKey('Lead', on_delete=models.CASCADE)
    agent = models.ForeignKey(TeamMember, on_delete=models.CASCADE)
    call_id = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='initiated')
    initiated_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.lead.full_name} -> {self.agent.name} ({self.status})"
    
    class Meta:
        ordering = ['-initiated_at']