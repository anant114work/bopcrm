from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import json
from .auto_whatsapp_models import AutoWhatsAppCampaign
from .project_models import Project
from .whatsapp_models import WhatsAppTemplate

def auto_whatsapp_config(request):
    """Configure automatic WhatsApp campaigns"""
    campaigns = AutoWhatsAppCampaign.objects.select_related('project', 'template').all()
    projects = Project.objects.all()
    
    return render(request, 'leads/auto_whatsapp_config.html', {
        'campaigns': campaigns,
        'projects': projects
    })

@csrf_exempt
def create_auto_campaign(request):
    """Create new auto WhatsApp campaign"""
    if request.method == 'POST':
        data = json.loads(request.body)
        project_id = data.get('project_id')
        template_id = data.get('template_id')
        delay_minutes = data.get('delay_minutes', 0)
        
        if not project_id or not template_id:
            return JsonResponse({'success': False, 'error': 'Missing required fields'})
        
        try:
            project = Project.objects.get(id=project_id)
            template = WhatsAppTemplate.objects.get(id=template_id)
            
            campaign = AutoWhatsAppCampaign.objects.create(
                project=project,
                template=template,
                delay_minutes=delay_minutes
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Auto campaign created for {project.name}'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
def toggle_auto_campaign(request, campaign_id):
    """Toggle auto campaign active status"""
    if request.method == 'POST':
        try:
            campaign = get_object_or_404(AutoWhatsAppCampaign, id=campaign_id)
            campaign.is_active = not campaign.is_active
            campaign.save()
            return JsonResponse({
                'success': True,
                'is_active': campaign.is_active
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
def delete_auto_campaign(request, campaign_id):
    """Delete auto campaign"""
    if request.method == 'POST':
        try:
            campaign = get_object_or_404(AutoWhatsAppCampaign, id=campaign_id)
            campaign.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
def get_project_templates(request, project_id):
    """Get templates for a project"""
    try:
        templates = WhatsAppTemplate.objects.filter(project_id=project_id)
        data = [{'id': t.id, 'name': t.name} for t in templates]
        return JsonResponse({'success': True, 'templates': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
