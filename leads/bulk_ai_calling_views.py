from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Lead
from .project_models import Project
from .callkaro_models import CallKaroAgent
import json
import requests

def bulk_ai_calling_page(request):
    """Page for bulk AI calling"""
    leads = Lead.objects.filter(
        phone_number__isnull=False
    ).exclude(phone_number='').order_by('-created_time')[:500]
    
    agents = CallKaroAgent.objects.filter(is_active=True).order_by('name')
    projects = Project.objects.all().order_by('name')
    
    return render(request, 'leads/bulk_ai_calling.html', {
        'leads': leads,
        'agents': agents,
        'projects': projects
    })

@csrf_exempt
def bulk_ai_call(request):
    """Initiate bulk AI calls"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            agent_id = data.get('agent_id')
            leads_data = data.get('leads', [])
            
            if not agent_id or not leads_data:
                return JsonResponse({'success': False, 'error': 'Agent and leads required'})
            
            agent = CallKaroAgent.objects.get(id=agent_id)
            
            initiated = 0
            failed = 0
            
            for lead_data in leads_data:
                lead_id = lead_data.get('id')
                phone = lead_data.get('phone')
                
                try:
                    lead = Lead.objects.get(id=lead_id)
                    
                    # Clean phone number
                    clean_phone = phone.replace('+91', '').replace('+', '').replace(' ', '').replace('-', '')
                    if not clean_phone.startswith('91'):
                        clean_phone = f"91{clean_phone}"
                    
                    # Prepare payload
                    payload = {
                        "to_number": f"+{clean_phone}",
                        "agent_id": agent.agent_id,
                        "metadata": {
                            "name": lead.full_name or "User",
                            "city": lead.city or "Unknown",
                            "budget": lead.budget or "Not specified",
                            "form_name": lead.form_name or "Unknown",
                            "lead_id": str(lead.id)
                        },
                        "priority": 1
                    }
                    
                    headers = {
                        "Content-Type": "application/json",
                        "X-API-KEY": agent.api_key
                    }
                    
                    # Make API call
                    response = requests.post(
                        "https://api.callkaro.ai/call/outbound",
                        json=payload,
                        headers=headers,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        initiated += 1
                        lead.stage = 'contacted'
                        lead.save()
                    else:
                        failed += 1
                        
                except Exception as e:
                    print(f"Error calling lead {lead_id}: {str(e)}")
                    failed += 1
            
            return JsonResponse({
                'success': True,
                'initiated': initiated,
                'failed': failed,
                'total': len(leads_data)
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})
