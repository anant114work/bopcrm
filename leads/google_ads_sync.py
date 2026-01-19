from django.utils import timezone
from .google_ads_client import GoogleAdsClient
from .google_ads_models import GoogleAdsConfig, GoogleAdsCampaign, GoogleAdsLead, GoogleAdsPerformance
from .models import Lead
import logging

logger = logging.getLogger(__name__)

class GoogleAdsSyncService:
    def __init__(self):
        self.client = GoogleAdsClient()
        self.config = None
        self._load_config()
    
    def _load_config(self):
        """Load Google Ads configuration"""
        try:
            self.config = GoogleAdsConfig.objects.filter(is_active=True).first()
            if self.config:
                self.client.set_credentials(
                    self.config.access_token,
                    self.config.manager_customer_id,
                    self.config.client_customer_id
                )
        except Exception as e:
            logger.error(f"Error loading Google Ads config: {e}")
    
    def sync_campaigns(self):
        """Sync campaigns from Google Ads"""
        if not self.config or not self.config.access_token:
            logger.error("Google Ads not configured")
            return False
        
        try:
            campaigns_data = self.client.get_campaigns()
            synced_count = 0
            
            for campaign_data in campaigns_data:
                campaign_info = campaign_data.get('campaign', {})
                metrics = campaign_data.get('metrics', {})
                
                campaign, created = GoogleAdsCampaign.objects.update_or_create(
                    campaign_id=campaign_info.get('id'),
                    defaults={
                        'name': campaign_info.get('name', ''),
                        'status': campaign_info.get('status', ''),
                        'advertising_channel_type': campaign_info.get('advertisingChannelType', ''),
                        'impressions': metrics.get('impressions', 0),
                        'clicks': metrics.get('clicks', 0),
                        'cost_micros': metrics.get('costMicros', 0),
                    }
                )
                synced_count += 1
            
            logger.info(f"Synced {synced_count} campaigns from Google Ads")
            return True
            
        except Exception as e:
            logger.error(f"Error syncing campaigns: {e}")
            return False
    
    def sync_leads(self, days_back=7):
        """Sync leads from Google Ads lead forms"""
        if not self.config or not self.config.access_token:
            logger.error("Google Ads not configured")
            return False
        
        try:
            leads_data = self.client.get_leads_from_forms(days_back)
            synced_count = 0
            
            for lead_data in leads_data:
                submission_data = lead_data.get('leadFormSubmissionData', {})
                
                # Extract lead information
                submission_id = submission_data.get('id')
                if not submission_id:
                    continue
                
                # Parse custom fields for contact info
                custom_fields = submission_data.get('customLeadFormSubmissionFields', [])
                lead_info = self._parse_lead_fields(custom_fields)
                
                # Create or update Google Ads lead
                google_lead, created = GoogleAdsLead.objects.update_or_create(
                    submission_id=submission_id,
                    defaults={
                        'asset_id': submission_data.get('assetId'),
                        'campaign_id': submission_data.get('campaignId'),
                        'form_submission_date_time': submission_data.get('formSubmissionDateTime'),
                        'full_name': lead_info.get('name', ''),
                        'email': lead_info.get('email', ''),
                        'phone_number': lead_info.get('phone', ''),
                        'company': lead_info.get('company', ''),
                        'custom_fields': dict(custom_fields) if custom_fields else {}
                    }
                )
                
                # Sync to CRM if not already synced
                if created and not google_lead.is_synced_to_crm:
                    self._sync_to_crm(google_lead)
                
                synced_count += 1
            
            logger.info(f"Synced {synced_count} leads from Google Ads")
            return True
            
        except Exception as e:
            logger.error(f"Error syncing leads: {e}")
            return False
    
    def _parse_lead_fields(self, custom_fields):
        """Parse custom lead form fields"""
        lead_info = {}
        
        for field in custom_fields:
            field_name = field.get('fieldName', '').lower()
            field_value = field.get('fieldValue', '')
            
            if 'name' in field_name or 'full_name' in field_name:
                lead_info['name'] = field_value
            elif 'email' in field_name:
                lead_info['email'] = field_value
            elif 'phone' in field_name or 'mobile' in field_name:
                lead_info['phone'] = field_value
            elif 'company' in field_name:
                lead_info['company'] = field_value
        
        return lead_info
    
    def _sync_to_crm(self, google_lead):
        """Sync Google Ads lead to CRM"""
        try:
            # Check if lead already exists in CRM
            existing_lead = None
            if google_lead.email:
                existing_lead = Lead.objects.filter(email=google_lead.email).first()
            elif google_lead.phone_number:
                existing_lead = Lead.objects.filter(phone_number=google_lead.phone_number).first()
            
            if existing_lead:
                # Update existing lead
                google_lead.crm_lead = existing_lead
                google_lead.is_synced_to_crm = True
                google_lead.save()
            else:
                # Create new CRM lead
                crm_lead = Lead.objects.create(
                    lead_id=f"gads_{google_lead.submission_id}",
                    full_name=google_lead.full_name or '',
                    email=google_lead.email or '',
                    phone_number=google_lead.phone_number or '',
                    source='Google Ads',
                    form_name='Google Ads Lead Form',
                    created_time=google_lead.form_submission_date_time,
                    campaign_id=google_lead.campaign_id or '',
                )
                
                google_lead.crm_lead = crm_lead
                google_lead.is_synced_to_crm = True
                google_lead.save()
                
                logger.info(f"Created CRM lead from Google Ads: {crm_lead.id}")
                
        except Exception as e:
            logger.error(f"Error syncing Google Ads lead to CRM: {e}")
    
    def sync_performance(self, days_back=7):
        """Sync ad performance data"""
        if not self.config or not self.config.access_token:
            logger.error("Google Ads not configured")
            return False
        
        try:
            performance_data = self.client.get_ad_performance(days_back)
            synced_count = 0
            
            for perf_data in performance_data:
                ad_info = perf_data.get('adGroupAd', {}).get('ad', {})
                campaign_info = perf_data.get('campaign', {})
                ad_group_info = perf_data.get('adGroup', {})
                metrics = perf_data.get('metrics', {})
                segments = perf_data.get('segments', {})
                
                GoogleAdsPerformance.objects.update_or_create(
                    ad_id=ad_info.get('id'),
                    date=segments.get('date'),
                    defaults={
                        'ad_name': ad_info.get('name', ''),
                        'campaign_name': campaign_info.get('name', ''),
                        'ad_group_name': ad_group_info.get('name', ''),
                        'impressions': metrics.get('impressions', 0),
                        'clicks': metrics.get('clicks', 0),
                        'cost_micros': metrics.get('costMicros', 0),
                        'conversions': metrics.get('conversions', 0),
                    }
                )
                synced_count += 1
            
            logger.info(f"Synced {synced_count} performance records from Google Ads")
            return True
            
        except Exception as e:
            logger.error(f"Error syncing performance data: {e}")
            return False
    
    def full_sync(self):
        """Perform full sync of campaigns, leads, and performance"""
        results = {
            'campaigns': self.sync_campaigns(),
            'leads': self.sync_leads(),
            'performance': self.sync_performance()
        }
        return results