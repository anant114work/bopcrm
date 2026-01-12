from django.db import models
from django.utils import timezone

class SyncLog(models.Model):
    SYNC_TYPES = [
        ('meta', 'Meta'),
        ('google', 'Google Sheets'),
    ]
    
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('error', 'Error'),
        ('partial', 'Partial Success'),
    ]
    
    sync_type = models.CharField(max_length=10, choices=SYNC_TYPES)
    config_name = models.CharField(max_length=200)
    config_id = models.IntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    leads_synced = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.sync_type} - {self.config_name} - {self.status}"
    
    class Meta:
        ordering = ['-started_at']