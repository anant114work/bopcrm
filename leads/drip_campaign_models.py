from django.db import models
from django.utils import timezone
from datetime import timedelta
from .project_models import Project

class DripCampaign(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('draft', 'Draft'),
    ]
    
    name = models.CharField(max_length=200)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='drip_campaigns')
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Campaign variant support
    variant_group = models.CharField(max_length=100, blank=True, help_text="Group ID for campaign variants (e.g., 'spjday')")
    is_active_variant = models.BooleanField(default=True, help_text="Whether this variant is currently active for new subscribers")
    
    # Analytics
    total_subscribers = models.IntegerField(default=0)
    total_messages_sent = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.name} - {self.project.name}"
    
    class Meta:
        ordering = ['-created_at']

class DripMessage(models.Model):
    campaign = models.ForeignKey(DripCampaign, on_delete=models.CASCADE, related_name='messages')
    day_number = models.IntegerField(help_text="Day number in the sequence (1, 2, 3, etc.)")
    template_name = models.CharField(max_length=100, help_text="AI Sensy template name")
    campaign_name = models.CharField(max_length=100, help_text="AI Sensy campaign name")
    message_text = models.TextField()
    api_key = models.TextField()
    
    # Template parameters
    template_params = models.JSONField(default=list, help_text="Template parameters for AI Sensy")
    fallback_params = models.JSONField(default=dict, help_text="Fallback parameter values")
    
    # Timing
    delay_hours = models.IntegerField(default=24, help_text="Hours to wait before sending this message")
    delay_minutes = models.IntegerField(default=0, help_text="Additional minutes to wait")
    
    @property
    def total_delay_minutes(self):
        return (self.delay_hours * 60) + self.delay_minutes
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Analytics
    sent_count = models.IntegerField(default=0)
    delivered_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    
    def __str__(self):
        return f"Day {self.day_number}: {self.template_name}"
    
    class Meta:
        ordering = ['day_number']
        unique_together = ['campaign', 'day_number']

class DripSubscriber(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('unsubscribed', 'Unsubscribed'),
    ]
    
    campaign = models.ForeignKey(DripCampaign, on_delete=models.CASCADE, related_name='subscribers')
    lead = models.ForeignKey('Lead', on_delete=models.CASCADE, related_name='drip_subscriptions')
    phone_number = models.CharField(max_length=20)
    first_name = models.CharField(max_length=100, blank=True)
    
    # Subscription details
    subscribed_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    current_day = models.IntegerField(default=0, help_text="Current day in the sequence")
    next_message_at = models.DateTimeField(null=True, blank=True)
    
    # Completion tracking
    completed_at = models.DateTimeField(null=True, blank=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.first_name} ({self.phone_number}) - Day {self.current_day}"
    
    def get_next_message(self):
        """Get the next message to send"""
        next_day = self.current_day + 1
        return self.campaign.messages.filter(day_number=next_day, is_active=True).first()
    
    def schedule_next_message(self):
        """Schedule the next message"""
        next_message = self.get_next_message()
        if next_message:
            self.next_message_at = timezone.now() + timedelta(minutes=next_message.total_delay_minutes)
            self.save()
            return True
        else:
            # No more messages, mark as completed
            self.status = 'completed'
            self.completed_at = timezone.now()
            self.next_message_at = None
            self.save()
            return False
    
    class Meta:
        ordering = ['-subscribed_at']
        unique_together = ['campaign', 'lead']

class DripMessageLog(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('read', 'Read'),
    ]
    
    subscriber = models.ForeignKey(DripSubscriber, on_delete=models.CASCADE, related_name='message_logs')
    drip_message = models.ForeignKey(DripMessage, on_delete=models.CASCADE, related_name='logs')
    
    # Message details
    phone_number = models.CharField(max_length=20)
    recipient_name = models.CharField(max_length=100, blank=True)
    final_message_text = models.TextField()
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    scheduled_at = models.DateTimeField()
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    
    # API response
    api_response = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Day {self.drip_message.day_number} to {self.recipient_name} - {self.status}"
    
    class Meta:
        ordering = ['-created_at']