from django.db import models
from .project_models import Project

class FormSourceMapping(models.Model):
    """Maps lead form sources to projects"""
    form_name = models.CharField(max_length=200, unique=True, help_text="Exact form name or keyword from Meta/source")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='form_mappings')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.form_name} → {self.project.name}"
    
    class Meta:
        ordering = ['form_name']
        verbose_name = 'Form Source Mapping'
        verbose_name_plural = 'Form Source Mappings'
