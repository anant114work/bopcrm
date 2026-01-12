from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Lead, LeadReassignmentLog, LeadViewActivity, TeamMember, LeadAssignment
from .team_auth import team_login_required
from django.utils import timezone
from datetime import datetime, timedelta

def activity_dashboard(request):
    # Check if user is admin or team member
    if request.session.get('is_team_member'):
        team_member = get_object_or_404(TeamMember, id=request.session['team_member_id'])
    else:
        # Admin access - create a virtual admin team member
        team_member = type('AdminUser', (), {
            'id': 0,
            'name': 'Admin',
            'role': 'Admin',
            'get_all_team_members': lambda: TeamMember.objects.all()
        })()
    
    # Get accessible leads based on hierarchy
    accessible_leads = get_accessible_leads(team_member)
    
    # Filter parameters
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    lead_search = request.GET.get('lead_search', '')
    team_member_filter = request.GET.get('team_member_filter')
    activity_type = request.GET.get('activity_type')
    
    # Base queries
    reassignments = LeadReassignmentLog.objects.filter(lead__in=accessible_leads)
    views = LeadViewActivity.objects.filter(lead__in=accessible_leads)
    
    # Apply date filters
    if date_from:
        date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        reassignments = reassignments.filter(timestamp__date__gte=date_from)
        views = views.filter(timestamp__date__gte=date_from)
    
    if date_to:
        date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
        reassignments = reassignments.filter(timestamp__date__lte=date_to)
        views = views.filter(timestamp__date__lte=date_to)
    
    # Apply lead search
    if lead_search:
        reassignments = reassignments.filter(
            Q(lead__full_name__icontains=lead_search) |
            Q(lead__email__icontains=lead_search) |
            Q(lead__phone_number__icontains=lead_search)
        )
        views = views.filter(
            Q(lead__full_name__icontains=lead_search) |
            Q(lead__email__icontains=lead_search) |
            Q(lead__phone_number__icontains=lead_search)
        )
    
    # Apply team member filter
    if team_member_filter:
        reassignments = reassignments.filter(
            Q(reassigned_by_id=team_member_filter) |
            Q(new_assignee_id=team_member_filter) |
            Q(previous_assignee_id=team_member_filter)
        )
        views = views.filter(viewed_by_id=team_member_filter)
    
    # Apply activity type filter
    if activity_type == 'reassignments':
        views = views.none()  # Hide views
    elif activity_type == 'views':
        reassignments = reassignments.none()  # Hide reassignments
    
    # Pagination
    reassignments_paginator = Paginator(reassignments.select_related('lead', 'previous_assignee', 'new_assignee', 'reassigned_by'), 10)
    views_paginator = Paginator(views.select_related('lead', 'viewed_by'), 10)
    
    reassignments_page = reassignments_paginator.get_page(request.GET.get('r_page'))
    views_page = views_paginator.get_page(request.GET.get('v_page'))
    
    # Get all team members for filter dropdown
    all_team_members = TeamMember.objects.filter(is_active=True).order_by('name')
    
    context = {
        'team_member': team_member,
        'reassignments': reassignments_page,
        'views': views_page,
        'date_from': date_from,
        'date_to': date_to,
        'lead_search': lead_search,
        'team_member_filter': team_member_filter,
        'activity_type': activity_type,
        'all_team_members': all_team_members,
    }
    
    return render(request, 'leads/activity_dashboard.html', context)

@team_login_required
def lead_activity_detail(request, lead_id):
    team_member = get_object_or_404(TeamMember, id=request.session['team_member_id'])
    lead = get_object_or_404(Lead, id=lead_id)
    
    # Check if user can view this lead's activity
    if not can_view_lead_activity(team_member, lead):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    reassignments = LeadReassignmentLog.objects.filter(lead=lead).select_related(
        'previous_assignee', 'new_assignee', 'reassigned_by'
    )
    views = LeadViewActivity.objects.filter(lead=lead).select_related('viewed_by')
    
    context = {
        'lead': lead,
        'reassignments': reassignments,
        'views': views,
    }
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'leads/activity_detail_modal.html', context)
    
    return render(request, 'leads/activity_detail.html', context)

def reassign_lead(request):
    if request.method == 'POST':
        lead_id = request.POST.get('lead_id')
        new_assignee_id = request.POST.get('new_assignee_id')
        reason = request.POST.get('reason', '')
        
        # Handle both admin and team member access
        if request.session.get('is_team_member'):
            team_member = get_object_or_404(TeamMember, id=request.session['team_member_id'])
        else:
            # Admin access
            team_member = type('AdminUser', (), {'id': 0, 'role': 'Admin'})()
        
        lead = get_object_or_404(Lead, id=lead_id)
        new_assignee = get_object_or_404(TeamMember, id=new_assignee_id)
        
        # Check permissions (admin always has permission)
        if team_member.role != 'Admin' and not can_reassign_lead(team_member, lead):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        # Get or create assignment
        assignment, created = LeadAssignment.objects.get_or_create(
            lead=lead,
            defaults={'assigned_to': new_assignee}
        )
        
        if not created:
            # Store reassignment info for signal
            if hasattr(team_member, 'id') and team_member.id > 0:
                assignment._reassigned_by = team_member
            assignment._reassignment_reason = reason
            assignment.assigned_to = new_assignee
            assignment.save()
        
        return JsonResponse({'success': True, 'message': 'Lead reassigned successfully'})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

def get_accessible_leads(team_member):
    """Get leads that the team member can view based on hierarchy"""
    role = team_member.role
    
    if role in ['Admin', 'Sales Director - T1', 'TEAM Head - T2']:
        # Can see all leads
        return Lead.objects.all()
    elif role in ['Team leader - t3']:
        # Can see leads of their team members
        team_members = team_member.get_all_team_members()
        return Lead.objects.filter(assignment__assigned_to__in=team_members)
    else:
        # Can only see their own leads
        return Lead.objects.filter(assignment__assigned_to=team_member)

def can_view_lead_activity(team_member, lead):
    """Check if team member can view activity for this lead"""
    role = team_member.role
    
    if role in ['Admin', 'Sales Director - T1', 'TEAM Head - T2']:
        return True
    elif role in ['Team leader - t3']:
        # Can view if lead is assigned to their team
        team_members = team_member.get_all_team_members()
        return lead.assigned_to in team_members if lead.assigned_to else False
    else:
        # Can view if lead is assigned to them
        return lead.assigned_to == team_member

def can_reassign_lead(team_member, lead):
    """Check if team member can reassign this lead"""
    role = team_member.role
    
    if role in ['Admin', 'Sales Director - T1', 'TEAM Head - T2', 'Team leader - t3']:
        return True
    
    return False