from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import openpyxl
import re
from .project_models import Project
from .models import TeamMember
from .project_team_models import ProjectTeamMember

def project_team_members(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    team_members = project.team_members.all()
    all_team_members = TeamMember.objects.filter(is_active=True)
    
    return render(request, 'leads/project_team_members.html', {
        'project': project,
        'team_members': team_members,
        'all_team_members': all_team_members
    })

@csrf_exempt
def upload_project_team_members(request, project_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    project = get_object_or_404(Project, id=project_id)
    
    if 'file' not in request.FILES:
        return JsonResponse({'error': 'No file provided'})
    
    try:
        excel_file = request.FILES['file']
        workbook = openpyxl.load_workbook(excel_file)
        worksheet = workbook.active
        
        added_count = 0
        skipped_count = 0
        errors = []
        
        for row_idx, row in enumerate(worksheet.iter_rows(min_row=1, values_only=True), start=1):
            if not row[0]:
                continue
            
            name = str(row[0]).strip() if row[0] else ''
            name = re.sub(r'^\d+\.\s*', '', name)
            
            phone_val = row[1] if len(row) > 1 else None
            
            if not phone_val:
                errors.append(f"Row {row_idx}: Phone required")
                skipped_count += 1
                continue
            
            try:
                phone = str(int(float(str(phone_val).strip())))
            except (ValueError, TypeError):
                errors.append(f"Row {row_idx}: Invalid phone")
                skipped_count += 1
                continue
            
            try:
                team_member, created = TeamMember.objects.get_or_create(
                    phone=phone,
                    defaults={'name': name}
                )
                
                obj, proj_created = ProjectTeamMember.objects.get_or_create(
                    project=project,
                    team_member=team_member
                )
                
                if proj_created:
                    added_count += 1
                else:
                    skipped_count += 1
                    
            except Exception as e:
                errors.append(f"Row {row_idx}: {str(e)}")
                skipped_count += 1
        
        return JsonResponse({
            'success': True,
            'added': added_count,
            'skipped': skipped_count,
            'errors': errors[:10]
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)})

@csrf_exempt
def add_team_member_to_project(request, project_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    project = get_object_or_404(Project, id=project_id)
    team_member_id = request.POST.get('team_member_id')
    
    try:
        team_member = TeamMember.objects.get(id=team_member_id)
        obj, created = ProjectTeamMember.objects.get_or_create(
            project=project,
            team_member=team_member
        )
        
        return JsonResponse({
            'success': True,
            'message': f'{team_member.name} added to {project.name}'
        })
    except TeamMember.DoesNotExist:
        return JsonResponse({'error': 'Team member not found'})

@csrf_exempt
def remove_team_member_from_project(request, project_id, team_member_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    project = get_object_or_404(Project, id=project_id)
    
    try:
        ProjectTeamMember.objects.get(
            project=project,
            team_member_id=team_member_id
        ).delete()
        
        return JsonResponse({'success': True})
    except ProjectTeamMember.DoesNotExist:
        return JsonResponse({'error': 'Not found'})
