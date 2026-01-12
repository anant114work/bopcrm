from django.db import models
from django.utils import timezone
from .models import Lead

class LeadJourney(models.Model):
    JOURNEY_TYPES = [
        ('form_submission', 'Form Submission'),
        ('whatsapp_message', 'WhatsApp Message'),
        ('whatsapp_campaign', 'WhatsApp Campaign'),
        ('phone_call', 'Phone Call'),
        ('email_sent', 'Email Sent'),
        ('status_change', 'Status Change'),
        ('assignment', 'Lead Assignment'),
        ('note_added', 'Note Added'),
    ]
    
    SOURCE_TYPES = [
        ('meta', 'Meta Leads'),
        ('google', 'Google Leads'),
        ('ivr', 'IVR Calls'),
        ('manual', 'Manual Entry'),
    ]
    
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='journey')
    journey_type = models.CharField(max_length=50, choices=JOURNEY_TYPES)
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES, default='manual')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.lead.full_name} - {self.get_journey_type_display()}"

class DuplicatePhoneTracker(models.Model):
    phone_number = models.CharField(max_length=20, unique=True)
    meta_leads = models.ManyToManyField(Lead, related_name='meta_duplicates', blank=True)
    google_leads = models.ManyToManyField('Lead', related_name='google_duplicates', blank=True)
    ivr_calls = models.JSONField(default=list, blank=True)  # Store IVR call data
    first_seen = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    @property
    def total_occurrences(self):
        return self.meta_leads.count() + self.google_leads.count() + len(self.ivr_calls)
    
    @property
    def sources(self):
        sources = []
        if self.meta_leads.exists():
            sources.append('Meta')
        if self.google_leads.exists():
            sources.append('Google')
        if self.ivr_calls:
            sources.append('IVR')
        return sources
    
    def __str__(self):
        return f"{self.phone_number} ({self.total_occurrences} occurrences)"