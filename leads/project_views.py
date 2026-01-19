from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.utils import timezone
from datetime import date
from .project_models import Project
from .project_image_models import ProjectImage
from .models import Lead
import json
import requests

def projects_list(request):
    projects = Project.objects.all()
    context = {
        'projects': projects
    }
    return render(request, 'leads/projects_list_crm.html', context)

def project_leads(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    leads = project.get_leads()
    
    # Get AI agents
    from .ai_calling_models import AICallingAgent
    ai_agents = AICallingAgent.objects.filter(is_active=True)
    
    # Check if user is admin (superuser or admin role)
    is_team_member = request.session.get('is_team_member', False)
    team_member_name = request.session.get('team_member_name', '')
    is_admin = (request.user.is_superuser or 
                team_member_name == 'ADMIN USER' or 
                (hasattr(request.user, 'team_member') and request.user.team_member.role == 'Admin'))
    
    # Only filter if user is team member AND not admin
    if is_team_member and not is_admin:
        team_member_id = request.session.get('team_member_id')
        if team_member_id:
            from .models import TeamMember
            try:
                team_member = TeamMember.objects.get(id=team_member_id)
                team_members = team_member.get_all_team_members()
                team_member_ids = [tm.id for tm in team_members]
                leads = leads.filter(assignment__assigned_to__id__in=team_member_ids)
            except TeamMember.DoesNotExist:
                leads = leads.none()
    
    # Pagination
    paginator = Paginator(leads, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get today's leads count, excluding already called numbers
    today = date.today()
    
    # Get all numbers called today (from CallLog)
    from .models import CallLog
    called_today_raw = CallLog.objects.filter(
        initiated_at__date=today,
        call_type__startswith='auto_daily',
        status='initiated'
    ).values_list('phone_number', flat=True)
    
    # Normalize called numbers (both +91 and without +91 formats)
    excluded_numbers = ['919955967814', '917943595065', '+919955967814', '+917943595065']
    for phone in called_today_raw:
        excluded_numbers.append(phone)
        # Add both formats
        if phone.startswith('+91'):
            excluded_numbers.append(phone[3:])  # Remove +91
        elif phone.startswith('91') and len(phone) == 12:
            excluded_numbers.append(f'+{phone}')  # Add +91
        elif len(phone) == 10:
            excluded_numbers.append(f'+91{phone}')  # Add +91
            excluded_numbers.append(f'91{phone}')   # Add 91
    
    todays_leads = project.get_leads().filter(created_time__date=today)
    todays_leads_with_phone = todays_leads.filter(phone_number__isnull=False).exclude(phone_number='').exclude(phone_number__in=excluded_numbers)
    
    # Today's leads by source
    todays_meta_leads = todays_leads_with_phone.filter(source='Meta')
    todays_google_leads = todays_leads_with_phone.filter(source='Google Sheets')
    
    # All leads by source (for auto-calling all)
    all_meta_leads = project.get_leads().filter(source='Meta', phone_number__isnull=False).exclude(phone_number='').exclude(phone_number__in=excluded_numbers)
    all_google_leads = project.get_leads().filter(source='Google Sheets', phone_number__isnull=False).exclude(phone_number='').exclude(phone_number__in=excluded_numbers)
    
    # Source breakdown
    meta_leads = leads.filter(source='Meta').count()
    google_leads = leads.filter(source='Google Sheets').count()
    
    context = {
        'project': project,
        'leads': page_obj,
        'total_leads': leads.count(),
        'all_project_leads': project.get_leads().count(),
        'todays_leads_count': todays_leads_with_phone.count(),
        'todays_meta_leads_count': todays_meta_leads.count(),
        'todays_google_leads_count': todays_google_leads.count(),
        'all_meta_leads_count': all_meta_leads.count(),
        'all_google_leads_count': all_google_leads.count(),
        'meta_leads_count': meta_leads,
        'google_leads_count': google_leads,
        'today_date': today.strftime('%Y-%m-%d'),
        'ai_agents': ai_agents
    }
    return render(request, 'leads/project_leads_crm.html', context)

def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    images = project.images.all()[:5]  # Limit to 5 images
    templates = project.whatsapp_templates.all()
    
    context = {
        'project': project,
        'images': images,
        'templates': templates,
        'can_add_image': images.count() < 5
    }
    return render(request, 'leads/project_detail.html', context)

@csrf_exempt
@require_http_methods(["POST"])
def upload_project_image(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if project.images.count() >= 5:
        messages.error(request, 'Maximum 5 images allowed per project')
        return redirect('project_detail', project_id=project_id)
    
    if 'image' in request.FILES:
        image = request.FILES['image']
        caption = request.POST.get('caption', '')
        order = project.images.count() + 1
        
        ProjectImage.objects.create(
            project=project,
            image=image,
            caption=caption,
            order=order
        )
        messages.success(request, 'Image uploaded successfully')
    
    return redirect('project_detail', project_id=project_id)

@csrf_exempt
@require_http_methods(["POST"])
def upload_project_brochure(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if 'brochure' in request.FILES:
        project.brochure = request.FILES['brochure']
        project.save()
        messages.success(request, 'Brochure uploaded successfully')
    
    return redirect('project_detail', project_id=project_id)

@require_http_methods(["POST"])
def delete_project_image(request, project_id, image_id):
    project = get_object_or_404(Project, id=project_id)
    image = get_object_or_404(ProjectImage, id=image_id, project=project)
    
    image.delete()
    messages.success(request, 'Image deleted successfully')
    
    return redirect('project_detail', project_id=project_id)

def project_edit(request, project_id):
    """Edit project details including description and amenities"""
    project = get_object_or_404(Project, id=project_id)
    
    if request.method == 'POST':
        # Update basic fields
        project.name = request.POST.get('name', '').strip()
        project.code = request.POST.get('code', '').strip()
        project.developer = request.POST.get('developer', '').strip()
        project.location = request.POST.get('location', '').strip()
        project.description = request.POST.get('description', '').strip()
        
        # Process amenities (one per line)
        amenities_text = request.POST.get('amenities', '').strip()
        if amenities_text:
            amenities = [line.strip() for line in amenities_text.split('\n') if line.strip()]
            project.amenities = amenities
        else:
            project.amenities = []
        
        # Process form keywords (comma separated)
        keywords_text = request.POST.get('form_keywords', '').strip()
        if keywords_text:
            keywords = [kw.strip() for kw in keywords_text.split(',') if kw.strip()]
            project.form_keywords = keywords
        else:
            project.form_keywords = []
        
        try:
            project.save()
            messages.success(request, 'Project updated successfully!')
            return redirect('project_detail', project_id=project_id)
        except Exception as e:
            messages.error(request, f'Error updating project: {str(e)}')
    
    context = {
        'project': project
    }
    return render(request, 'leads/project_edit.html', context)

@csrf_exempt
@require_http_methods(["POST"])
def delete_project(request, project_id):
    """Delete a project"""
    project = get_object_or_404(Project, id=project_id)
    project_name = project.name
    project.delete()
    messages.success(request, f'Project "{project_name}" deleted successfully')
    return redirect('projects_list')

def project_create(request):
    """Create a new project"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        code = request.POST.get('code', '').strip()
        developer = request.POST.get('developer', '').strip()
        location = request.POST.get('location', '').strip()
        description = request.POST.get('description', '').strip()
        
        if not all([name, code, developer, location]):
            messages.error(request, 'Please fill all required fields')
            return render(request, 'leads/project_create.html')
        
        if Project.objects.filter(code=code).exists():
            messages.error(request, f'Project with code "{code}" already exists')
            return render(request, 'leads/project_create.html', {'form_data': request.POST})
        
        amenities_text = request.POST.get('amenities', '').strip()
        amenities = [line.strip() for line in amenities_text.split('\n') if line.strip()] if amenities_text else []
        
        keywords_text = request.POST.get('form_keywords', '').strip()
        keywords = [kw.strip() for kw in keywords_text.split(',') if kw.strip()] if keywords_text else []
        
        try:
            project = Project.objects.create(
                name=name,
                code=code,
                developer=developer,
                location=location,
                description=description,
                amenities=amenities,
                form_keywords=keywords
            )
            messages.success(request, f'Project "{project.name}" created successfully!')
            return redirect('project_detail', project_id=project.id)
        except Exception as e:
            messages.error(request, f'Error creating project: {str(e)}')
    
    return render(request, 'leads/project_create.html')
@csrf_exempt
def start_auto_calling(request, project_id):
    """Start auto-calling today's leads for a project"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    project = get_object_or_404(Project, id=project_id)
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            source_filter = data.get('source', 'all')
            agent_id = data.get('agent_id')
            from_date = data.get('from_date')
            to_date = data.get('to_date')
        else:
            source_filter = request.POST.get('source', 'all')
            agent_id = request.POST.get('agent_id')
            from_date = None
            to_date = None
    except Exception as e:
        print(f"Error parsing request: {e}")
        source_filter = 'all'
        agent_id = None
        from_date = None
        to_date = None
    
    # Get today's leads with phone numbers, excluding already called numbers
    today = date.today()
    
    # Get all numbers called today (from CallLog)
    from .models import CallLog
    called_today_raw = CallLog.objects.filter(
        initiated_at__date=today,
        call_type__startswith='auto_daily',
        status='initiated'
    ).values_list('phone_number', flat=True)
    
    # Normalize called numbers (both +91 and without +91 formats)
    excluded_numbers = ['919955967814', '917943595065', '+919955967814', '+917943595065']
    for phone in called_today_raw:
        excluded_numbers.append(phone)
        # Add both formats
        if phone.startswith('+91'):
            excluded_numbers.append(phone[3:])  # Remove +91
        elif phone.startswith('91') and len(phone) == 12:
            excluded_numbers.append(f'+{phone}')  # Add +91
        elif len(phone) == 10:
            excluded_numbers.append(f'+91{phone}')  # Add +91
            excluded_numbers.append(f'91{phone}')   # Add 91
    
    # Handle date range or today's leads
    if from_date and to_date:
        from datetime import datetime
        from django.utils import timezone as django_timezone
        
        # Parse dates
        from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
        to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()
        
        print(f"🔍 DEBUG: Searching for leads between {from_date_obj} and {to_date_obj}")
        
        # Get leads in date range with phone numbers
        todays_leads = project.get_leads().filter(
            created_time__date__gte=from_date_obj,
            created_time__date__lte=to_date_obj,
            phone_number__isnull=False
        ).exclude(phone_number='').exclude(phone_number__in=excluded_numbers)
        
        print(f"🔍 DEBUG: Found {todays_leads.count()} leads in date range before source filter")
        
        # Remove '_range' suffix if present
        if '_range' in source_filter:
            source_filter = source_filter.replace('_range', '')
    else:
        todays_leads = project.get_leads().filter(
            created_time__date=today,
            phone_number__isnull=False
        ).exclude(phone_number='').exclude(phone_number__in=excluded_numbers)
    
    # Filter by source if specified
    if source_filter == 'meta':
        todays_leads = todays_leads.filter(source='Meta')
        print(f"🔍 DEBUG: After Meta filter: {todays_leads.count()} leads")
    elif source_filter == 'google':
        todays_leads = todays_leads.filter(source='Google Sheets')
        print(f"🔍 DEBUG: After Google filter: {todays_leads.count()} leads")
        
        # Debug: Show some sample Google leads in range
        if todays_leads.count() == 0:
            print("🔍 DEBUG: No Google leads found. Checking all Google leads in project...")
            all_google_in_project = project.get_leads().filter(source='Google Sheets')
            print(f"🔍 DEBUG: Total Google leads in project: {all_google_in_project.count()}")
            
            if from_date and to_date:
                google_in_range = all_google_in_project.filter(
                    created_time__date__gte=from_date_obj,
                    created_time__date__lte=to_date_obj
                )
                print(f"🔍 DEBUG: Google leads in date range: {google_in_range.count()}")
                
                for lead in google_in_range[:5]:
                    print(f"🔍 DEBUG: - {lead.full_name}: {lead.phone_number} ({lead.created_time.date()})")
                    
                google_with_phone = google_in_range.filter(phone_number__isnull=False).exclude(phone_number='')
                print(f"🔍 DEBUG: Google leads with phone in range: {google_with_phone.count()}")
                
                for lead in google_with_phone[:5]:
                    excluded_status = "EXCLUDED" if lead.phone_number in excluded_numbers else "AVAILABLE"
                    print(f"🔍 DEBUG: - {lead.full_name}: {lead.phone_number} - {excluded_status}")
                    
    elif source_filter == 'all_meta':
        todays_leads = project.get_leads().filter(source='Meta', phone_number__isnull=False).exclude(phone_number='').exclude(phone_number__in=excluded_numbers)
    elif source_filter == 'all_google':
        todays_leads = project.get_leads().filter(source='Google Sheets', phone_number__isnull=False).exclude(phone_number='').exclude(phone_number__in=excluded_numbers)
    
    print(f"🔍 DEBUG: Final leads count after all filters: {todays_leads.count()}")
    
    if not todays_leads.exists():
        source_text = f" ({source_filter} leads)" if source_filter != 'all' else ""
        date_text = f" for {from_date} to {to_date}" if from_date and to_date else " for today"
        
        # Additional debug info
        debug_info = ""
        if from_date and to_date and source_filter == 'google':
            total_google = project.get_leads().filter(source='Google Sheets').count()
            google_in_range = project.get_leads().filter(
                source='Google Sheets',
                created_time__date__gte=from_date_obj,
                created_time__date__lte=to_date_obj
            ).count()
            debug_info = f" (Found {google_in_range} Google leads in range, {total_google} total Google leads)"
        
        return JsonResponse({
            'success': False,
            'message': f'No leads with phone numbers found{date_text}{source_text}{debug_info}'
        })
    
    # Call Karo AI configuration
    api_key = "bc422db39aa327234a911dd901accfcfa975623ee84c65c83aae9c4f844ffdb8"
    
    # Use provided agent_id or fallback to default
    if not agent_id:
        agent_id = "69294d3d2cc1373b1f3a3972"
    success_count = 0
    failed_count = 0
    
    print(f"\n{'='*60}")
    if from_date and to_date:
        print(f"🤖 AUTO-CALLING DATE RANGE LEADS - {project.name} ({source_filter.upper()})")
        print(f"📅 Date Range: {from_date} to {to_date}")
    else:
        print(f"🤖 AUTO-CALLING TODAY'S LEADS - {project.name} ({source_filter.upper()})")
        print(f"📅 Date: {today}")
    print(f"{'='*60}")
    print(f"📊 Total leads to call: {todays_leads.count()}")
    print(f"📞 Already called today: {len(called_today_raw)}")
    print(f"🚫 Total excluded numbers: {len(excluded_numbers)}")
    print(f"🎯 Agent ID: {agent_id}")
    print(f"🔑 API Key: {api_key[:20]}...")
    print(f"📋 Source Filter: {source_filter}")
    
    # Debug: Show called numbers
    if called_today_raw:
        print(f"\n📄 Called numbers today:")
        for phone in called_today_raw:
            print(f"  - {phone}")
    
    print(f"{'='*60}")
    
    for lead in todays_leads:
        try:
            # Clean and format phone number properly
            original_phone = lead.phone_number
            phone = lead.phone_number.strip()
            
            # Extract only digits
            digits_only = ''.join(filter(str.isdigit, phone))
            
            # Take last 10 digits (right to left)
            if len(digits_only) >= 10:
                phone = f"+91{digits_only[-10:]}"
            else:
                print(f"❌ SKIPPING - Invalid phone format: {original_phone} (only {len(digits_only)} digits)")
                failed_count += 1
                continue
            
            print(f"\n📞 Calling: {lead.full_name} ({phone})")
            print(f"💰 Budget: {lead.budget or 'Not specified'}")
            
            # Use official API format with proper metadata
            payload = {
                "to_number": phone,
                "agent_id": agent_id,
                "metadata": {
                    "name": lead.full_name or "Unknown",
                    "source": f"auto_call_today_{source_filter}",
                    "project": project.name,
                    "campaign_type": f"daily_auto_call_{source_filter}",
                    "lead_source": lead.source,
                    "budget": lead.budget or "Not specified",
                    "city": lead.city or "Unknown"
                },
                "priority": 1,
                "language": "hi"
            }
            
            # First attempt
            response = requests.post(
                "https://api.callkaro.ai/call/outbound",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-API-KEY": api_key
                },
                timeout=10
            )
            
            print(f"📡 API Response Status: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
            if response.status_code == 200:
                api_response = response.json()
                call_sid = api_response.get('call_sid', '')
                print(f"✅ SUCCESS: {api_response}")
                success_count += 1
                
                # Log the call
                from .models import CallLog, TeamMember
                try:
                    admin_user = TeamMember.objects.filter(role='Admin').first() or TeamMember.objects.first()
                    CallLog.objects.create(
                        lead=lead,
                        team_member=admin_user,
                        phone_number=phone,
                        call_type=f'auto_daily_{source_filter}',
                        status='initiated',
                        call_sid=call_sid
                    )
                    print(f"📝 Call logged for {lead.full_name}")
                except Exception as log_error:
                    print(f"⚠️ Failed to log call: {log_error}")
                
                # Update lead stage
                lead.stage = 'contacted'
                lead.save()
            else:
                print(f"❌ FAILED - Attempting redial...")
                # Redial attempt
                import time
                time.sleep(2)
                
                # Use same redial payload (NO NAME)
                redial_payload = {
                    "to_number": phone,
                    "agent_id": agent_id,
                    "metadata": {
                        "source": f"auto_call_redial_{source_filter}",
                        "project": project.name,
                        "campaign_type": f"daily_auto_call_retry_{source_filter}",
                        "lead_source": lead.source
                    },
                    "priority": 1
                }
                
                redial_response = requests.post(
                    "https://api.callkaro.ai/call/outbound",
                    json=redial_payload,
                    headers={
                        "Content-Type": "application/json",
                        "X-API-KEY": api_key
                    },
                    timeout=10
                )
                
                print(f"🔄 REDIAL Response Status: {redial_response.status_code}")
                print(f"📄 Redial Response: {redial_response.text}")
                
                if redial_response.status_code == 200:
                    redial_api_response = redial_response.json()
                    redial_call_sid = redial_api_response.get('call_sid', '')
                    print(f"✅ REDIAL SUCCESS: {redial_api_response}")
                    success_count += 1
                    
                    # Log the redial call
                    from .models import CallLog, TeamMember
                    try:
                        admin_user = TeamMember.objects.filter(role='Admin').first() or TeamMember.objects.first()
                        CallLog.objects.create(
                            lead=lead,
                            team_member=admin_user,
                            phone_number=phone,
                            call_type=f'auto_daily_{source_filter}',
                            status='initiated',
                            call_sid=redial_call_sid
                        )
                        print(f"📝 Redial call logged for {lead.full_name}")
                    except Exception as log_error:
                        print(f"⚠️ Failed to log redial call: {log_error}")
                    
                    lead.stage = 'contacted'
                    lead.save()
                else:
                    print(f"❌ REDIAL ALSO FAILED")
                    failed_count += 1
                
        except Exception as e:
            print(f"💥 EXCEPTION: {str(e)}")
            failed_count += 1
    
    print(f"\n{'='*60}")
    print(f"📊 AUTO-CALLING COMPLETE")
    print(f"✅ Success: {success_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"{'='*60}\n")
    
    source_text = f" ({source_filter} leads)" if source_filter != 'all' else ""
    return JsonResponse({
        'success': True,
        'message': f'Auto-calling initiated for {success_count}{source_text}. {failed_count} failed.',
        'success_count': success_count,
        'failed_count': failed_count,
        'total_processed': success_count + failed_count,
        'source_filter': source_filter
    })

@csrf_exempt
def call_single_lead(request, project_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        data = json.loads(request.body)
        lead_id = data.get('lead_id')
        agent_id = data.get('agent_id')  # Get selected agent
        
        lead = get_object_or_404(Lead, id=lead_id)
        
        if not lead.phone_number:
            return JsonResponse({'success': False, 'error': 'No phone number'})
        
        # Use CallKaro API
        api_key = "bc422db39aa327234a911dd901accfcfa975623ee84c65c83aae9c4f844ffdb8"
        
        # Use provided agent_id or fallback to default
        if not agent_id:
            agent_id = "69294d3d2cc1373b1f3a3972"
        
        project = get_object_or_404(Project, id=project_id)
        
        # Clean and format phone number
        phone = lead.phone_number.strip()
        digits_only = ''.join(filter(str.isdigit, phone))
        
        if len(digits_only) >= 10:
            phone = f"+91{digits_only[-10:]}"
        else:
            return JsonResponse({
                'success': False,
                'error': f'Invalid phone number format'
            })
        
        payload = {
            "to_number": phone,
            "agent_id": agent_id,
            "metadata": {
                "name": lead.full_name or "Unknown",
                "source": "manual_call",
                "project": project.name,
                "lead_source": lead.source,
                "budget": lead.budget or "Not specified",
                "city": lead.city or "Unknown"
            },
            "priority": 1,
            "language": "hi"
        }
        
        response = requests.post(
            "https://api.callkaro.ai/call/outbound",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "X-API-KEY": api_key
            },
            timeout=10
        )
        
        if response.status_code == 200:
            # Log the call
            from .models import CallLog, TeamMember
            admin_user = TeamMember.objects.filter(role='Admin').first() or TeamMember.objects.first()
            CallLog.objects.create(
                lead=lead,
                team_member=admin_user,
                phone_number=phone,
                call_type='manual_single',
                status='initiated'
            )
            
            return JsonResponse({
                'success': True,
                'lead_name': lead.full_name,
                'phone': phone
            })
        else:
            return JsonResponse({
                'success': False,
                'error': f'Call failed: {response.status_code}'
            })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })