"""
Lead Reassignment and Round-Robin System
"""
from django.utils import timezone
from django.db import models
from datetime import timedelta
from .models import Lead, TeamMember, LeadAssignment
from .lead_assignment_models import LeadAssignmentHistory, RoundRobinQueue

class LeadReassignmentManager:
    """Manage lead reassignments and round-robin distribution"""
    
    @classmethod
    def get_overdue_leads(cls):
        """Get all overdue leads with their assignment history"""
        overdue_assignments = LeadAssignment.objects.filter(
            is_attended=False,
            sla_deadline__lt=timezone.now()
        ).select_related('lead', 'assigned_to')
        
        overdue_data = []
        for assignment in overdue_assignments:
            # Get assignment history for this lead
            history = LeadAssignmentHistory.objects.filter(
                lead=assignment.lead
            ).select_related('assigned_to', 'assigned_by')
            
            overdue_hours = (timezone.now() - assignment.sla_deadline).total_seconds() / 3600
            
            overdue_data.append({
                'lead': assignment.lead,
                'current_assignee': assignment.assigned_to,
                'assigned_at': assignment.assigned_at,
                'sla_deadline': assignment.sla_deadline,
                'overdue_hours': round(overdue_hours, 1),
                'assignment_history': history,
                'total_reassignments': history.count() - 1  # Exclude initial assignment
            })
        
        return overdue_data
    
    @classmethod
    def shuffle_overdue_leads(cls, reassigned_by=None):
        """Shuffle all overdue leads using round-robin"""
        overdue_leads = cls.get_overdue_leads()
        shuffled_count = 0
        
        for overdue_data in overdue_leads:
            lead = overdue_data['lead']
            current_assignee = overdue_data['current_assignee']
            
            # Get next assignee (different from current)
            next_assignee = cls._get_next_round_robin_assignee(exclude=current_assignee)
            
            if next_assignee:
                # Reassign the lead
                cls.reassign_lead(
                    lead=lead,
                    new_assignee=next_assignee,
                    reassigned_by=reassigned_by,
                    reason='overdue_shuffle'
                )
                shuffled_count += 1
        
        return {
            'shuffled_count': shuffled_count,
            'total_overdue': len(overdue_leads)
        }
    
    @classmethod
    def reassign_lead(cls, lead, new_assignee, reassigned_by=None, reason='manual_reassignment'):
        """Reassign a lead to a new team member"""
        try:
            # Get current assignment
            current_assignment = LeadAssignment.objects.get(lead=lead)
            
            # Mark current assignment history as reassigned
            current_history = LeadAssignmentHistory.objects.filter(
                lead=lead,
                assigned_to=current_assignment.assigned_to,
                reassigned_at__isnull=True
            ).first()
            
            if current_history:
                current_history.reassigned_at = timezone.now()
                if current_assignment.is_overdue:
                    current_history.mark_overdue()
                current_history.save()
            
            # Create new assignment history
            new_sla_deadline = timezone.now() + timedelta(minutes=30)
            LeadAssignmentHistory.objects.create(
                lead=lead,
                assigned_to=new_assignee,
                assigned_by=reassigned_by,
                sla_deadline=new_sla_deadline,
                reason=reason
            )
            
            # Update current assignment
            current_assignment.assigned_to = new_assignee
            current_assignment.assigned_at = timezone.now()
            current_assignment.sla_deadline = new_sla_deadline
            current_assignment.is_attended = False
            current_assignment.attended_at = None
            current_assignment.save()
            
            # Update round-robin queue
            queue_item, created = RoundRobinQueue.objects.get_or_create(
                team_member=new_assignee,
                defaults={'is_active': True}
            )
            queue_item.increment_assignment()
            
            return True
        
        except Exception as e:
            print(f"Error reassigning lead: {e}")
            return False
    
    @classmethod
    def _get_next_round_robin_assignee(cls, exclude=None):
        """Get next team member in round-robin, excluding specified member"""
        queue = RoundRobinQueue.objects.filter(
            is_active=True,
            team_member__is_active=True
        )
        
        if exclude:
            queue = queue.exclude(team_member=exclude)
        
        first_queue = queue.first()
        return first_queue.team_member if first_queue else None
    
    @classmethod
    def initialize_round_robin_queue(cls):
        """Initialize round-robin queue with all active team members"""
        active_members = TeamMember.objects.filter(is_active=True)
        
        for member in active_members:
            RoundRobinQueue.objects.get_or_create(
                team_member=member,
                defaults={'is_active': True}
            )
    
    @classmethod
    def get_lead_assignment_timeline(cls, lead):
        """Get complete assignment timeline for a lead"""
        history = LeadAssignmentHistory.objects.filter(
            lead=lead
        ).select_related('assigned_to', 'assigned_by').order_by('assigned_at')
        
        timeline = []
        for i, assignment in enumerate(history):
            is_current = (i == len(history) - 1) and assignment.reassigned_at is None
            
            timeline_item = {
                'assignment': assignment,
                'is_current': is_current,
                'duration': None,
                'status': 'current' if is_current else 'completed'
            }
            
            # Calculate duration if not current
            if not is_current and assignment.reassigned_at:
                duration = assignment.reassigned_at - assignment.assigned_at
                timeline_item['duration'] = duration
            elif is_current:
                duration = timezone.now() - assignment.assigned_at
                timeline_item['duration'] = duration
            
            timeline.append(timeline_item)
        
        return timeline
    
    @classmethod
    def get_reassignment_stats(cls):
        """Get statistics about lead reassignments"""
        total_leads = Lead.objects.count()
        overdue_count = LeadAssignment.objects.filter(
            is_attended=False,
            sla_deadline__lt=timezone.now()
        ).count()
        
        # Get leads with multiple assignments
        reassigned_leads = LeadAssignmentHistory.objects.values('lead').annotate(
            assignment_count=models.Count('id')
        ).filter(assignment_count__gt=1).count()
        
        return {
            'total_leads': total_leads,
            'overdue_leads': overdue_count,
            'reassigned_leads': reassigned_leads,
            'overdue_percentage': (overdue_count / total_leads * 100) if total_leads > 0 else 0
        }