from django.db import models

class BookingSourceCategory(models.Model):
    """Main source categories like Direct, Broker"""
    name = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class BookingSource(models.Model):
    """Specific sources under each category"""
    category = models.ForeignKey(BookingSourceCategory, on_delete=models.CASCADE, related_name='sources')
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.category.name} - {self.name}"
    
    class Meta:
        ordering = ['category__name', 'name']
        unique_together = ['category', 'name']