from django.db import models
from .models import Lead

class LeadRating(models.Model):
    lead = models.OneToOneField(Lead, on_delete=models.CASCADE, related_name='ai_rating')
    score = models.IntegerField(default=5)  # 1-10 scale
    priority = models.CharField(max_length=10, choices=[
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low')
    ], default='medium')
    reason = models.TextField(blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'leads_leadrating'
    
    def __str__(self):
        return f"{self.lead.full_name} - Score: {self.score}"