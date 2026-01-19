from django.db import models
from django.utils import timezone

class GoogleAdsConfig(models.Model):
    """Configuration for Google Ads API"""
    developer_token = models.CharField(max_length=100, default="Qqs06KvnUON1MNgyVWI0hw")
    access_token = models.TextField(blank=True, null=True)
    refresh_token = models.TextField(blank=True, null=True)
    manager_customer_id = models.CharField(max_length=20, blank=True, null=True)
    client_customer_id = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Google Ads Configuration"
        verbose_name_plural = "Google Ads Configurations"

class GoogleAdsCampaign(models.Model):
    """Google Ads Campaign data"""
    campaign_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=50)
    advertising_channel_type = models.CharField(max_length=50)
    impressions = models.BigIntegerField(default=0)
    clicks = models.BigIntegerField(default=0)
    cost_micros = models.BigIntegerField(default=0)
    last_synced = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def cost_dollars(self):
        return self.cost_micros / 1000000
    
    @property
    def ctr(self):
        if self.impressions > 0:
            return (self.clicks / self.impressions) * 100
        return 0
    
    class Meta:
        verbose_name = "Google Ads Campaign"
        verbose_name_plural = "Google Ads Campaigns"

class GoogleAdsLead(models.Model):
    """Google Ads Lead Form submissions"""
    submission_id = models.CharField(max_length=100, unique=True)
    asset_id = models.CharField(max_length=50, blank=True, null=True)
    campaign_id = models.CharField(max_length=50, blank=True, null=True)
    campaign = models.ForeignKey(GoogleAdsCampaign, on_delete=models.SET_NULL, null=True, blank=True)
    form_submission_date_time = models.DateTimeField()
    
    # Lead data fields
    full_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    
    # Custom fields (JSON)
    custom_fields = models.JSONField(default=dict, blank=True)
    
    # CRM integration
    crm_lead = models.ForeignKey('Lead', on_delete=models.SET_NULL, null=True, blank=True)
    is_synced_to_crm = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Google Ads Lead"
        verbose_name_plural = "Google Ads Leads"

class GoogleAdsPerformance(models.Model):
    """Ad performance metrics"""
    ad_id = models.CharField(max_length=50)
    ad_name = models.CharField(max_length=255, blank=True, null=True)
    campaign_name = models.CharField(max_length=255)
    ad_group_name = models.CharField(max_length=255)
    impressions = models.BigIntegerField(default=0)
    clicks = models.BigIntegerField(default=0)
    cost_micros = models.BigIntegerField(default=0)
    conversions = models.FloatField(default=0)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def cost_dollars(self):
        return self.cost_micros / 1000000
    
    class Meta:
        verbose_name = "Google Ads Performance"
        verbose_name_plural = "Google Ads Performance"
        unique_together = ['ad_id', 'date']