def get_user_leads(request):
    """
    Get leads based on user permissions:
    - Admin sees all leads
    - Team members see only assigned leads
    """
    from .models import Lead, TeamMember
    
    # Check if user is admin
    team_member_name = request.session.get('team_member_name', '')
    is_team_member = request.session.get('is_team_member', False)
    
    # Admin sees everything
    if not is_team_member or team_member_name == 'ADMIN USER':
        return Lead.objects.all()
    
    # Team member sees only assigned leads
    team_member_id = request.session.get('team_member_id')
    if team_member_id:
        try:
            team_member = TeamMember.objects.get(id=team_member_id)
            return Lead.objects.filter(assignment__assigned_to=team_member)
        except TeamMember.DoesNotExist:
            pass
    
    return Lead.objects.none()

def is_admin_user(request):
    """Check if current user is admin"""
    team_member_name = request.session.get('team_member_name', '')
    is_team_member = request.session.get('is_team_member', False)
    return not is_team_member or team_member_name == 'ADMIN USER'