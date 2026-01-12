from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from .models import Lead, LeadAssignment, TeamMember
from .form_mapping_models import FormSourceMapping
from .project_team_models import ProjectTeamMember

@receiver(post_save, sender=Lead)
def auto_assign_lead_to_project_team(sender, instance, created, **kwargs):
    if not created:
        return
    
    if not instance.form_name:
        return
    
    try:
        mapping = FormSourceMapping.objects.get(form_name=instance.form_name, is_active=True)
        project = mapping.project
        
        team_members = ProjectTeamMember.objects.filter(project=project).values_list('team_member_id', flat=True)
        
        if not team_members:
            return
        
        team_member_id = team_members[0]
        team_member = TeamMember.objects.get(id=team_member_id)
        
        if not hasattr(instance, 'assignment') or instance.assignment is None:
            LeadAssignment.objects.create(
                lead=instance,
                assigned_to=team_member,
                sla_deadline=timezone.now() + timedelta(minutes=30)
            )
    except FormSourceMapping.DoesNotExist:
        pass
    except Exception as e:
        pass
