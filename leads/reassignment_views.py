"""
Lead Reassignment Views
"""
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Lead, TeamMember
from .lead_reassignment import LeadReassignmentManager

def overdue_leads_dashboard(request):
    """Dashboard showing overdue leads with reassignment options"""
    overdue_leads = LeadReassignmentManager.get_overdue_leads()
    stats = LeadReassignmentManager.get_reassignment_stats()
    active_members = TeamMember.objects.filter(is_active=True).order_by('name')
    
    context = {
        'overdue_leads': overdue_leads,
        'stats': stats,
        'active_members': active_members,
        'total_overdue': len(overdue_leads)
    }
    
    return render(request, 'leads/overdue_leads_dashboard.html', context)

@csrf_exempt
def shuffle_overdue_leads(request):
    """Shuffle all overdue leads using round-robin"""
    if request.method == 'POST':
        try:
            # Initialize round-robin queue if needed
            LeadReassignmentManager.initialize_round_robin_queue()
            
            # Get reassigned_by from request (could be current user)
            data = json.loads(request.body) if request.body else {}
            reassigned_by_id = data.get('reassigned_by_id')
            reassigned_by = None
            
            if reassigned_by_id:
                reassigned_by = TeamMember.objects.get(id=reassigned_by_id)
            
            # Shuffle overdue leads
            result = LeadReassignmentManager.shuffle_overdue_leads(reassigned_by=reassigned_by)
            
            return JsonResponse({
                'success': True,
                'message': f'Shuffled {result["shuffled_count"]} out of {result["total_overdue"]} overdue leads',
                'shuffled_count': result['shuffled_count'],
                'total_overdue': result['total_overdue']
            })
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
def reassign_single_lead(request):
    """Reassign a single lead to a specific team member"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            lead_id = data.get('lead_id')
            new_assignee_id = data.get('new_assignee_id')
            reassigned_by_id = data.get('reassigned_by_id')
            reason = data.get('reason', 'manual_reassignment')
            
            lead = get_object_or_404(Lead, id=lead_id)
            new_assignee = get_object_or_404(TeamMember, id=new_assignee_id)
            reassigned_by = None
            
            if reassigned_by_id:
                reassigned_by = TeamMember.objects.get(id=reassigned_by_id)
            
            success = LeadReassignmentManager.reassign_lead(
                lead=lead,
                new_assignee=new_assignee,
                reassigned_by=reassigned_by,
                reason=reason
            )
            
            if success:
                return JsonResponse({
                    'success': True,
                    'message': f'Lead {lead.full_name} reassigned to {new_assignee.name}'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Failed to reassign lead'
                })
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def lead_assignment_timeline(request, lead_id):
    """Get assignment timeline for a specific lead"""
    lead = get_object_or_404(Lead, id=lead_id)
    timeline = LeadReassignmentManager.get_lead_assignment_timeline(lead)
    
    timeline_data = []
    for item in timeline:
        assignment = item['assignment']
        timeline_data.append({
            'assigned_to': assignment.assigned_to.name,
            'assigned_to_role': assignment.assigned_to.role,
            'assigned_by': assignment.assigned_by.name if assignment.assigned_by else 'System',
            'assigned_at': assignment.assigned_at.strftime('%Y-%m-%d %H:%M:%S'),
            'sla_deadline': assignment.sla_deadline.strftime('%Y-%m-%d %H:%M:%S'),
            'is_overdue': assignment.is_overdue,
            'overdue_at': assignment.overdue_at.strftime('%Y-%m-%d %H:%M:%S') if assignment.overdue_at else None,
            'reassigned_at': assignment.reassigned_at.strftime('%Y-%m-%d %H:%M:%S') if assignment.reassigned_at else None,
            'reason': assignment.reason,
            'is_current': item['is_current'],
            'duration_hours': item['duration'].total_seconds() / 3600 if item['duration'] else None,
            'status': item['status']
        })
    
    return JsonResponse({
        'lead': {
            'id': lead.id,
            'name': lead.full_name,
            'phone': lead.phone_number,
            'email': lead.email
        },
        'timeline': timeline_data,
        'total_assignments': len(timeline_data)
    })

def initialize_round_robin(request):
    """Initialize round-robin queue with all active team members"""
    try:
        LeadReassignmentManager.initialize_round_robin_queue()
        return JsonResponse({
            'success': True,
            'message': 'Round-robin queue initialized successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })