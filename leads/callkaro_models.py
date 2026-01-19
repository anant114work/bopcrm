from django.db import models
from django.utils import timezone
from .models import Lead, TeamMember

class CallKaroConfig(models.Model):
    """Configuration for Call Karo AI integration"""
    api_key = models.CharField(max_length=255, help_text="Call Karo AI API Key")
    default_agent_id = models.CharField(max_length=100, help_text="Default AI Agent ID")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Call Karo Configuration"
        verbose_name_plural = "Call Karo Configurations"
    
    def __str__(self):
        return f"Call Karo Config - Agent: {self.default_agent_id}"

class CallKaroAgent(models.Model):
    """AI Agents available in Call Karo"""
    AGENT_TYPES = [
        ('general', 'General Purpose'),
        ('lead_qualification', 'Lead Qualification'),
        ('project_specific', 'Project Specific'),
        ('follow_up', 'Follow Up'),
    ]
    
    agent_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    agent_type = models.CharField(max_length=50, choices=AGENT_TYPES, default='general')
    project_name = models.CharField(max_length=200, blank=True, help_text="For project-specific agents")
    assigned_team_member = models.ForeignKey(
        TeamMember, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Team member this agent is assigned to"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Call Karo Agent"
        verbose_name_plural = "Call Karo Agents"
    
    def __str__(self):
        return f"{self.name} ({self.agent_id})"

class CallKaroCampaign(models.Model):
    """Call Karo AI Campaigns (Batch Calls)"""
    name = models.CharField(max_length=200)
    batch_id = models.CharField(max_length=100, unique=True)
    agent = models.ForeignKey(CallKaroAgent, on_delete=models.CASCADE)
    created_by = models.ForeignKey(TeamMember, on_delete=models.CASCADE)
    total_calls = models.IntegerField(default=0)
    completed_calls = models.IntegerField(default=0)
    status = models.CharField(max_length=50, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Call Karo Campaign"
        verbose_name_plural = "Call Karo Campaigns"
    
    def __str__(self):
        return f"{self.name} - {self.batch_id}"

class CallKaroCallLog(models.Model):
    """Log of calls made through Call Karo AI"""
    CALL_STATUS_CHOICES = [
        ('initiated', 'Initiated'),
        ('ringing', 'Ringing'),
        ('answered', 'Answered'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('missed', 'Missed'),
        ('busy', 'Busy'),
        ('no_answer', 'No Answer'),
    ]
    
    call_id = models.CharField(max_length=100, unique=True)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, null=True, blank=True)
    phone_number = models.CharField(max_length=20)
    agent = models.ForeignKey(CallKaroAgent, on_delete=models.CASCADE)
    campaign = models.ForeignKey(CallKaroCampaign, on_delete=models.SET_NULL, null=True, blank=True)
    initiated_by = models.ForeignKey(TeamMember, on_delete=models.CASCADE)
    
    status = models.CharField(max_length=20, choices=CALL_STATUS_CHOICES, default='initiated')
    duration = models.IntegerField(null=True, blank=True, help_text="Call duration in seconds")
    
    # Metadata passed to Call Karo
    metadata = models.JSONField(default=dict, blank=True)
    
    # Scheduling information
    scheduled_at = models.DateTimeField(null=True, blank=True)
    min_trigger_time = models.TimeField(null=True, blank=True)
    max_trigger_time = models.TimeField(null=True, blank=True)
    carry_over = models.BooleanField(default=False)
    number_of_retries = models.IntegerField(default=0)
    gap_between_retries = models.JSONField(default=list, blank=True)
    priority = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Call Karo Call Log"
        verbose_name_plural = "Call Karo Call Logs"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Call {self.call_id} - {self.phone_number} ({self.status})"
    
    @property
    def duration_formatted(self):
        """Return formatted duration"""
        if self.duration:
            minutes = self.duration // 60
            seconds = self.duration % 60
            return f"{minutes}m {seconds}s"
        return "0s"