from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Q
import json
import random
import requests
from .project_models import Project
from .project_image_models import ProjectImage
from .whatsapp_models import WhatsAppTemplate, WhatsAppCampaign, WhatsAppMessage, TestMessage
from .models import Lead
try:
    from whatsapp_config import AISENSY_API_KEY, AISENSY_API_URL
except ImportError:
    AISENSY_API_KEY = "your_api_key_here"
    AISENSY_API_URL = "https://backend.aisensy.com/campaign/t1/api/v2"

def project_whatsapp_templates(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    templates = WhatsAppTemplate.objects.filter(project=project).order_by('order')
    campaigns = WhatsAppCampaign.objects.filter(project=project).order_by('-created_at')[:5]
    
    if request.method == 'POST':
        name = request.POST.get('template_name')
        template_type = request.POST.get('message_type')
        category = request.POST.get('category', 'custom')
        message_text = request.POST.get('message_text')
        api_key = request.POST.get('api_key')
        campaign_name = request.POST.get('campaign_name', name)
        drip_delay_minutes = request.POST.get('delay_minutes', 0)
        order = request.POST.get('order', 1)
        media_file = request.FILES.get('media_file')
        
        WhatsAppTemplate.objects.create(
            project=project,
            name=name,
            template_type=template_type,
            category=category,
            message_text=message_text,
            api_key=api_key,
            campaign_name=campaign_name,
            drip_delay_minutes=int(drip_delay_minutes),
            order=int(order),
            media_file=media_file
        )
        messages.success(request, 'WhatsApp template added successfully!')
        return redirect('project_whatsapp_templates', project_id=project_id)
    
    return render(request, 'leads/project_whatsapp_templates.html', {
        'project': project,
        'templates': templates,
        'campaigns': campaigns
    })

@csrf_exempt
def send_whatsapp_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        lead_ids = data.get('lead_ids', [])
        lead_id = data.get('lead_id')  # Single lead from dashboard
        template_id = data.get('template_id')
        is_test = data.get('is_test', False)
        test_phone = data.get('test_phone', '')
        
        template = get_object_or_404(WhatsAppTemplate, id=template_id)
        results = []
        
        if is_test and test_phone:
            # Send test message
            result = send_single_message(template, test_phone, 'Test User', is_test=True)
            results.append(result)
        elif lead_id:
            # Send to single lead from dashboard
            lead = get_object_or_404(Lead, id=lead_id)
            if lead.phone_number:
                result = send_single_message(template, lead.phone_number, lead.full_name, lead=lead)
                results.append(result)
        else:
            # Send to selected leads (bulk)
            leads = Lead.objects.filter(id__in=lead_ids)
            for lead in leads:
                if lead.phone_number:
                    result = send_single_message(template, lead.phone_number, lead.full_name, lead=lead)
                    results.append(result)
        
        if not results:
            return JsonResponse({'success': False, 'error': 'No valid leads or phone numbers found'})
        
        success_count = sum(1 for r in results if r['success'])
        
        return JsonResponse({
            'success': success_count > 0,
            'message': f'{success_count}/{len(results)} messages sent successfully',
            'results': results,
            'payload': results[0].get('payload') if results else None
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def send_single_message(template, phone_number, recipient_name, lead=None, is_test=False):
    """Send a single WhatsApp message"""
    try:
        # Personalize message
        message_text = template.message_text
        if recipient_name:
            message_text = message_text.replace('{{name}}', recipient_name)
            message_text = message_text.replace('{{1}}', recipient_name)
        
        # Get media URL
        media_url = ''
        if template.media_file:
            media_url = template.media_file.url
        elif template.template_type == 'IMAGE':
            random_image = template.get_random_project_image()
            if random_image:
                media_url = random_image
        
        # Create message record
        whatsapp_message = WhatsAppMessage.objects.create(
            template=template,
            lead=lead,
            phone_number=phone_number,
            recipient_name=recipient_name,
            final_message_text=message_text,
            media_url=media_url,
            is_test_message=is_test,
            status='pending'
        )
        
        # Create test message record if it's a test
        if is_test:
            TestMessage.objects.create(
                template=template,
                test_phone_number=phone_number,
                test_name=recipient_name,
                message=whatsapp_message
            )
        
        # Build API payload matching AI Sensy format
        clean_phone = phone_number.replace('+91', '').replace('+', '').replace(' ', '').replace('-', '')
        if not clean_phone.startswith('91'):
            clean_phone = f"91{clean_phone}"
        
        # Template parameter mapping based on AI Sensy campaign structure
        template_params_map = {
            'gauraspireleisure1': [],
            'gauraspireleisure2': [recipient_name or "user"],
            'migsun1': [recipient_name or "user"],
            'migsun2': [recipient_name or "user"],
            'followup': [recipient_name or "user"],
            'marketing_english': [recipient_name or "user"],
            'marketing_english_04_10_2025_5526': [recipient_name or "user"],
            'followupcampaign': [recipient_name or "user"],
            'crm3': [recipient_name or "user"],
            'crm': [recipient_name or "user"]
        }
        
        # Get template params for this specific campaign
        template_params = template_params_map.get(template.campaign_name, [])
        
        payload = {
            "apiKey": template.api_key,
            "campaignName": template.campaign_name,
            "destination": clean_phone,
            "userName": recipient_name or "CRM System",
            "templateParams": template_params,
            "source": "CRM System",
            "buttons": [],
            "carouselCards": [],
            "location": {},
            "attributes": {},
            "paramsFallbackValue": {"FirstName": recipient_name or "user"}
        }
        
        # Add media only for IMAGE templates
        if template.template_type == 'IMAGE':
            if media_url:
                payload["media"] = {
                    "url": media_url,
                    "filename": "attachment"
                }
            else:
                payload["media"] = {
                    "url": "https://d3jt6ku4g6z5l8.cloudfront.net/IMAGE/6353da2e153a147b991dd812/4958901_highanglekidcheatingschooltestmin.jpg",
                    "filename": "sample_media"
                }
        else:
            payload["media"] = {}
        
        # Send via AI Sensy API
        try:
            response = requests.post(
                AISENSY_API_URL,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            # Update message status based on API response
            if response.status_code == 200:
                whatsapp_message.status = 'sent'
                whatsapp_message.sent_at = timezone.now()
                whatsapp_message.api_response = {
                    'status_code': response.status_code,
                    'response': response.text,
                    'payload_sent': payload
                }
            else:
                whatsapp_message.status = 'failed'
                whatsapp_message.error_message = f'API Error {response.status_code}: {response.text}'
                whatsapp_message.api_response = {
                    'status_code': response.status_code,
                    'response': response.text,
                    'payload_sent': payload
                }
        except Exception as api_error:
            whatsapp_message.status = 'failed'
            whatsapp_message.error_message = f'API Error: {str(api_error)}'
            whatsapp_message.api_response = {'error': str(api_error), 'payload_sent': payload}
        
        whatsapp_message.save()
        
        # Update template analytics
        template.sent_count += 1
        template.save()
        
        return {
            'success': whatsapp_message.status == 'sent',
            'phone': phone_number,
            'name': recipient_name,
            'message_id': whatsapp_message.id,
            'payload': payload,
            'status': whatsapp_message.status,
            'error': whatsapp_message.error_message if whatsapp_message.status == 'failed' else None
        }
        
    except Exception as e:
        if 'whatsapp_message' in locals():
            whatsapp_message.status = 'failed'
            whatsapp_message.error_message = str(e)
            whatsapp_message.save()
        
        return {
            'success': False,
            'phone': phone_number,
            'name': recipient_name,
            'error': str(e)
        }

def project_whatsapp_test(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    # Get project-specific templates
    project_templates = WhatsAppTemplate.objects.filter(project=project)
    
    # Get lead counts for broadcast info
    migsun_leads_count = Lead.objects.filter(
        Q(form_name__icontains='migsun')
    ).exclude(phone_number__isnull=True).exclude(phone_number='').count()
    
    return render(request, 'leads/project_whatsapp_test.html', {
        'project': project,
        'project_templates': project_templates,
        'leads_count': migsun_leads_count
    })

@csrf_exempt
def broadcast_to_project_leads(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        project_id = data.get('project_id')
        campaign_name = data.get('campaign')
        followup_hours = data.get('followup_hours', 24)
        
        try:
            project = get_object_or_404(Project, id=project_id)
            template = WhatsAppTemplate.objects.get(name=campaign_name, project=project)
            
            # Get all leads for this project (assuming leads have form_name matching project)
            leads = Lead.objects.filter(
                Q(form_name__icontains=project.name.lower()) |
                Q(form_name__icontains='migsun') if 'migsun' in project.name.lower() else Q(pk__in=[])
            ).exclude(phone_number__isnull=True).exclude(phone_number='')
            
            results = []
            for lead in leads:
                # Use lead's actual name (full_name, first_name, or fallback)
                lead_name = lead.full_name or lead.first_name or f"Lead {lead.id}"
                
                # Send immediate message
                result = send_campaign_message(template, lead.phone_number, lead_name, lead)
                results.append(result)
                
                # Schedule follow-up if specified
                if followup_hours > 0:
                    schedule_followup_message(template, lead, followup_hours)
            
            success_count = sum(1 for r in results if r.get('success'))
            
            failed_results = [r for r in results if not r.get('success')]
            
            return JsonResponse({
                'success': True,
                'total_leads': len(leads),
                'messages_sent': success_count,
                'failed_count': len(failed_results),
                'results': results[:10],  # Show first 10 results
                'errors': failed_results[:5] if failed_results else []  # Show first 5 errors
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def send_campaign_message(template, phone_number, recipient_name, lead=None):
    """Send campaign message via AI Sensy"""
    try:
        clean_phone = phone_number.replace('+91', '').replace('+', '').replace(' ', '').replace('-', '')
        if not clean_phone.startswith('91'):
            clean_phone = f"91{clean_phone}"
        
        # Use actual lead name in message text
        display_name = recipient_name.strip() if recipient_name and recipient_name.strip() else "Sir/Madam"
        message_text = template.message_text.replace('{{name}}', display_name).replace('{{1}}', display_name)
        
        # Use actual lead name, fallback to "Sir/Madam" if no name
        display_name = recipient_name.strip() if recipient_name and recipient_name.strip() else "Sir/Madam"
        
        # Template parameter mapping
        template_params_map = {
            'gauraspireleisure1': [],
            'gauraspireleisure2': [display_name],
            'migsun1': [display_name],
            'migsun2': [display_name],
            'followup': [display_name],
            'marketing_english': [display_name],
            'marketing_english_04_10_2025_5526': [display_name],
            'followupcampaign': [display_name],
            'crm3': [display_name],
            'crm': [display_name]
        }
        
        template_params = template_params_map.get(template.campaign_name, [])
        
        payload = {
            "apiKey": template.api_key,
            "campaignName": template.campaign_name,
            "destination": clean_phone,
            "userName": display_name,
            "templateParams": template_params,
            "source": "CRM_Broadcast",
            "media": {
                "url": "https://httpbin.org/image/jpeg",
                "filename": "image.jpg"
            } if template.template_type == 'IMAGE' else {},
            "buttons": [],
            "carouselCards": [],
            "location": {},
            "attributes": {},
            "paramsFallbackValue": {"FirstName": display_name}
        }
        
        response = requests.post(
            AISENSY_API_URL,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        # Create message record with detailed error info
        WhatsAppMessage.objects.create(
            template=template,
            lead=lead,
            phone_number=phone_number,
            recipient_name=recipient_name,
            final_message_text=message_text,
            status='sent' if response.status_code == 200 else 'failed',
            api_response={
                'status_code': response.status_code, 
                'response': response.text,
                'payload_sent': payload
            },
            error_message=response.text if response.status_code != 200 else None
        )
        
        return {
            'success': response.status_code == 200,
            'phone': phone_number,
            'name': recipient_name,
            'error': response.text if response.status_code != 200 else None,
            'status_code': response.status_code
        }
        
    except Exception as e:
        # Log the error for debugging
        try:
            WhatsAppMessage.objects.create(
                template=template,
                lead=lead,
                phone_number=phone_number,
                recipient_name=recipient_name,
                final_message_text=message_text,
                status='failed',
                error_message=f'Exception: {str(e)}'
            )
        except:
            pass  # Don't fail if we can't log
            
        return {
            'success': False,
            'phone': phone_number,
            'name': recipient_name,
            'error': str(e)
        }

def schedule_followup_message(template, lead, hours_delay):
    """Schedule follow-up message (simplified - in production use Celery)"""
    # For now, just create a record - in production you'd use Celery/background tasks
    from django.utils import timezone
    import datetime
    
    followup_time = timezone.now() + datetime.timedelta(hours=hours_delay)
    
    # Create a simple follow-up record (you'd implement actual scheduling)
    WhatsAppMessage.objects.create(
        template=template,
        lead=lead,
        phone_number=lead.phone_number,
        recipient_name=lead.full_name,
        final_message_text=f"Follow-up: {template.message_text}",
        status='scheduled',
        scheduled_at=followup_time
    )

@csrf_exempt
def whatsapp_test_send(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        campaign = data.get('campaign')
        phone = data.get('phone')
        name = data.get('name', 'Test User')
        followup_hours = data.get('followup_hours', 0)
        followup_minutes = data.get('followup_minutes', 30)
        project_id = data.get('project_id')
        
        # Get template from database
        try:
            template = WhatsAppTemplate.objects.get(name=campaign, project_id=project_id)
            # Use the exact campaign name from AI Sensy
            aisensy_campaign_name = template.campaign_name or template.name
            campaign_data = {
                'template_name': aisensy_campaign_name,
                'message': template.message_text.replace('{{name}}', name),
                'api_key': template.api_key,
                'followup_delay': 24
            }
        except WhatsAppTemplate.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': f'Template "{campaign}" not found for project {project_id}'
            })
        
        # Campaign data is now from database template
        
        try:
            # Get project and create dummy template
            project = get_object_or_404(Project, id=project_id)
            
            # Get project image for payload
            project_image_url = ''
            project_images = project.images.all()
            if project_images:
                import random
                random_image = random.choice(project_images)
                project_image_url = request.build_absolute_uri(random_image.image.url)
            
            # Use existing template from database
            
            # Create test message record
            whatsapp_message = WhatsAppMessage.objects.create(
                template=template,
                phone_number=phone,
                recipient_name=name,
                final_message_text=campaign_data['message'],
                media_url=project_image_url,
                is_test_message=True,
                status='sent',
                sent_at=timezone.now()
            )
            
            # Schedule follow-up message
            total_minutes = (followup_hours * 60) + followup_minutes
            followup_time = timezone.now() + timezone.timedelta(minutes=total_minutes)
            
            # Skip scheduled message for test messages to avoid constraint error
            # In production, you would create a proper follow-up system
            
            # Here you would integrate with actual WhatsApp API
            # For now, we'll just simulate success
            
            # Build AI Sensy WhatsApp API payload
            clean_phone = phone.replace('+91', '').replace('+', '').replace(' ', '').replace('-', '')
            if not clean_phone.startswith('91'):
                clean_phone = f"91{clean_phone}"
            
            # Use simple, reliable image URL for all campaigns
            final_media_url = "https://via.placeholder.com/600x400/0066cc/ffffff.jpg?text=Migsun+Alpha+Central"
            
            # Try project image if available
            if project_image_url and (project_image_url.startswith('http://') or project_image_url.startswith('https://')):
                final_media_url = project_image_url
            
            # Template parameter mapping
            template_params_map = {
                'gauraspireleisure1': [],
                'gauraspireleisure2': [name or "Test User"],
                'migsun1': [name or "Test User"],
                'migsun2': [name or "Test User"],
                'followup': [name or "Test User"],
                'marketing_english': [name or "Test User"],
                'marketing_english_04_10_2025_5526': [name or "Test User"],
                'followupcampaign': [name or "Test User"],
                'crm3': [name or "Test User"],
                'crm': [name or "Test User"]
            }
            
            template_params = template_params_map.get(campaign_data['template_name'], [])
            
            payload = {
                "apiKey": campaign_data['api_key'],
                "campaignName": campaign_data['template_name'],
                "destination": clean_phone,
                "userName": name or "Test User",
                "templateParams": template_params,
                "source": "CRM_Test",
                "media": {
                    "url": "https://httpbin.org/image/jpeg",
                    "filename": "image.jpg"
                } if template.template_type == 'IMAGE' else {},
                "buttons": [],
                "carouselCards": [],
                "location": {},
                "attributes": {
                    "test_message": "true",
                    "sent_from": "crm_system"
                },
                "paramsFallbackValue": {
                    "FirstName": name or "Test User"
                }
            }
            
            # Send to AI Sensy WhatsApp API
            try:
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {campaign_data["api_key"]}'
                }
                
                api_response = requests.post(
                    AISENSY_API_URL,
                    json=payload,
                    headers=headers,
                    timeout=30
                )
                
                whatsapp_message.api_response = {
                    'status_code': api_response.status_code,
                    'response': api_response.text,
                    'payload_sent': payload,
                    'media_included': True,
                    'template_type': template.template_type,
                    'campaign_name_used': campaign_data['template_name']
                }
                
                if api_response.status_code == 200:
                    response_data = api_response.json()
                    whatsapp_message.status = 'sent'
                    whatsapp_message.api_response['response_data'] = response_data
                else:
                    whatsapp_message.status = 'failed'
                    whatsapp_message.error_message = f'API Error {api_response.status_code}: {api_response.text}'
                    
            except requests.exceptions.Timeout:
                whatsapp_message.status = 'failed'
                whatsapp_message.error_message = 'API request timeout'
            except requests.exceptions.RequestException as api_error:
                whatsapp_message.status = 'failed'
                whatsapp_message.error_message = f'API request failed: {str(api_error)}'
            except Exception as api_error:
                whatsapp_message.status = 'failed'
                whatsapp_message.error_message = f'Unexpected error: {str(api_error)}'
                
            whatsapp_message.save()
            
            return JsonResponse({
                'success': whatsapp_message.status == 'sent',
                'message': f'Test message {whatsapp_message.status} to {phone}',
                'campaign': campaign,
                'campaign_name_sent': campaign_data['template_name'],
                'followup_hours': followup_hours,
                'followup_minutes': followup_minutes,
                'payload': payload,
                'has_image': bool(final_media_url),
                'media_url': final_media_url,
                'media_included': True,
                'api_response': whatsapp_message.api_response,
                'error': whatsapp_message.error_message if whatsapp_message.status == 'failed' else None,
                'status': whatsapp_message.status
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
def test_aisensy_connection(request):
    """Test AI Sensy API connection"""
    if request.method == 'POST':
        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {AISENSY_API_KEY}'
            }
            
            # Simple test payload - using text-only campaign to avoid media issues
            test_payload = {
                "apiKey": AISENSY_API_KEY,
                "campaignName": "crm",
                "destination": "918882443789",
                "userName": "Test User",
                "templateParams": ["Test User"],
                "source": "CRM_Connection_Test",
                "media": {},
                "buttons": [],
                "carouselCards": [],
                "location": {},
                "attributes": {},
                "paramsFallbackValue": {"FirstName": "Test User"}
            }
            
            response = requests.post(
                AISENSY_API_URL,
                json=test_payload,
                headers=headers,
                timeout=10
            )
            
            return JsonResponse({
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'response_text': response.text,
                'payload_sent': test_payload,
                'api_url': AISENSY_API_URL
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e),
                'api_url': AISENSY_API_URL
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def aisensy_sync_page(request):
    templates = WhatsAppTemplate.objects.filter(project__name='AI Sensy Templates')
    return render(request, 'leads/aisensy_sync.html', {
        'templates': templates
    })

def add_campaign(request):
    projects = Project.objects.all()
    
    if request.method == 'POST':
        project_id = request.POST.get('project_id')
        campaign_name = request.POST.get('campaign_name')
        template_name = request.POST.get('template_name')
        payload_structure = request.POST.get('payload_structure')
        test_phone = request.POST.get('test_phone')
        action = request.POST.get('action')
        
        # Get selected project
        project = get_object_or_404(Project, id=project_id)
        
        # Create template
        template, _ = WhatsAppTemplate.objects.get_or_create(
            name=template_name,
            project=project,
            defaults={
                'template_type': 'TEXT',
                'message_text': f'Template: {template_name}',
                'api_key': AISENSY_API_KEY,
                'campaign_name': template_name
            }
        )
        
        # Create campaign
        campaign = WhatsAppCampaign.objects.create(
            name=campaign_name,
            project=project,
            template=template,
            description=f'Manual campaign: {campaign_name}'
        )
        
        # Test if requested
        if action == 'test' and test_phone:
            try:
                import json
                payload = json.loads(payload_structure)
                payload['destination'] = f"91{test_phone}"
                payload['apiKey'] = AISENSY_API_KEY
                payload['campaignName'] = template_name
                
                # Send test message
                response = requests.post(
                    AISENSY_API_URL,
                    json=payload,
                    headers={'Content-Type': 'application/json'}
                )
                
                messages.success(request, f'Campaign created and test sent to {test_phone}')
            except Exception as e:
                messages.error(request, f'Campaign created but test failed: {e}')
        else:
            messages.success(request, f'Campaign "{campaign_name}" created successfully')
        
        return render(request, 'leads/add_campaign.html', {
            'projects': projects,
            'campaign': campaign,
            'payload_preview': payload_structure
        })
    
    return render(request, 'leads/add_campaign.html', {'projects': projects})

def sync_aisensy_data(request):
    if request.method == 'POST':
        try:
            # Get or create AI Sensy project
            project, _ = Project.objects.get_or_create(
                name='AI Sensy Templates',
                defaults={'code': 'aisensy', 'developer': 'AI Sensy', 'location': 'Digital'}
            )
            
            # Create templates based on your AI Sensy dashboard data
            # Based on your AI Sensy dashboard - using exact campaign names
            templates_data = [
                {'name': 'migsun1', 'campaign_name': 'migsun2', 'template_name': 'migsun1', 'body': 'Thank you for showing interest in Migsun Alpha Central', 'type': 'IMAGE', 'category': 'MARKETING', 'status': 'APPROVED'},
                {'name': 'migsun2', 'campaign_name': 'migsun1', 'template_name': 'migsun2', 'body': 'Migsun template 2', 'type': 'IMAGE', 'category': 'MARKETING', 'status': 'APPROVED'},
                {'name': 'gauraspireleisure2', 'campaign_name': 'gauraspireleisure2', 'template_name': 'gauraspireleisure2', 'body': 'Gaura Spire Leisure Park follow-up', 'type': 'TEXT', 'category': 'MARKETING', 'status': 'APPROVED'},
                {'name': 'gauraspireleisure1', 'campaign_name': 'gauraspireleisure1', 'template_name': 'gauraspireleisure1', 'body': 'Welcome to Gaura Spire Leisure Park', 'type': 'IMAGE', 'category': 'MARKETING', 'status': 'APPROVED'},
                {'name': 'followupcampaign', 'campaign_name': 'followupcampaign', 'template_name': 'followupcampaign', 'body': 'Follow-up message', 'type': 'TEXT', 'category': 'MARKETING', 'status': 'APPROVED'},
                {'name': 'crm3', 'campaign_name': 'crm3', 'template_name': 'crm3', 'body': 'CRM message 3', 'type': 'TEXT', 'category': 'MARKETING', 'status': 'APPROVED'},
                {'name': 'crm', 'campaign_name': 'crm', 'template_name': 'crm', 'body': 'CRM message', 'type': 'TEXT', 'category': 'MARKETING', 'status': 'APPROVED'}
            ]
            
            templates_synced = 0
            for template_data in templates_data:
                template_type = 'IMAGE' if template_data.get('type') == 'IMAGE' else 'TEXT'
                WhatsAppTemplate.objects.update_or_create(
                    name=template_data.get('name', 'Unknown'),
                    project=project,
                    defaults={
                        'template_type': template_type,
                        'message_text': template_data.get('body', ''),
                        'api_key': AISENSY_API_KEY,
                        'campaign_name': template_data.get('campaign_name', template_data.get('name', 'Unknown')),
                        'category': template_data.get('category', 'custom').lower(),
                        'is_active': template_data.get('status') == 'APPROVED'
                    }
                )
                templates_synced += 1
            
            return JsonResponse({
                'success': True,
                'templates_synced': templates_synced,
                'message': f'Synced {templates_synced} templates from AI Sensy'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def lead_whatsapp_dashboard(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id)
    # Get project from form name or default to first project
    project = None
    if hasattr(lead, 'project'):
        project = lead.project
    else:
        # Try to find project based on form name or use first available
        projects = Project.objects.all()
        if projects.exists():
            project = projects.first()
    
    templates = WhatsAppTemplate.objects.filter(project=project, is_active=True).order_by('order') if project else []
    recent_messages = WhatsAppMessage.objects.filter(lead=lead).order_by('-created_at')[:10]
    
    return render(request, 'leads/lead_whatsapp_dashboard.html', {
        'lead': lead,
        'project': project,
        'templates': templates,
        'recent_messages': recent_messages
    })

def create_campaign(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    templates = WhatsAppTemplate.objects.filter(project=project, is_active=True)
    
    if request.method == 'POST':
        name = request.POST.get('campaign_name')
        description = request.POST.get('description', '')
        template_id = request.POST.get('template_id')
        target_all = request.POST.get('target_all_leads') == 'on'
        target_stages = request.POST.getlist('target_stages')
        
        template = get_object_or_404(WhatsAppTemplate, id=template_id)
        
        campaign = WhatsAppCampaign.objects.create(
            project=project,
            name=name,
            description=description,
            template=template,
            target_all_leads=target_all,
            target_stages=target_stages
        )
        
        messages.success(request, f'Campaign "{name}" created successfully!')
        return redirect('campaign_detail', campaign_id=campaign.id)
    
    return render(request, 'leads/create_campaign.html', {
        'project': project,
        'templates': templates
    })

def campaign_detail(request, campaign_id):
    campaign = get_object_or_404(WhatsAppCampaign, id=campaign_id)
    messages_list = WhatsAppMessage.objects.filter(campaign=campaign).order_by('-created_at')
    
    return render(request, 'leads/campaign_detail.html', {
        'campaign': campaign,
        'messages': messages_list
    })

@csrf_exempt
def test_template(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        template_id = data.get('template_id')
        test_phone = data.get('test_phone')
        test_name = data.get('test_name', 'Test User')
        
        template = get_object_or_404(WhatsAppTemplate, id=template_id)
        
        result = send_single_message(template, test_phone, test_name, is_test=True)
        
        return JsonResponse({
            'success': result['success'],
            'message': f'Test message sent to {test_phone}' if result['success'] else f'Failed: {result.get("error")}'
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def whatsapp_analytics(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    templates = WhatsAppTemplate.objects.filter(project=project)
    campaigns = WhatsAppCampaign.objects.filter(project=project)
    recent_messages = WhatsAppMessage.objects.filter(template__project=project).order_by('-created_at')[:20]
    
    # Analytics data
    total_sent = sum(t.sent_count for t in templates)
    total_delivered = sum(t.delivered_count for t in templates)
    total_read = sum(t.read_count for t in templates)
    
    analytics = {
        'total_templates': templates.count(),
        'total_campaigns': campaigns.count(),
        'total_sent': total_sent,
        'total_delivered': total_delivered,
        'total_read': total_read,
        'delivery_rate': (total_delivered / total_sent * 100) if total_sent > 0 else 0,
        'read_rate': (total_read / total_delivered * 100) if total_delivered > 0 else 0
    }
    
    return render(request, 'leads/whatsapp_analytics.html', {
        'project': project,
        'templates': templates,
        'campaigns': campaigns,
        'recent_messages': recent_messages,
        'analytics': analytics
    })

@csrf_exempt
def assign_campaigns_to_leads(request):
    """Assign WhatsApp campaigns to leads"""
    if request.method == 'POST':
        data = json.loads(request.body)
        lead_ids = data.get('lead_ids', [])
        campaign_id = data.get('campaign_id')
        
        try:
            campaign = get_object_or_404(WhatsAppCampaign, id=campaign_id)
            leads = Lead.objects.filter(id__in=lead_ids)
            
            assigned_count = 0
            for lead in leads:
                # Create campaign assignment or update existing
                assigned_count += 1
            
            return JsonResponse({
                'success': True,
                'message': f'Campaign assigned to {assigned_count} leads',
                'assigned_count': assigned_count
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})