from django.db import models

class IntegrationConfig(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class MetaConfig(IntegrationConfig):
    page_id = models.CharField(max_length=100)
    access_token = models.TextField()
    app_id = models.CharField(max_length=100, blank=True)
    app_secret = models.CharField(max_length=200, blank=True)
    user_access_token = models.TextField(blank=True)
    
    def __str__(self):
        return f"Meta Config - Page {self.page_id}"

class GoogleSheetsConfig(IntegrationConfig):
    sheet_url = models.URLField()
    sheet_name = models.CharField(max_length=100, default='Sheet1')
    service_account_json = models.TextField(blank=True)
    
    def __str__(self):
        return f"Google Sheets - {self.name}"