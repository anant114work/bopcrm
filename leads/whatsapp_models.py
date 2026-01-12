from django.db import models
from django.utils import timezone
from .project_models import Project

class WhatsAppTemplate(models.Model):
    TEMPLATE_TYPES = [
        ('TEXT', 'Text'),
        ('IMAGE', 'Image'),
        ('DOCUMENT', 'Document'),
    ]
    
    CATEGORY_CHOICES = [
        ('welcome', 'Welcome'),
        ('followup', 'Follow-up'),
        ('promotional', 'Promotional'),
        ('reminder', 'Reminder'),
        ('custom', 'Custom'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='whatsapp_templates')
    name = models.CharField(max_length=100)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES, default='TEXT')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='custom')
    message_text = models.TextField()
    api_key = models.TextField()
    campaign_name = models.CharField(max_length=100)
    is_drip_message = models.BooleanField(default=False)
    drip_delay_minutes = models.IntegerField(default=30)
    order = models.IntegerField(default=1)
    media_file = models.FileField(upload_to='whatsapp_media/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Analytics fields
    sent_count = models.IntegerField(default=0)
    delivered_count = models.IntegerField(default=0)
    read_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['project', 'order']
    
    def __str__(self):
        return f"{self.project.name} - {self.name}"
    
    def get_random_project_image(self):
        """Get a random image from project images"""
        images = self.project.images.all()
        if images:
            import random
            return random.choice(images).image.url
        return None
    
    @property
    def delivery_rate(self):
        if self.sent_count == 0:
            return 0
        return (self.delivered_count / self.sent_count) * 100
    
    @property
    def read_rate(self):
        if self.delivered_count == 0:
            return 0
        return (self.read_count / self.delivered_count) * 100

class WhatsAppCampaign(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('paused', 'Paused'),
        ('cancelled', 'Cancelled'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='whatsapp_campaigns')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    template = models.ForeignKey(WhatsAppTemplate, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    scheduled_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Target criteria
    target_all_leads = models.BooleanField(default=True)
    target_stages = models.JSONField(default=list, blank=True)
    target_date_range = models.JSONField(default=dict, blank=True)
    
    # Analytics
    total_leads = models.IntegerField(default=0)
    messages_sent = models.IntegerField(default=0)
    messages_delivered = models.IntegerField(default=0)
    messages_failed = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.project.name} - {self.name}"
    
    @property
    def success_rate(self):
        if self.messages_sent == 0:
            return 0
        return (self.messages_delivered / self.messages_sent) * 100

class WhatsAppMessage(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('failed', 'Failed'),
    ]
    
    campaign = models.ForeignKey(WhatsAppCampaign, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    template = models.ForeignKey(WhatsAppTemplate, on_delete=models.CASCADE)
    lead = models.ForeignKey('Lead', on_delete=models.CASCADE, null=True, blank=True)
    phone_number = models.CharField(max_length=20)
    recipient_name = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_test_message = models.BooleanField(default=False)
    
    # Message content
    final_message_text = models.TextField()
    media_url = models.URLField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # API response
    api_response = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.phone_number} - {self.template.name} - {self.status}"

class TestMessage(models.Model):
    template = models.ForeignKey(WhatsAppTemplate, on_delete=models.CASCADE)
    test_phone_number = models.CharField(max_length=20)
    test_name = models.CharField(max_length=200, default='Test User')
    message = models.OneToOneField(WhatsAppMessage, on_delete=models.CASCADE, related_name='test_info')
    created_by = models.CharField(max_length=100, default='System')
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-message__created_at']
    
    def __str__(self):
        return f"Test: {self.template.name} -> {self.test_phone_number}"