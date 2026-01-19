from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .project_models import Project
from .project_image_models import ProjectImage
from .whatsapp_models import WhatsAppTemplate, WhatsAppCampaign, WhatsAppMessage, TestMessage
from .drip_campaign_models import DripCampaign, DripMessage, DripSubscriber, DripMessageLog
from .acefone_models import AcefoneConfig, DIDNumber
from .integration_models import MetaConfig, GoogleSheetsConfig
from .sync_log_models import SyncLog
from .booking_models import UnitedNetworkBooking
from .form_mapping_models import FormSourceMapping
from .auto_whatsapp_models import AutoWhatsAppCampaign
from .bulk_call_models import BulkCallCampaign, BulkCallRecord
from .call_report_models import CallReportUpload, CallReportRecord
from .booking_source_models import BookingSourceCategory, BookingSource

STAGE_CHOICES = [
    ('new', 'New'),
    ('contacted', 'Contacted'),
    ('interested', 'Interested'),
    ('not_interested', 'Not Interested'),
    ('site_visit', 'Site Visit'),
    ('hot', 'Hot'),
    ('warm', 'Warm'),
    ('cold', 'Cold'),
    ('dead', 'Dead'),
    ('converted', 'Converted'),
]

class Lead(models.Model):
    lead_id = models.CharField(max_length=100, unique=True)
    meta_lead_id = models.CharField(max_length=100, blank=True, null=True)
    created_time = models.DateTimeField()
    email = models.EmailField(blank=True)
    full_name = models.CharField(max_length=200, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    form_name = models.CharField(max_length=200)
    city = models.CharField(max_length=100, blank=True)
    budget = models.CharField(max_length=200, blank=True)
    configuration = models.CharField(max_length=100, blank=True)
    preferred_time = models.CharField(max_length=100, blank=True)
    extra_fields = models.JSONField(default=dict, blank=True)
    synced_at = models.DateTimeField(auto_now_add=True)
    stage = models.CharField(max_length=50, choices=STAGE_CHOICES, default='new')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_leads')
    source = models.CharField(max_length=50, default='Meta')
    campaign_id = models.CharField(max_length=100, blank=True)
    adset_id = models.CharField(max_length=100, blank=True)
    ad_id = models.CharField(max_length=100, blank=True)
    form_id = models.CharField(max_length=100, blank=True)
    campaign_spend = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    adset_spend = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ad_spend = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ever_interested = models.BooleanField(default=False)  # Track if lead was ever interested
    
    def __str__(self):
        return f"{self.full_name} - {self.email}"
    
    @property
    def assigned_to(self):
        try:
            return self.assignment.assigned_to
        except:
            return None
    
    @property
    def is_overdue(self):
        try:
            return self.assignment.is_overdue
        except:
            return False
    
    @property
    def interest_percentage(self):
        """Calculate interest conversion percentage"""
        total_leads = Lead.objects.count()
        interested_leads = Lead.objects.filter(ever_interested=True).count()
        return round((interested_leads / total_leads * 100) if total_leads > 0 else 0, 1)
    
    class Meta:
        ordering = ['-created_time']

class GoogleSheet(models.Model):
    name = models.CharField(max_length=200)
    sheet_url = models.URLField()
    sheet_name = models.CharField(max_length=100, default='Sheet1')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_synced = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']

class ScheduledMessage(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE)
    template_name = models.CharField(max_length=100)
    scheduled_time = models.DateTimeField()
    delay_hours = models.IntegerField()
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    error_message = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.lead.full_name} - {self.template_name} - {self.scheduled_time}"
    
    class Meta:
        ordering = ['scheduled_time']

class SourceMapping(models.Model):
    source_name = models.CharField(max_length=200, unique=True)
    project_name = models.CharField(max_length=200)
    location = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.source_name} -> {self.project_name}, {self.location}"
    
    class Meta:
        ordering = ['source_name']

class ZohoConfig(models.Model):
    client_id = models.CharField(max_length=200)
    client_secret = models.CharField(max_length=200)
    redirect_uri = models.URLField()
    access_token = models.TextField(blank=True)
    refresh_token = models.TextField(blank=True)
    api_domain = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Zoho Config - {self.client_id[:10]}..."
    
    class Meta:
        ordering = ['-created_at']

class Property(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.location}"
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Properties'

class TeamMember(models.Model):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Sales Director - T1', 'Sales Director - T1'),
        ('TEAM Head - T2', 'TEAM Head - T2'),
        ('Team leader - t3', 'Team leader - t3'),
        ('Sales Manager - T4', 'Sales Manager - T4'),
        ('Sales Executive - T5', 'Sales Executive - T5'),
        ('Telecaller - T6', 'Telecaller - T6'),
        ('BROKER', 'BROKER'),
        ('Commercial', 'Commercial'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='team_member')
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    parent_user = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='team_members')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.role}"
    
    def get_all_team_members(self):
        """Get all team members under this user (including self)"""
        team_members = [self]
        
        def get_children_recursive(parent):
            children = TeamMember.objects.filter(parent_user=parent, is_active=True)
            for child in children:
                team_members.append(child)
                get_children_recursive(child)
        
        get_children_recursive(self)
        return team_members
    
    class Meta:
        ordering = ['name']

