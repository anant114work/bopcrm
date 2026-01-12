from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.utils import timezone
from .google_ads_models import GoogleAdsConfig, GoogleAdsCampaign, GoogleAdsLead, GoogleAdsPerformance
from .google_ads_sync import GoogleAdsSyncService
from .google_ads_client import GoogleAdsClient
import json

def google_ads_dashboard(request):
    """Google Ads dashboard view"""
    config = GoogleAdsConfig.objects.filter(is_active=True).first()
    campaigns = GoogleAdsCampaign.objects.all()[:10]
    recent_leads = GoogleAdsLead.objects.order_by('-form_submission_date_time')[:10]
    
    # Performance summary
    total_campaigns = GoogleAdsCampaign.objects.count()
    total_leads = GoogleAdsLead.objects.count()
    total_cost = sum(c.cost_dollars for c in campaigns)
    total_clicks = sum(c.clicks for c in campaigns)
    
    context = {
        'config': config,
        'campaigns': campaigns,
        'recent_leads': recent_leads,
        'stats': {
            'total_campaigns': total_campaigns,
            'total_leads': total_leads,
            'total_cost': total_cost,
            'total_clicks': total_clicks,
        }
    }
    return render(request, 'leads/google_ads_dashboard.html', context)

def google_ads_config(request):
    """Configure Google Ads API settings"""
    config = GoogleAdsConfig.objects.filter(is_active=True).first()
    
    if request.method == 'POST':
        access_token = request.POST.get('access_token')
        manager_customer_id = request.POST.get('manager_customer_id')
        client_customer_id = request.POST.get('client_customer_id')
        
        if config:
            config.access_token = access_token
            config.manager_customer_id = manager_customer_id
            config.client_customer_id = client_customer_id
            config.is_active = True
            config.save()
        else:
            config = GoogleAdsConfig.objects.create(
                access_token=access_token,
                manager_customer_id=manager_customer_id,
                client_customer_id=client_customer_id,
                is_active=True
            )
        
        messages.success(request, 'Google Ads configuration saved successfully!')
        return redirect('google_ads_dashboard')
    
    # Test connection if config exists
    connection_status = False
    accessible_customers = []
    
    if config and config.access_token:
        try:
            client = GoogleAdsClient()
            client.set_credentials(
                config.access_token,
                config.manager_customer_id,
                config.client_customer_id
            )
            accessible_customers = client.get_accessible_customers()
            connection_status = len(accessible_customers) > 0
        except:
            connection_status = False
    
    context = {
        'config': config,
        'connection_status': connection_status,
        'accessible_customers': accessible_customers,
        'developer_token': 'Qqs06KvnUON1MNgyVWI0hw'
    }
    return render(request, 'leads/google_ads_config.html', context)

@csrf_exempt
def sync_google_ads(request):
    """Manual sync from Google Ads"""
    if request.method == 'POST':
        sync_service = GoogleAdsSyncService()
        
        sync_type = request.POST.get('sync_type', 'full')
        
        if sync_type == 'campaigns':
            result = sync_service.sync_campaigns()
            message = 'Campaigns synced successfully!' if result else 'Failed to sync campaigns'
        elif sync_type == 'leads':
            result = sync_service.sync_leads()
            message = 'Leads synced successfully!' if result else 'Failed to sync leads'
        elif sync_type == 'performance':
            result = sync_service.sync_performance()
            message = 'Performance data synced successfully!' if result else 'Failed to sync performance'
        else:
            results = sync_service.full_sync()
            success_count = sum(1 for r in results.values() if r)
            message = f'Sync completed: {success_count}/3 successful'
            result = success_count > 0
        
        return JsonResponse({
            'success': result,
            'message': message
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def google_ads_campaigns(request):
    """View Google Ads campaigns"""
    campaigns = GoogleAdsCampaign.objects.all().order_by('-last_synced')
    
    context = {
        'campaigns': campaigns,
        'total_cost': sum(c.cost_dollars for c in campaigns),
        'total_clicks': sum(c.clicks for c in campaigns),
        'total_impressions': sum(c.impressions for c in campaigns),
    }
    return render(request, 'leads/google_ads_campaigns.html', context)

def google_ads_leads(request):
    """View Google Ads leads"""
    leads = GoogleAdsLead.objects.all().order_by('-form_submission_date_time')
    
    # Filter options
    campaign_id = request.GET.get('campaign')
    synced_only = request.GET.get('synced') == 'true'
    
    if campaign_id:
        leads = leads.filter(campaign_id=campaign_id)
    
    if synced_only:
        leads = leads.filter(is_synced_to_crm=True)
    
    campaigns = GoogleAdsCampaign.objects.all()
    
    context = {
        'leads': leads,
        'campaigns': campaigns,
        'selected_campaign': campaign_id,
        'synced_only': synced_only,
        'total_leads': leads.count(),
        'synced_leads': leads.filter(is_synced_to_crm=True).count(),
    }
    return render(request, 'leads/google_ads_leads.html', context)

@csrf_exempt
def sync_lead_to_crm(request, lead_id):
    """Manually sync a specific Google Ads lead to CRM"""
    if request.method == 'POST':
        try:
            google_lead = GoogleAdsLead.objects.get(id=lead_id)
            sync_service = GoogleAdsSyncService()
            sync_service._sync_to_crm(google_lead)
            
            return JsonResponse({
                'success': True,
                'message': 'Lead synced to CRM successfully!'
            })
        except GoogleAdsLead.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Lead not found'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})