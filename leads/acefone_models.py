from django.db import models
from django.contrib.auth.models import User

class AcefoneConfig(models.Model):
    token = models.TextField()
    base_url = models.URLField(default='https://api.acefone.in/v1')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ClickApiKey(models.Model):
    """Store Click-to-Call API tokens per agent"""
    name = models.CharField(max_length=100)
    api_token = models.TextField()
    agent = models.ForeignKey('TeamMember', null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    enabled = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} - {self.agent.name if self.agent else 'Global'}"

class DIDNumber(models.Model):
    number = models.CharField(max_length=20, unique=True)
    display_name = models.CharField(max_length=100)
    assigned_user = models.ForeignKey('TeamMember', on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.display_name} ({self.number[-4:]})"

class CallRecord(models.Model):
    CALL_STATUS = [
        ('initiating', 'Initiating'),
        ('initiated', 'Initiated'),
        ('ringing', 'Ringing'),
        ('answered', 'Answered'),
        ('completed', 'Completed'),
        ('missed', 'Missed'),
        ('failed', 'Failed'),
    ]
    
    acefone_call_id = models.CharField(max_length=128, blank=True, null=True)
    lead = models.ForeignKey('Lead', on_delete=models.CASCADE, related_name='calls', null=True, blank=True)
    agent = models.ForeignKey('TeamMember', on_delete=models.SET_NULL, null=True)
    lead_name = models.CharField(max_length=255, blank=True)
    lead_number = models.CharField(max_length=32)
    from_number = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=20, choices=CALL_STATUS, default='initiating')
    duration = models.IntegerField(null=True, blank=True)  # seconds
    recording_url = models.URLField(blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Call to {self.lead_name or self.lead_number} - {self.status}"
    
    class Meta:
        ordering = ['-created_at']