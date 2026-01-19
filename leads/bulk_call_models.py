from django.db import models
from django.utils import timezone

class BulkCallCampaign(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('paused', 'Paused'),
    ]
    
    name = models.CharField(max_length=200)
    file_name = models.CharField(max_length=200)
    agent_id = models.CharField(max_length=100, blank=True)
    total_numbers = models.IntegerField(default=0)
    completed_calls = models.IntegerField(default=0)
    successful_calls = models.IntegerField(default=0)
    failed_calls = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.status})"
    
    class Meta:
        ordering = ['-created_at']

class BulkCallRecord(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('calling', 'Calling'),
        ('connected', 'Connected'),
        ('failed', 'Failed'),
        ('no_answer', 'No Answer'),
        ('busy', 'Busy'),
        ('skipped', 'Skipped (Duplicate)'),
    ]
    
    campaign = models.ForeignKey(BulkCallCampaign, on_delete=models.CASCADE, related_name='call_records')
    name = models.CharField(max_length=200, blank=True)
    phone_number = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    call_id = models.CharField(max_length=100, blank=True)
    initiated_at = models.DateTimeField(null=True, blank=True)
    connected_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    api_response = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return f"{self.name} - {self.phone_number} ({self.status})"
    
    class Meta:
        ordering = ['id']