class LeadStage(models.Model):
    name = models.CharField(max_length=50, choices=STAGE_CHOICES, unique=True)
    color = models.CharField(max_length=7, default='#6b7280')  # Hex color
    
    def __str__(self):
        return self.get_name_display()

class LeadAssignment(models.Model):
    lead = models.OneToOneField('Lead', on_delete=models.CASCADE, related_name='assignment')
    assigned_to = models.ForeignKey(TeamMember, on_delete=models.CASCADE, related_name='assigned_leads')
    assigned_at = models.DateTimeField(auto_now_add=True)
    sla_deadline = models.DateTimeField()
    is_attended = models.BooleanField(default=False)
    attended_at = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.sla_deadline:
            self.sla_deadline = timezone.now() + timedelta(minutes=30)
        super().save(*args, **kwargs)
    
    @property
    def is_overdue(self):
        return not self.is_attended and timezone.now() > self.sla_deadline
    
    def __str__(self):
        return f"{self.lead.full_name} -> {self.assigned_to.name}"

class LeadNote(models.Model):
    lead = models.ForeignKey('Lead', on_delete=models.CASCADE, related_name='notes')
    team_member = models.ForeignKey(TeamMember, on_delete=models.CASCADE)
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.lead.full_name} - {self.team_member.name}"
    
    class Meta:
        ordering = ['-created_at']

class LeadReassignmentLog(models.Model):
    lead = models.ForeignKey('Lead', on_delete=models.CASCADE, related_name='reassignment_logs')
    previous_assignee = models.ForeignKey(TeamMember, on_delete=models.SET_NULL, null=True, related_name='previous_assignments')
    new_assignee = models.ForeignKey(TeamMember, on_delete=models.SET_NULL, null=True, related_name='new_assignments')
    reassigned_by = models.ForeignKey(TeamMember, on_delete=models.SET_NULL, null=True, related_name='performed_reassignments')
    timestamp = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.lead.full_name}: {self.previous_assignee} -> {self.new_assignee}"
    
    class Meta:
        ordering = ['-timestamp']

class LeadViewActivity(models.Model):
    lead = models.ForeignKey('Lead', on_delete=models.CASCADE, related_name='view_activities')
    viewed_by = models.ForeignKey(TeamMember, on_delete=models.CASCADE, related_name='lead_views')
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.lead.full_name} viewed by {self.viewed_by.name}"
    
    class Meta:
        ordering = ['-timestamp']

class LeadTag(models.Model):
    lead = models.ForeignKey('Lead', on_delete=models.CASCADE, related_name='tags')
    tag = models.CharField(max_length=50)
    confidence = models.FloatField(default=0.8)  # AI confidence score
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['lead', 'tag']
        ordering = ['-confidence', '-created_at']
    
    def __str__(self):
        return f"{self.lead.full_name} - {self.tag}"

class LeadRating(models.Model):
    lead = models.OneToOneField('Lead', on_delete=models.CASCADE, related_name='ai_rating')
    score = models.IntegerField(default=5)  # 1-10 scale
    priority = models.CharField(max_length=10, choices=[
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low')
    ], default='medium')
    reason = models.TextField(blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.lead.full_name} - Score: {self.score}"

class LeadInterestLog(models.Model):
    lead = models.ForeignKey('Lead', on_delete=models.CASCADE, related_name='interest_logs')
    marked_interested_at = models.DateTimeField(auto_now_add=True)
    marked_by = models.ForeignKey(TeamMember, on_delete=models.SET_NULL, null=True)
    stage_at_time = models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.lead.full_name} - Interested on {self.marked_interested_at.date()}"
    
    class Meta:
        ordering = ['-marked_interested_at']

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
class ScheduledCall(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE)
    team_member = models.ForeignKey(TeamMember, on_delete=models.CASCADE)
    scheduled_datetime = models.DateTimeField()
    phone_number = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    executed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['scheduled_datetime']

class CallLog(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE)
    team_member = models.ForeignKey(TeamMember, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)
    call_type = models.CharField(max_length=20, choices=[
        ('manual', 'Manual'),
        ('scheduled', 'Scheduled'),
        ('bulk', 'Bulk'),
        ('auto_daily', 'Auto Daily')
    ])
    status = models.CharField(max_length=20, choices=[
        ('initiated', 'Initiated'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ])
    initiated_at = models.DateTimeField(auto_now_add=True)
    call_sid = models.CharField(max_length=100, blank=True)
    
    class Meta:
        ordering = ['-initiated_at']