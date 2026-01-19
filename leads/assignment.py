from django.utils import timezone
from datetime import timedelta
from .models import TeamMember, Lead, LeadAssignment
import random

class RoundRobinAssigner:
    def __init__(self):
        pass
    
    def assign_lead(self, lead):
        """Assign lead to next available team member using proper round robin"""
        # Get active sales executives and managers (exclude admins)
        available_members = TeamMember.objects.filter(
            is_active=True,
            role__in=['Sales Executive - T5', 'Sales Manager - T4', 'Team leader - t3']
        ).exclude(role='Admin').order_by('id')
        
        if not available_members:
            return None
        
        # Get assignment counts for each member
        member_counts = {}
        for member in available_members:
            count = LeadAssignment.objects.filter(assigned_to=member).count()
            member_counts[member.id] = count
        
        # Find member with least assignments
        min_count = min(member_counts.values()) if member_counts else 0
        members_with_min_count = [
            member for member in available_members 
            if member_counts.get(member.id, 0) == min_count
        ]
        
        # If multiple members have same count, get the one who was assigned longest ago
        if len(members_with_min_count) > 1:
            # Get the member who was last assigned the longest time ago
            next_member = None
            oldest_assignment = None
            
            for member in members_with_min_count:
                last_assignment = LeadAssignment.objects.filter(
                    assigned_to=member
                ).order_by('-assigned_at').first()
                
                if not last_assignment:
                    # This member has never been assigned, prioritize them
                    next_member = member
                    break
                elif not oldest_assignment or last_assignment.assigned_at < oldest_assignment:
                    oldest_assignment = last_assignment.assigned_at
                    next_member = member
            
            if not next_member:
                next_member = members_with_min_count[0]
        else:
            next_member = members_with_min_count[0]
        
        # Create assignment
        assignment = LeadAssignment.objects.create(
            lead=lead,
            assigned_to=next_member,
            sla_deadline=timezone.now() + timedelta(minutes=30)
        )
        
        return assignment
    
    def reassign_overdue_leads(self):
        """Reassign leads that are overdue"""
        overdue_assignments = LeadAssignment.objects.filter(
            is_attended=False,
            sla_deadline__lt=timezone.now()
        )
        
        reassigned_count = 0
        for assignment in overdue_assignments:
            # Mark old assignment as overdue
            assignment.delete()
            
            # Create new assignment
            new_assignment = self.assign_lead(assignment.lead)
            if new_assignment:
                reassigned_count += 1
        
        return reassigned_count

def auto_assign_new_lead(lead):
    """Auto assign new lead when created"""
    assigner = RoundRobinAssigner()
    return assigner.assign_lead(lead)