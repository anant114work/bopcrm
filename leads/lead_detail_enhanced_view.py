from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from leads.models import Lead, TeamMember, CallLog

def lead_detail_enhanced(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id)
    
    # Get drip campaign subscription if exists
    drip_subscription = None
    drip_messages = []
    try:
        from leads.drip_campaign_models import DripCampaignSubscription, DripCampaignMessage
        drip_subscription = DripCampaignSubscription.objects.filter(
            lead=lead,
            is_active=True
        ).select_related('campaign').first()
        
        if drip_subscription:
            drip_messages = DripCampaignMessage.objects.filter(
                subscription=drip_subscription
            ).order_by('day_number')
    except:
        pass
    
    # Get call logs
    call_logs = CallLog.objects.filter(lead=lead).order_by('-initiated_at')[:10]
    
    # Get team members for assignment
    team_members = TeamMember.objects.filter(is_active=True).order_by('name')
    
    context = {
        'lead': lead,
        'drip_subscription': drip_subscription,
        'drip_messages': drip_messages,
        'call_logs': call_logs,
        'team_members': team_members
    }
    
    return render(request, 'leads/lead_detail_enhanced.html', context)
