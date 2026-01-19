from django.shortcuts import render
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime
from .models import Lead, Project
from .journey_models import LeadJourney, DuplicatePhoneTracker
from .whatsapp_models import WhatsAppMessage
from tata_integration.models import TataCall

def enhanced_leads_list(request):
    from django.core.paginator import Paginator
    
    # Filter leads based on team member session
    if request.session.get('is_team_member'):
        team_member_id = request.session.get('team_member_id')
        if team_member_id:
            from .models import TeamMember
            try:
                team_member = TeamMember.objects.get(id=team_member_id)
                team_members = team_member.get_all_team_members()
                team_member_ids = [tm.id for tm in team_members]
                leads = Lead.objects.filter(assignment__assigned_to__id__in=team_member_ids)
            except TeamMember.DoesNotExist:
                leads = Lead.objects.none()
        else:
            leads = Lead.objects.none()
    elif request.session.get('is_admin'):
        leads = Lead.objects.all()
    else:
        leads = Lead.objects.none()
    
    projects = Project.objects.all()
    
    # Search functionality
    search = request.GET.get('search', '')
    if search:
        leads = leads.filter(
            Q(full_name__icontains=search) |
            Q(phone_number__icontains=search) |
            Q(email__icontains=search) |
            Q(form_name__icontains=search)
        )
    
    # Source filter
    source = request.GET.get('source', '')
    if source == 'meta':
        leads = leads.filter(form_name__icontains='meta')
    elif source == 'google':
        leads = leads.filter(form_name__icontains='google')
    elif source == 'ivr':
        # Filter leads that have IVR calls
        ivr_phones = TataCall.objects.values_list('customer_number', flat=True)
        leads = leads.filter(phone_number__in=ivr_phones)
    
    # Stage filter
    stage = request.GET.get('stage', '')
    if stage:
        leads = leads.filter(stage=stage)
    
    # Date filters
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    if date_from:
        leads = leads.filter(created_time__gte=datetime.strptime(date_from, '%Y-%m-%d'))
    if date_to:
        leads = leads.filter(created_time__lte=datetime.strptime(date_to, '%Y-%m-%d'))
    
    # Project filter
    project_id = request.GET.get('project', '')
    if project_id:
        project = Project.objects.get(id=project_id)
        leads = leads.filter(id__in=project.get_leads().values_list('id', flat=True))
    
    # Duplicate filter
    duplicates = request.GET.get('duplicates', '')
    if duplicates == 'yes':
        # Show only leads with duplicates
        duplicate_trackers = DuplicatePhoneTracker.objects.annotate(
            meta_count=Count('meta_leads')
        ).filter(meta_count__gt=1)
        duplicate_phones = duplicate_trackers.values_list('phone_number', flat=True)
        leads = leads.filter(phone_number__in=duplicate_phones)
    elif duplicates == 'no':
        # Hide duplicates
        duplicate_trackers = DuplicatePhoneTracker.objects.annotate(
            meta_count=Count('meta_leads')
        ).filter(meta_count__gt=1)
        duplicate_phones = duplicate_trackers.values_list('phone_number', flat=True)
        leads = leads.exclude(phone_number__in=duplicate_phones)
    
    # Always consolidate by phone number (except when specifically showing duplicates)
    from collections import defaultdict
    phone_groups = defaultdict(list)
    
    # Convert to list and group by phone number
    all_leads = list(leads.order_by('-created_time'))
    for lead in all_leads:
        phone_groups[lead.phone_number].append(lead)
    
    # Create consolidated leads list
    leads = []
    for phone, phone_leads in phone_groups.items():
        if duplicates == 'yes' and len(phone_leads) == 1:
            # Skip single entries when showing duplicates only
            continue
        elif duplicates == 'no' and len(phone_leads) > 1:
            # Skip duplicates when hiding duplicates
            continue
            
        # Use the latest lead as primary
        primary_lead = phone_leads[0]
        
        # Add consolidated info
        primary_lead.total_submissions = len(phone_leads)
        primary_lead.all_sources = list(set([lead.form_name for lead in phone_leads]))
        primary_lead.first_submission = phone_leads[-1].created_time
        primary_lead.latest_submission = phone_leads[0].created_time
        
        leads.append(primary_lead)
    
    # Add duplicate information to leads
    for lead in leads:
        try:
            lead.duplicate_info = DuplicatePhoneTracker.objects.get(phone_number=lead.phone_number)
        except DuplicatePhoneTracker.DoesNotExist:
            lead.duplicate_info = None
            
        # Add consolidated info if not already present
        if not hasattr(lead, 'total_submissions'):
            same_phone_leads = Lead.objects.filter(phone_number=lead.phone_number).order_by('-created_time')
            lead.total_submissions = same_phone_leads.count()
            lead.all_sources = list(set([l.form_name for l in same_phone_leads]))
            lead.first_submission = same_phone_leads.last().created_time
            lead.latest_submission = same_phone_leads.first().created_time
    
    # Add pagination
    paginator = Paginator(leads, 50)  # 50 leads per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calculate total leads count
    total_leads = len(leads) if isinstance(leads, list) else leads.count()
    
    return render(request, 'leads/enhanced_leads_list.html', {
        'leads': page_obj,
        'projects': projects,
        'total_leads': total_leads,
        'page_obj': page_obj,
        'search': search,
        'source': source,
        'stage': stage,
        'date_from': date_from,
        'date_to': date_to,
        'project_id': project_id,
        'duplicates': duplicates
    })

def create_journey_entry(lead, journey_type, title, description='', source_type='manual', metadata=None):
    """Helper function to create journey entries"""
    LeadJourney.objects.create(
        lead=lead,
        journey_type=journey_type,
        source_type=source_type,
        title=title,
        description=description,
        metadata=metadata or {}
    )

def track_duplicate_phone(phone_number, lead, source_type='meta'):
    """Track duplicate phone numbers across sources"""
    tracker, created = DuplicatePhoneTracker.objects.get_or_create(
        phone_number=phone_number
    )
    
    if source_type == 'meta':
        tracker.meta_leads.add(lead)
    elif source_type == 'google':
        tracker.google_leads.add(lead)
    
    tracker.save()
    return tracker

def sync_ivr_calls_to_duplicates():
    """Sync IVR calls to duplicate tracker"""
    ivr_calls = TataCall.objects.all()
    
    for call in ivr_calls:
        tracker, created = DuplicatePhoneTracker.objects.get_or_create(
            phone_number=call.customer_number
        )
        
        # Add call data to IVR calls list
        call_data = {
            'call_id': call.id,
            'date': call.start_stamp.isoformat() if call.start_stamp else None,
            'duration': call.duration,
            'status': call.status
        }
        
        if call_data not in tracker.ivr_calls:
            tracker.ivr_calls.append(call_data)
            tracker.save()