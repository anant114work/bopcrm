from django.db import models

class Project(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    developer = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    status = models.CharField(max_length=20, default='Active')
    description = models.TextField(blank=True, help_text="Project description and details")
    amenities = models.JSONField(default=list, blank=True, help_text="List of amenities available")
    form_keywords = models.JSONField(default=list)  # Keywords to match form names
    brochure = models.FileField(upload_to='project_brochures/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.developer}"
    
    @property
    def amenities_display(self):
        """Return amenities as comma-separated string"""
        if isinstance(self.amenities, list):
            return ", ".join(self.amenities)
        return self.amenities or ""
    
    @property
    def lead_count(self):
        from .models import Lead
        keywords = self.form_keywords
        if not keywords:
            return 0
        
        leads = Lead.objects.none()
        for keyword in keywords:
            leads = leads | Lead.objects.filter(form_name__icontains=keyword)
        return leads.distinct().count()
    
    def get_leads(self):
        from .models import Lead
        from .form_mapping_models import FormSourceMapping
        
        # Get leads from form mappings first
        mapped_forms = FormSourceMapping.objects.filter(
            project=self,
            is_active=True
        ).values_list('form_name', flat=True)
        
        leads = Lead.objects.none()
        
        # Add leads from mapped forms
        if mapped_forms:
            for form_name in mapped_forms:
                leads = leads | Lead.objects.filter(form_name__icontains=form_name)
        
        # Fallback to keyword matching
        keywords = self.form_keywords
        if keywords:
            for keyword in keywords:
                leads = leads | Lead.objects.filter(form_name__icontains=keyword)
        
        return leads.distinct().order_by('-created_time')
    
    class Meta:
        ordering = ['name']