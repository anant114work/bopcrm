"""
Enhanced Team Management Views
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import json
from .models import TeamMember
from .team_hierarchy import TeamHierarchy

def team_hierarchy_view(request):
    """Enhanced team members view with hierarchy and pagination"""
    from django.core.paginator import Paginator
    from django.db.models import Q, Count
    
    # Search and filter parameters
    search = request.GET.get('search', '')
    role_filter = request.GET.get('role', '')
    status_filter = request.GET.get('status', '')
    
    # Get all team members with related data
    members = TeamMember.objects.select_related('parent_user').prefetch_related('assigned_leads').all()
    
    # Apply filters
    if search:
        members = members.filter(
            Q(name__icontains=search) | 
            Q(email__icontains=search) | 
            Q(phone__icontains=search)
        )
    
    if role_filter:
        members = members.filter(role__icontains=role_filter)
    
    if status_filter == 'active':
        members = members.filter(is_active=True)
    elif status_filter == 'inactive':
        members = members.filter(is_active=False)
    
    # Order by name
    members = members.order_by('name')
    
    # Pagination
    paginator = Paginator(members, 12)  # 12 members per page
    page = request.GET.get('page')
    members_page = paginator.get_page(page)
    
    # Get hierarchy data
    hierarchy = TeamHierarchy.get_hierarchy_tree()
    unmapped_members = TeamHierarchy.get_unmapped_members()
    business_heads = TeamHierarchy.get_business_heads()
    stats = TeamHierarchy.get_team_stats()
    
    # Get filter options
    all_roles = TeamMember.objects.values_list('role', flat=True).distinct().exclude(role='')
    
    context = {
        'members': members_page,
        'hierarchy': hierarchy,
        'unmapped_members': unmapped_members,
        'business_heads': business_heads,
        'stats': stats,
        'total_unmapped': len(unmapped_members),
        'search': search,
        'role_filter': role_filter,
        'status_filter': status_filter,
        'all_roles': all_roles,
        'total_members': TeamMember.objects.count()
    }
    
    return render(request, 'leads/team_hierarchy.html', context)

@csrf_exempt
def assign_team_member(request):
    """Assign a team member to a parent"""
    if request.method == 'POST':
        data = json.loads(request.body)
        member_id = data.get('member_id')
        parent_id = data.get('parent_id')
        
        try:
            member = get_object_or_404(TeamMember, id=member_id)
            
            if parent_id:
                parent = get_object_or_404(TeamMember, id=parent_id)
                member.parent_user = parent
            else:
                member.parent_user = None
            
            member.save()
            
            return JsonResponse({
                'success': True,
                'message': f'{member.name} assigned successfully'
            })
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
def auto_assign_hierarchy(request):
    """Auto-assign team hierarchy based on roles"""
    if request.method == 'POST':
        try:
            assignments = TeamHierarchy.auto_assign_hierarchy()
            assigned_count = 0
            
            for assignment in assignments:
                if assignment['suggested_parent'] and assignment['confidence'] in ['high', 'medium']:
                    member = assignment['member']
                    parent = assignment['suggested_parent']
                    member.parent_user = parent
                    member.save()
                    assigned_count += 1
            
            return JsonResponse({
                'success': True,
                'message': f'Auto-assigned {assigned_count} team members',
                'assigned_count': assigned_count
            })
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def team_member_suggestions(request, member_id):
    """Get parent suggestions for a specific team member"""
    member = get_object_or_404(TeamMember, id=member_id)
    suggestions = TeamHierarchy.suggest_parent_for_member(member)
    
    suggestions_data = [{
        'id': parent.id,
        'name': parent.name,
        'role': parent.role,
        'current_team_size': parent.team_members.filter(is_active=True).count()
    } for parent in suggestions]
    
    return JsonResponse({
        'member': {
            'id': member.id,
            'name': member.name,
            'role': member.role
        },
        'suggestions': suggestions_data
    })

def team_members_list(request):
    """Enhanced team members list with pagination and filters"""
    from django.core.paginator import Paginator
    from django.db.models import Q, Count
    
    # Search and filter parameters
    search = request.GET.get('search', '')
    role_filter = request.GET.get('role', '')
    status_filter = request.GET.get('status', '')
    
    # Get all team members with related data
    members = TeamMember.objects.select_related('parent_user').prefetch_related('assigned_leads').all()
    
    # Apply filters
    if search:
        members = members.filter(
            Q(name__icontains=search) | 
            Q(email__icontains=search) | 
            Q(phone__icontains=search)
        )
    
    if role_filter:
        members = members.filter(role__icontains=role_filter)
    
    if status_filter == 'active':
        members = members.filter(is_active=True)
    elif status_filter == 'inactive':
        members = members.filter(is_active=False)
    
    # Order by name
    members = members.order_by('name')
    
    # Pagination
    paginator = Paginator(members, 15)  # 15 members per page
    page = request.GET.get('page')
    members_page = paginator.get_page(page)
    
    # Get filter options
    all_roles = TeamMember.objects.values_list('role', flat=True).distinct().exclude(role='')
    
    # Calculate stats
    total_members = TeamMember.objects.count()
    active_members = TeamMember.objects.filter(is_active=True).count()
    # Use a more efficient query for total leads
    from django.db.models import Count
    total_leads = TeamMember.objects.aggregate(
        total=Count('assigned_leads')
    )['total'] or 0
    
    context = {
        'members': members_page,
        'search': search,
        'role_filter': role_filter,
        'status_filter': status_filter,
        'all_roles': all_roles,
        'total_members': total_members,
        'active_members': active_members,
        'total_leads': total_leads
    }
    
    return render(request, 'leads/team_members_enhanced.html', context)

def create_team_member(request):
    """Create new team member with hierarchy assignment"""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        role = request.POST.get('role')
        parent_id = request.POST.get('parent_id')
        
        try:
            # Create team member
            member = TeamMember.objects.create(
                name=name,
                email=email,
                phone=phone,
                role=role
            )
            
            # Assign parent if provided
            if parent_id:
                parent = get_object_or_404(TeamMember, id=parent_id)
                member.parent_user = parent
                member.save()
            
            messages.success(request, f'Team member {name} created successfully')
            return redirect('team_hierarchy')
        
        except Exception as e:
            messages.error(request, f'Error creating team member: {str(e)}')
    
    # Get business heads for parent selection
    business_heads = TeamHierarchy.get_business_heads()
    all_members = TeamMember.objects.filter(is_active=True).order_by('name')
    
    return render(request, 'leads/create_team_member.html', {
        'business_heads': business_heads,
        'all_members': all_members,
        'role_choices': TeamMember.ROLE_CHOICES
    })

@csrf_exempt
def edit_team_member(request):
    """Edit team member details"""
    if request.method == 'POST':
        data = json.loads(request.body)
        member_id = data.get('member_id')
        
        try:
            member = get_object_or_404(TeamMember, id=member_id)
            member.name = data.get('name', member.name)
            member.email = data.get('email', member.email)
            member.phone = data.get('phone', member.phone)
            member.role = data.get('role', member.role)
            member.is_active = data.get('is_active', member.is_active)
            member.save()
            
            return JsonResponse({
                'success': True,
                'message': f'{member.name} updated successfully'
            })
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
def unassign_team_member(request):
    """Unassign team member from parent"""
    if request.method == 'POST':
        data = json.loads(request.body)
        member_id = data.get('member_id')
        
        try:
            member = get_object_or_404(TeamMember, id=member_id)
            member.parent_user = None
            member.save()
            
            return JsonResponse({
                'success': True,
                'message': f'{member.name} unassigned successfully'
            })
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})