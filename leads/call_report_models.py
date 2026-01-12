from django.db import models
from django.utils import timezone

class CallReportUpload(models.Model):
    """Model to track call report uploads"""
    uploaded_at = models.DateTimeField(auto_now_add=True)
    filename = models.CharField(max_length=255)
    total_records = models.IntegerField(default=0)
    matched_records = models.IntegerField(default=0)
    unmatched_records = models.IntegerField(default=0)
    uploaded_by = models.CharField(max_length=100, default='Admin')
    
    def __str__(self):
        return f"Call Report - {self.filename} ({self.uploaded_at.date()})"
    
    class Meta:
        ordering = ['-uploaded_at']

class CallReportRecord(models.Model):
    """Model to store individual call report records"""
    upload = models.ForeignKey(CallReportUpload, on_delete=models.CASCADE, related_name='records')
    phone_number = models.CharField(max_length=20)
    agent = models.CharField(max_length=100, blank=True)
    version = models.CharField(max_length=10, blank=True)
    call_date = models.DateField(null=True, blank=True)
    call_time = models.DateTimeField(null=True, blank=True)
    disposition = models.TextField(blank=True)
    call_duration = models.FloatField(null=True, blank=True)
    call_recording = models.URLField(blank=True)
    try_count = models.IntegerField(default=0)
    hangup_reason = models.CharField(max_length=100, blank=True)
    cost = models.FloatField(null=True, blank=True)
    source = models.CharField(max_length=100, blank=True)
    project = models.CharField(max_length=200, blank=True)
    campaign_type = models.CharField(max_length=100, blank=True)
    lead_source = models.CharField(max_length=50, blank=True)
    conversion_status = models.CharField(max_length=10, blank=True)
    disposition_reason = models.TextField(blank=True)
    x_model_used = models.CharField(max_length=50, blank=True)
    variable_name = models.CharField(max_length=100, blank=True)
    
    # Matching fields
    matched_lead = models.ForeignKey('Lead', on_delete=models.SET_NULL, null=True, blank=True)
    matched_call_log = models.ForeignKey('CallLog', on_delete=models.SET_NULL, null=True, blank=True)
    is_matched = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.phone_number} - {self.disposition[:50]}"
    
    class Meta:
        ordering = ['-call_time']