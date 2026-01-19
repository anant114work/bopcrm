from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.contrib import messages
import json
from .form_mapping_models import FormSourceMapping
from .project_models import Project
from .models import Lead

def form_mapping_list(request):
    """List all form mappings"""
    mappings = FormSourceMapping.objects.select_related('project').all()
    projects = Project.objects.all().order_by('name')
    
    # Get all unique form names from leads
    unique_forms = Lead.objects.values_list('form_name', flat=True).distinct().order_by('form_name')
    
    # Get unmapped forms
    mapped_forms = set(mappings.values_list('form_name', flat=True))
    unmapped_forms = [f for f in unique_forms if f not in mapped_forms]
    
    return render(request, 'leads/form_mapping_list.html', {
        'mappings': mappings,
        'projects': projects,
        'unique_forms': unique_forms,
        'unmapped_forms': unmapped_forms
    })

@csrf_exempt
def create_form_mapping(request):
    """Create new form mapping"""
    if request.method == 'POST':
        data = json.loads(request.body)
        form_name = data.get('form_name')
        project_id = data.get('project_id')
        
        if not form_name or not project_id:
            return JsonResponse({'success': False, 'error': 'Missing required fields'})
        
        try:
            project = Project.objects.get(id=project_id)
            mapping, created = FormSourceMapping.objects.get_or_create(
                form_name=form_name,
                defaults={'project': project}
            )
            
            if not created:
                mapping.project = project
                mapping.is_active = True
                mapping.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Mapped "{form_name}" to {project.name}'
            })
        except Project.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Project not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
def delete_form_mapping(request, mapping_id):
    """Delete form mapping"""
    if request.method == 'POST':
        try:
            mapping = get_object_or_404(FormSourceMapping, id=mapping_id)
            mapping.delete()
            return JsonResponse({'success': True, 'message': 'Mapping deleted'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
def toggle_form_mapping(request, mapping_id):
    """Toggle form mapping active status"""
    if request.method == 'POST':
        try:
            mapping = get_object_or_404(FormSourceMapping, id=mapping_id)
            mapping.is_active = not mapping.is_active
            mapping.save()
            return JsonResponse({
                'success': True,
                'is_active': mapping.is_active
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def get_project_by_form(form_name):
    """Helper function to get project for a form name"""
    try:
        mapping = FormSourceMapping.objects.filter(
            form_name__iexact=form_name,
            is_active=True
        ).select_related('project').first()
        
        if mapping:
            return mapping.project
        
        # Fallback to keyword matching
        for project in Project.objects.all():
            for keyword in project.form_keywords:
                if keyword.lower() in form_name.lower():
                    return project
        
        return None
    except Exception:
        return None

@csrf_exempt
def bulk_create_form_mapping(request):
    """Create multiple form mappings at once"""
    if request.method == 'POST':
        data = json.loads(request.body)
        form_names = data.get('form_names', [])
        project_id = data.get('project_id')
        
        if not form_names or not project_id:
            return JsonResponse({'success': False, 'error': 'Missing required fields'})
        
        try:
            project = Project.objects.get(id=project_id)
            created_count = 0
            updated_count = 0
            errors = []
            
            for form_name in form_names:
                form_name = form_name.strip()
                if not form_name:
                    continue
                    
                try:
                    mapping, created = FormSourceMapping.objects.get_or_create(
                        form_name=form_name,
                        defaults={'project': project}
                    )
                    
                    if created:
                        created_count += 1
                    else:
                        mapping.project = project
                        mapping.is_active = True
                        mapping.save()
                        updated_count += 1
                except Exception as e:
                    errors.append(f'{form_name}: {str(e)}')
            
            message = f'Created {created_count} new mappings'
            if updated_count > 0:
                message += f', updated {updated_count} existing mappings'
            if errors:
                message += f'. Errors: {", ".join(errors)}'
            
            return JsonResponse({
                'success': True,
                'message': message,
                'created': created_count,
                'updated': updated_count,
                'errors': errors
            })
        except Project.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Project not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})
