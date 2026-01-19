from django.db import models
from leads.models import Lead

class TataCall(models.Model):
    call_id = models.CharField(max_length=100, unique=True)
    uuid = models.CharField(max_length=100, blank=True)
    lead = models.ForeignKey(Lead, on_delete=models.SET_NULL, null=True, blank=True)
    customer_number = models.CharField(max_length=20)
    agent_number = models.CharField(max_length=20, blank=True)
    agent_name = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)
    direction = models.CharField(max_length=20, default='inbound')
    status = models.CharField(max_length=20, default='received')
    start_stamp = models.DateTimeField()
    end_stamp = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField(default=0)
    recording_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

class CallNote(models.Model):
    call = models.ForeignKey(TataCall, on_delete=models.CASCADE, related_name='notes')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class TataDepartment(models.Model):
    dept_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    ring_strategy = models.CharField(max_length=50, blank=True)
    agent_count = models.IntegerField(default=0)
    calls_answered = models.IntegerField(default=0)
    calls_missed = models.IntegerField(default=0)
    use_as_queue = models.BooleanField(default=False)
    queue_timeout = models.IntegerField(default=90)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class TataAgent(models.Model):
    agent_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    extension_id = models.CharField(max_length=50, blank=True)
    department = models.ForeignKey(TataDepartment, on_delete=models.SET_NULL, null=True, blank=True)
    timeout = models.IntegerField(default=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class TataRecording(models.Model):
    recording_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    url = models.URLField()
    music_on_hold = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)