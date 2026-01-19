from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from leads.models import Lead, TeamMember, CallLog
from leads.drip_campaign_models import DripSubscription, DripMessage

def lead_detail_enhanced(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id)
    
    # Get drip campaign subscription
    drip_subscription = DripSubscription.objects.filter(
        lead=lead,
        status='active'
    ).select_related('campaign').first()
    
    # Get drip messages
    drip_messages = []
    if drip_subscription:
        drip_messages = DripMessage.objects.filter(
            subscription=drip_subscription
        ).order_by('day_number')
    
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
