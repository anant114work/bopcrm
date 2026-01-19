"""
Team Member Authentication System - Restricted Access
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import models
from .models import TeamMember, Lead, LeadAssignment, LeadNote
import json
from functools import wraps

def team_login_required(view_func):
    """Decorator to require team member login"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('is_team_member'):
            return redirect('team_login')
        return view_func(request, *args, **kwargs)
    return wrapper

def team_login_view(request):
    """Team member login - username: first name, password: phone number"""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip().lower()
        password = request.POST.get('password', '').strip()
        
        try:
            # Find team member by phone number and name match
            team_member = TeamMember.objects.filter(
                phone=password,
                is_active=True
            ).filter(
                models.Q(name__icontains=username) | 
                models.Q(name__iexact=username)
            ).first()
            
            if team_member:
                # Store team member info in session
                request.session['team_member_id'] = team_member.id
                request.session['team_member_name'] = team_member.name
                request.session['team_member_role'] = team_member.role
                request.session['is_team_member'] = True
                request.session['is_admin'] = team_member.role == 'Admin'
                
                # Redirect based on role
                if team_member.role == 'Admin':
                    return redirect('dashboard')  # Admin goes to main dashboard
                else:
                    return redirect('my_leads')  # Others go to my leads with sidebar
            else:
                messages.error(request, 'Invalid credentials. Please check your username and phone number.')
        
        except Exception as e:
            messages.error(request, f'Login failed: {str(e)}')
    
    return render(request, 'leads/team_login.html')

def team_dashboard_view(request):
    """Redirect team members to my_leads with sidebar navigation"""
    if not request.session.get('is_team_member'):
        return redirect('team_login')
    
    # Redirect to my_leads which has the proper sidebar
    return redirect('my_leads')

def team_lead_detail_view(request, lead_id):
    """View lead details - only if assigned to user or their subordinates"""
    if not request.session.get('is_team_member'):
        return redirect('team_login')
    
    team_member_id = request.session.get('team_member_id')
    team_member = TeamMember.objects.get(id=team_member_id)
    
    # Get subordinates
    subordinates = TeamMember.objects.filter(parent_user=team_member)
    allowed_assignees = [team_member] + list(subordinates)
    
    try:
        lead = Lead.objects.get(
            id=lead_id,
            assignment__assigned_to__in=allowed_assignees
        )
    except Lead.DoesNotExist:
        messages.error(request, 'Access denied')
        return redirect('team_dashboard')
    
    # Get notes (only from allowed team members)
    notes = lead.notes.filter(
        team_member__in=allowed_assignees
    ).order_by('-created_at')
    
    context = {
        'lead': lead,
        'team_member': team_member,
        'notes': notes,
        'assignment': lead.assignment,
        'can_edit': lead.assignment.assigned_to == team_member
    }
    
    return render(request, 'leads/team_lead_detail.html', context)

@csrf_exempt
def team_update_lead_status(request):
    """Update lead status - only own leads"""
    if not request.session.get('is_team_member'):
        return JsonResponse({'success': False, 'error': 'Access denied'})
    
    if request.method == 'POST':
        data = json.loads(request.body)
        lead_id = data.get('lead_id')
        new_stage = data.get('stage')
        
        team_member_id = request.session.get('team_member_id')
        team_member = TeamMember.objects.get(id=team_member_id)
        
        try:
            # Only allow updating own leads
            lead = Lead.objects.get(
                id=lead_id,
                assignment__assigned_to=team_member
            )
            
            lead.stage = new_stage
            lead.save()
            
            # Mark as attended
            from django.utils import timezone
            assignment = lead.assignment
            if not assignment.is_attended:
                assignment.is_attended = True
                assignment.attended_at = timezone.now()
                assignment.save()
            
            return JsonResponse({'success': True})
        
        except Lead.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Access denied'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
def team_add_note(request):
    """Add note - only to own leads"""
    if not request.session.get('is_team_member'):
        return JsonResponse({'success': False, 'error': 'Access denied'})
    
    if request.method == 'POST':
        data = json.loads(request.body)
        lead_id = data.get('lead_id')
        note_text = data.get('note')
        
        team_member_id = request.session.get('team_member_id')
        team_member = TeamMember.objects.get(id=team_member_id)
        
        try:
            # Check access to lead
            subordinates = TeamMember.objects.filter(parent_user=team_member)
            allowed_assignees = [team_member] + list(subordinates)
            
            lead = Lead.objects.get(
                id=lead_id,
                assignment__assigned_to__in=allowed_assignees
            )
            
            note = LeadNote.objects.create(
                lead=lead,
                team_member=team_member,
                note=note_text
            )
            
            return JsonResponse({
                'success': True,
                'note': {
                    'text': note.note,
                    'created_at': note.created_at.strftime('%Y-%m-%d %H:%M:%S')
                }
            })
        
        except Lead.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Access denied'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def team_profile_view(request):
    """Team member profile page with editable information"""
    if not request.session.get('is_team_member'):
        return redirect('team_login')
    
    team_member_id = request.session.get('team_member_id')
    team_member = TeamMember.objects.get(id=team_member_id)
    
    if request.method == 'POST':
        # Update profile information
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        
        try:
            team_member.name = name
            team_member.email = email
            team_member.phone = phone
            team_member.save()
            
            # Update session name
            request.session['team_member_name'] = name
            
            messages.success(request, 'Profile updated successfully!')
        except Exception as e:
            messages.error(request, 'Error updating profile. Please try again.')
    
    # Get performance stats
    total_assigned = Lead.objects.filter(assignment__assigned_to=team_member).count()
    completed = Lead.objects.filter(
        assignment__assigned_to=team_member,
        assignment__is_attended=True
    ).count()
    pending = Lead.objects.filter(
        assignment__assigned_to=team_member,
        assignment__is_attended=False
    ).count()
    
    conversion_rate = (completed / total_assigned * 100) if total_assigned > 0 else 0
    
    # Get subordinates
    subordinates = TeamMember.objects.filter(parent_user=team_member, is_active=True)
    
    context = {
        'team_member': team_member,
        'subordinates': subordinates,
        'stats': {
            'total_assigned': total_assigned,
            'completed': completed,
            'pending': pending,
            'conversion_rate': round(conversion_rate, 1)
        }
    }
    
    return render(request, 'leads/team_profile.html', context)

def team_logout_view(request):
    """Logout team member"""
    request.session.flush()
    return redirect('team_login')