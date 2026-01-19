from django.db import models
from .project_models import Project
from .whatsapp_models import WhatsAppTemplate

class AutoWhatsAppCampaign(models.Model):
    """Automatic WhatsApp campaign that triggers on new leads"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='auto_whatsapp_campaigns')
    template = models.ForeignKey(WhatsAppTemplate, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    delay_minutes = models.IntegerField(default=0, help_text="Delay in minutes before sending (0 = immediate)")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.project.name} - {self.template.name} (Auto)"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Auto WhatsApp Campaign'
        verbose_name_plural = 'Auto WhatsApp Campaigns'
