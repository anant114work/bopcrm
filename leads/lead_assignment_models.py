"""
Lead Assignment and Tracking Models
"""
from django.db import models
from django.utils import timezone
from .models import Lead, TeamMember

class LeadAssignmentHistory(models.Model):
    """Track complete history of lead assignments"""
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='assignment_history')
    assigned_to = models.ForeignKey(TeamMember, on_delete=models.CASCADE)
    assigned_by = models.ForeignKey(TeamMember, on_delete=models.SET_NULL, null=True, blank=True, related_name='assignments_made')
    assigned_at = models.DateTimeField(auto_now_add=True)
    sla_deadline = models.DateTimeField()
    is_overdue = models.BooleanField(default=False)
    overdue_at = models.DateTimeField(null=True, blank=True)
    reassigned_at = models.DateTimeField(null=True, blank=True)
    reason = models.CharField(max_length=200, default='initial_assignment')
    
    class Meta:
        ordering = ['-assigned_at']
    
    def mark_overdue(self):
        """Mark this assignment as overdue"""
        if not self.is_overdue and timezone.now() > self.sla_deadline:
            self.is_overdue = True
            self.overdue_at = timezone.now()
            self.save()
    
    def __str__(self):
        return f"{self.lead.full_name} -> {self.assigned_to.name} ({self.assigned_at})"

class RoundRobinQueue(models.Model):
    """Manage round-robin assignment queue"""
    team_member = models.OneToOneField(TeamMember, on_delete=models.CASCADE)
    last_assigned_at = models.DateTimeField(null=True, blank=True)
    assignment_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['last_assigned_at', 'assignment_count']
    
    def increment_assignment(self):
        """Increment assignment count and update timestamp"""
        self.assignment_count += 1
        self.last_assigned_at = timezone.now()
        self.save()
    
    @classmethod
    def get_next_assignee(cls):
        """Get next team member in round-robin queue"""
        return cls.objects.filter(
            is_active=True,
            team_member__is_active=True
        ).first()
    
    def __str__(self):
        return f"{self.team_member.name} - {self.assignment_count} assignments"