from django.db import models
from .project_models import Project
from .models import TeamMember

class ProjectTeamMember(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='team_members')
    team_member = models.ForeignKey(TeamMember, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['project', 'team_member']
    
    def __str__(self):
        return f"{self.project.name} - {self.team_member.name}"
