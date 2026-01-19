from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from datetime import timedelta
from .models import Lead, ScheduledMessage, SourceMapping, ZohoConfig, Property, TeamMember, LeadAssignment, LeadNote, LeadStage, STAGE_CHOICES, LeadTag
from .whatsapp import send_whatsapp_message, get_available_templates
# Import AI views with fallback
try:
    from .ai_views import ai_dashboard, analyze_lead_ai, refresh_ai_insights, generate_ai_recommendations, ai_lead_scoring, ai_stage_prediction, ai_insights_api
except ImportError:
    # Fallback if AI views not available
    def ai_dashboard(request):
        from django.shortcuts import render
        return render(request, 'leads/ai_dashboard.html', {'error': 'AI system not configured'})
    
    def analyze_lead_ai(request):
        from django.http import JsonResponse
        return JsonResponse({'error': 'AI system not configured'})
    
    def refresh_ai_insights(request):
        from django.http import JsonResponse
        return JsonResponse({'error': 'AI system not configured'})
    
    def generate_ai_recommendations(request):
        from django.http import JsonResponse
        return JsonResponse({'error': 'AI system not configured'})
    
    def ai_lead_scoring(request):
        from django.shortcuts import render
        return render(request, 'leads/ai_lead_scoring.html', {'error': 'AI system not configured'})
    
    def ai_stage_prediction(request):
        from django.http import JsonResponse
        return JsonResponse({'error': 'AI system not configured'})
    
    def ai_insights_api(request):
        from django.http import JsonResponse
        return JsonResponse({'error': 'AI system not configured'})
import requests
import json
import time

from django.conf import settings

ACCESS_TOKEN = settings.META_ACCESS_TOKEN
PAGE_ID = settings.META_PAGE_ID

def calculate_lead_analytics():
    from django.db.models import Q, Count, Case, When, IntegerField
    from datetime import timedelta
    import re
    
    # Single query for basic counts
    basic_stats = Lead.objects.aggregate(
        total_leads=Count('id'),
        meta_leads=Count('id', filter=~Q(lead_id__startswith='GF_') & ~Q(lead_id__startswith='GS_')),
        google_leads=Count('id', filter=Q(lead_id__startswith='GF_') | Q(lead_id__startswith='GS_')),
        leads_with_phone=Count('id', filter=~Q(phone_number='') & ~Q(phone_number__isnull=True)),
        converted_leads=Count('id', filter=Q(stage='converted')),
        recent_leads=Count('id', filter=Q(created_time__gte=timezone.now() - timedelta(days=7))),
        complete_leads=Count('id', filter=~Q(full_name='') & ~Q(email='') & ~Q(phone_number='') & 
                           ~Q(full_name__isnull=True) & ~Q(email__isnull=True) & ~Q(phone_number__isnull=True))
    )
    
    # City analysis in single query
    city_analysis = Lead.objects.exclude(city='').exclude(city__isnull=True).values('city').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Budget parsing function
    def parse_budget_fast(budget_str):
        if not budget_str or budget_str.lower().strip() in ['ok', 'good', 'yass', 'multiple', 'na', 'n/a', '']:
            return 0
        try:
            numbers = re.findall(r'\d+', str(budget_str).lower())
            if not numbers: return 0
            amount = float(numbers[0])
            if 'cr' in str(budget_str).lower(): return amount * 100
            elif 'l' in str(budget_str).lower(): return amount
            elif amount > 1000: return amount / 100
            return amount
        except: return 0
    
    # Get leads with budget for analysis
    leads_with_budget = Lead.objects.exclude(budget='').exclude(budget__isnull=True).values_list('budget', 'lead_id')
    
    budget_ranges = {'under_50l': 0, '50l_1cr': 0, '1cr_5cr': 0, '5cr_plus': 0}
    meta_budget_total = 0
    meta_high_budget = 0
    meta_with_budget = 0
    google_with_budget = 0
    
    for budget, lead_id in leads_with_budget:
        budget_lakhs = parse_budget_fast(budget)
        if budget_lakhs > 0:
            if lead_id.startswith('GF_') or lead_id.startswith('GS_'):
                google_with_budget += 1
            else:
                meta_with_budget += 1
                meta_budget_total += budget_lakhs
                if budget_lakhs >= 100:
                    meta_high_budget += 1
            
            if budget_lakhs < 50: budget_ranges['under_50l'] += 1
            elif budget_lakhs < 100: budget_ranges['50l_1cr'] += 1
            elif budget_lakhs < 500: budget_ranges['1cr_5cr'] += 1
            else: budget_ranges['5cr_plus'] += 1
    
    # Google premium count
    google_premium_count = Lead.objects.filter(
        Q(lead_id__startswith='GF_') | Q(lead_id__startswith='GS_'),
        Q(configuration__icontains='cr') | Q(configuration__icontains='premium') | Q(configuration__icontains='luxury')
    ).count()
    
    total = basic_stats['total_leads']
    
    return {
        'total_leads': total,
        'meta_leads_count': basic_stats['meta_leads'],
        'google_leads_count': basic_stats['google_leads'],
        'leads_with_phone': basic_stats['leads_with_phone'],
        'phone_percentage': round((basic_stats['leads_with_phone'] / total * 100) if total > 0 else 0, 1),
        'meta_budget_crores': round(meta_budget_total / 100, 2),
        'meta_high_budget_count': meta_high_budget,
        'google_premium_count': google_premium_count,
        'recent_leads_count': basic_stats['recent_leads'],
        'conversion_rate': round((basic_stats['converted_leads'] / total * 100) if total > 0 else 0, 1),
        'city_analysis': list(city_analysis),
        'budget_ranges': budget_ranges,
        'meta_with_budget': meta_with_budget,
        'google_with_budget': google_with_budget,
        'quality_score': round((basic_stats['complete_leads'] / total * 100) if total > 0 else 0, 1),
        'complete_leads': basic_stats['complete_leads']
    }

def leads_list(request):
    from django.core.paginator import Paginator
    from django.db.models import Q, Count, Case, When, IntegerField
    from datetime import timedelta
    from django.core.cache import cache
    
    # Calculate analytics without cache to avoid cache table error
    analytics = calculate_lead_analytics()
    
    # Admin always sees all leads, team members see only assigned leads
    is_team_member = request.session.get('is_team_member', False)
    team_member_name = request.session.get('team_member_name', '')
    
    # Check if user is admin (superuser or admin role)
    is_admin = (request.user.is_superuser or 
                team_member_name == 'ADMIN USER' or team_member_name == 'admin' or 
                (hasattr(request.user, 'team_member') and request.user.team_member.role == 'Admin'))
    
    # Admin sees all leads, team members see only assigned leads
    if is_admin:
        leads = Lead.objects.select_related('assignment__assigned_to').all()
    elif is_team_member:
        team_member_id = request.session.get('team_member_id')
        if team_member_id:
            try:
                team_member = TeamMember.objects.get(id=team_member_id)
                leads = Lead.objects.filter(
                    assignment__assigned_to=team_member
                ).select_related('assignment__assigned_to')
            except TeamMember.DoesNotExist:
                leads = Lead.objects.none()
        else:
            leads = Lead.objects.none()
    else:
        # Default to all leads if no specific role
        leads = Lead.objects.select_related('assignment__assigned_to').all()
    
    # Filters
    search = request.GET.get('search')
    form_filter = request.GET.get('form')
    source_filter = request.GET.get('source')
    assigned_to = request.GET.get('assigned_to')
    city_filter = request.GET.get('city')
    date_filter = request.GET.get('date_filter')
    ai_analyze = request.GET.get('ai_analyze')
    
    if search:
        leads = leads.filter(
            Q(full_name__icontains=search) | 
            Q(email__icontains=search) | 
            Q(phone_number__icontains=search)
        )
    
    if form_filter:
        leads = leads.filter(form_name__icontains=form_filter)
    
    if source_filter == 'meta':
        leads = leads.exclude(lead_id__startswith='GF_').exclude(lead_id__startswith='GS_')
    elif source_filter == 'google':
        leads = leads.filter(Q(lead_id__startswith='GF_') | Q(lead_id__startswith='GS_'))
    elif source_filter == 'gaur':
        leads = leads.filter(Q(form_name__icontains='gaur') | Q(source__icontains='gaur'))
    
    if assigned_to:
        leads = leads.filter(assignment__assigned_to_id=assigned_to)
    
    if city_filter:
        leads = leads.filter(city__icontains=city_filter)
    
    # Date range filtering
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        from datetime import datetime
        start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
        leads = leads.filter(created_time__date__gte=start_dt)
    
    if end_date:
        from datetime import datetime
        end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
        leads = leads.filter(created_time__date__lte=end_dt)
    
    leads = leads.order_by('-created_time')
    

    
    # Pagination
    paginator = Paginator(leads, 50)
    page = request.GET.get('page')
    leads = paginator.get_page(page)
    
    # Get dropdown data without cache
    forms = list(Lead.objects.values_list('form_name', flat=True).distinct().exclude(form_name=''))
    team_members = list(TeamMember.objects.filter(is_active=True).order_by('name'))
    
    return render(request, 'leads/list_crm.html', {
        'leads': leads,
        'forms': forms,
        'search': search,
        'form_filter': form_filter,
        'source_filter': source_filter,
        'assigned_to': assigned_to,
        'city_filter': city_filter,
        'ai_analyze': ai_analyze,
        'team_members': team_members,
        'start_date': start_date,
        'end_date': end_date,
        **analytics
    })

def lead_detail(request, lead_id):
    from django.shortcuts import get_object_or_404
    from .call_report_models import CallReportRecord
    
    lead = get_object_or_404(Lead, id=lead_id)
    
    # Check if this is an API request (JSON response expected)
    if request.headers.get('Accept') == 'application/json' or request.GET.get('format') == 'json':
        return JsonResponse({
            'success': True,
            'lead': {
                'id': lead.id,
                'full_name': lead.full_name,
                'email': lead.email,
                'phone_number': lead.phone_number,
                'city': lead.city,
                'budget': lead.budget,
                'source': lead.source,
                'form_name': lead.form_name,
                'configuration': lead.configuration,
                'created_time': lead.created_time.isoformat() if lead.created_time else None,
                'stage': getattr(lead, 'stage', 'new')
            }
        })
    
    # Regular HTML response
    notes = lead.notes.all().order_by('-created_at')
    team_members = TeamMember.objects.filter(is_active=True).order_by('name')
    
    # Get call records for this lead
    call_records = CallReportRecord.objects.filter(matched_lead=lead).order_by('-id')[:10]
    
    return render(request, 'leads/detail.html', {
        'lead': lead,
        'notes': notes,
        'team_members': team_members,
        'stage_choices': STAGE_CHOICES,
        'call_records': call_records
    })

def daily_sync_analysis_api(request):
    from django.db.models import Count, Q
    from datetime import datetime, timedelta
    from django.utils import timezone
    
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    week_ago = today - timedelta(days=7)
    
    # Get daily breakdown for last 7 days
    daily_data = []
    sync_issues = []
    
    for i in range(7):
        date = today - timedelta(days=i)
        
        # Count leads by source for this date
        meta_leads = Lead.objects.filter(
            created_time__date=date
        ).exclude(
            Q(lead_id__startswith='GF_') | Q(lead_id__startswith='GS_')
        ).count()
        
        google_leads = Lead.objects.filter(
            created_time__date=date
        ).filter(
            Q(lead_id__startswith='GF_') | Q(lead_id__startswith='GS_')
        ).count()
        
        total = meta_leads + google_leads
        
        # Get top forms for this date
        top_forms = Lead.objects.filter(
            created_time__date=date
        ).values('form_name').annotate(
            count=Count('form_name')
        ).order_by('-count')[:3]
        
        form_names = [f"{form['form_name'][:20]}({form['count']})" for form in top_forms if form['form_name']]
        
        daily_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'meta_leads': meta_leads,
            'google_leads': google_leads,
            'total': total,
            'top_forms': form_names
        })
        
        # Check for potential issues
        if total == 0 and i < 2:  # No leads in last 2 days
            sync_issues.append(f"No leads synced on {date.strftime('%Y-%m-%d')}")
        elif total < 5 and i == 0:  # Very few leads today
            sync_issues.append(f"Only {total} leads today - check if sync is running")
    
    # Calculate stats
    total_leads = Lead.objects.count()
    today_leads = Lead.objects.filter(created_time__date=today).count()
    yesterday_leads = Lead.objects.filter(created_time__date=yesterday).count()
    
    # 7-day average
    week_leads = Lead.objects.filter(created_time__date__gte=week_ago).count()
    avg_daily = week_leads / 7
    
    # Additional checks
    if today_leads == 0:
        sync_issues.append("No leads synced today - check auto-sync status")
    if avg_daily < 10:
        sync_issues.append(f"Low daily average ({avg_daily:.1f}) - may indicate sync issues")
    
    return JsonResponse({
        'total_leads': total_leads,
        'today_leads': today_leads,
        'yesterday_leads': yesterday_leads,
        'avg_daily': avg_daily,
        'daily_breakdown': daily_data,
        'sync_issues': sync_issues
    })

def dashboard(request):
    from django.db.models import Count, Q
    from datetime import timedelta
    
    total_leads = Lead.objects.count()
    meta_leads_count = Lead.objects.exclude(lead_id__startswith='GF_').exclude(lead_id__startswith='GS_').count()
    google_leads_count = Lead.objects.filter(Q(lead_id__startswith='GF_') | Q(lead_id__startswith='GS_')).count()
    
    return render(request, 'leads/dashboard.html', {
        'total_leads': total_leads,
        'meta_leads_count': meta_leads_count,
        'google_leads_count': google_leads_count,
    })

@csrf_exempt
def sync_leads(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'})
    
    try:
        if not ACCESS_TOKEN or not PAGE_ID:
            return JsonResponse({'error': 'Meta API credentials not configured in .env'})
        
        # Get all forms from Meta
        forms_url = f"https://graph.facebook.com/v21.0/{PAGE_ID}/leadgen_forms"
        forms_response = requests.get(forms_url, params={'access_token': ACCESS_TOKEN})
        
        if forms_response.status_code != 200:
            return JsonResponse({'error': f'Meta API error: {forms_response.text}'})
        
        forms_data = forms_response.json()
        forms = forms_data.get('data', [])
        
        if not forms:
            return JsonResponse({'error': 'No forms found in Meta account'})
        
        total_synced = 0
        today_leads = 0
        today = timezone.now().date()
        skipped = 0
        
        # Sync leads from each form (with pagination for ALL historical leads)
        for form in forms:
            form_id = form['id']
            form_name = form.get('name', 'Unknown Form')
            
            # Fetch ALL leads with pagination
            leads_url = f"https://graph.facebook.com/v21.0/{form_id}/leads"
            params = {
                'access_token': ACCESS_TOKEN,
                'fields': 'id,created_time,field_data',
                'limit': 500  # Max per page
            }
            
            while leads_url:
                leads_response = requests.get(leads_url, params=params)
                
                if leads_response.status_code != 200:
                    break
                
                leads_data = leads_response.json()
                
                for lead_data in leads_data.get('data', []):
                    lead_id = lead_data.get('id')
                    
                    # Skip if already exists
                    if Lead.objects.filter(lead_id=lead_id).exists():
                        skipped += 1
                        continue
                    
                    # Parse field data
                    field_data = {item['name']: item['values'][0] for item in lead_data.get('field_data', [])}
                    
                    # Parse created_time from Meta
                    created_time_str = lead_data.get('created_time')
                    if created_time_str:
                        created_time = parse_datetime(created_time_str)
                    else:
                        created_time = timezone.now()
                    
                    # Create lead
                    lead = Lead.objects.create(
                        lead_id=lead_id,
                        full_name=field_data.get('full_name', ''),
                        email=field_data.get('email', ''),
                        phone_number=field_data.get('phone_number', ''),
                        city=field_data.get('city', ''),
                        budget=field_data.get('budget', '') or field_data.get('what_is_your_budget_range?', ''),
                        source='Meta',
                        form_name=form_name,
                        configuration=field_data.get('configuration', ''),
                        created_time=created_time
                    )
                    
                    total_synced += 1
                    if lead.created_time.date() == today:
                        today_leads += 1
                
                # Check for next page
                paging = leads_data.get('paging', {})
                leads_url = paging.get('next')
                params = {}  # Next URL already has params
        
        return JsonResponse({
            'success': True,
            'message': f'Synced {total_synced} new leads (skipped {skipped} existing)',
            'total_synced': total_synced,
            'today_leads': today_leads,
            'skipped': skipped
        })
        
    except Exception as e:
        import traceback
        return JsonResponse({'error': str(e), 'traceback': traceback.format_exc()})

def meta_leads(request):
    from django.core.paginator import Paginator
    leads = Lead.objects.filter(source='Meta').order_by('-created_time')
    
    # Check if user is admin (superuser or admin role)
    is_team_member = request.session.get('is_team_member', False)
    team_member_name = request.session.get('team_member_name', '')
    is_admin = (request.user.is_superuser or 
                team_member_name == 'ADMIN USER' or team_member_name == 'admin' or 
                (hasattr(request.user, 'team_member') and request.user.team_member.role == 'Admin'))
    
    # Only filter if user is team member AND not admin
    if is_team_member and not is_admin:
        team_member_id = request.session.get('team_member_id')
        if team_member_id:
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
    
    context = {
        'leads': page_obj,
        'total_leads': leads.count(),
        'source_type': 'Meta',
        'page_title': 'Meta Leads'
    }
    return render(request, 'leads/source_leads.html', context)

def google_leads(request):
    from django.core.paginator import Paginator
    leads = Lead.objects.filter(source='Google Sheets').order_by('-created_time')
    
    # Check if user is admin (superuser or admin role)
    is_team_member = request.session.get('is_team_member', False)
    team_member_name = request.session.get('team_member_name', '')
    is_admin = (request.user.is_superuser or 
                team_member_name == 'ADMIN USER' or team_member_name == 'admin' or 
                (hasattr(request.user, 'team_member') and request.user.team_member.role == 'Admin'))
    
    # Only filter if user is team member AND not admin
    if is_team_member and not is_admin:
        team_member_id = request.session.get('team_member_id')
        if team_member_id:
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
    
    context = {
        'leads': page_obj,
        'total_leads': leads.count(),
        'source_type': 'Google Sheets',
        'page_title': 'Google Sheets Leads'
    }
    return render(request, 'leads/source_leads.html', context)

def whatsapp_page(request):
    from .project_models import Project
    from .whatsapp_models import WhatsAppTemplate
    from .drip_campaign_models import DripCampaign
    from django.core.paginator import Paginator
    from django.db.models import Q
    
    search = request.GET.get('search', '')
    form_filter = request.GET.get('form', '')
    
    leads = Lead.objects.filter(phone_number__isnull=False).exclude(phone_number='').order_by('-created_time')
    
    if search:
        leads = leads.filter(
            Q(full_name__icontains=search) |
            Q(phone_number__icontains=search) |
            Q(email__icontains=search)
        )
    
    if form_filter:
        leads = leads.filter(form_name=form_filter)
    
    paginator = Paginator(leads, 50)
    page = request.GET.get('page', 1)
    leads = paginator.get_page(page)
    
    projects = Project.objects.all().order_by('name')
    templates = WhatsAppTemplate.objects.all().order_by('project__name', 'order')
    drip_campaigns = DripCampaign.objects.filter(status='active').order_by('-created_at')
    forms = Lead.objects.filter(phone_number__isnull=False).exclude(phone_number='').values_list('form_name', flat=True).distinct()
    
    return render(request, 'leads/whatsapp.html', {
        'leads': leads,
        'projects': projects,
        'templates': templates,
        'drip_campaigns': drip_campaigns,
        'forms': forms,
        'search': search,
        'form_filter': form_filter,
        'total_leads': Lead.objects.filter(phone_number__isnull=False).exclude(phone_number='').count()
    })

def export_leads(request):
    return JsonResponse({'message': 'Export functionality'})

def add_lead(request):
    if request.method == 'POST':
        try:
            # Create new lead from form data
            lead = Lead.objects.create(
                full_name=request.POST.get('full_name'),
                phone_number=request.POST.get('phone_number'),
                email=request.POST.get('email', ''),
                city=request.POST.get('city', ''),
                budget=request.POST.get('budget', ''),
                source=request.POST.get('source', 'Offline'),
                form_name=request.POST.get('form_name', 'Manual Entry'),
                configuration=request.POST.get('configuration', ''),
                lead_id=f"MANUAL_{timezone.now().strftime('%Y%m%d_%H%M%S')}",
                created_time=timezone.now()
            )
            
            from django.shortcuts import redirect
            return redirect('/leads/')
            
        except Exception as e:
            from django.contrib import messages
            messages.error(request, f'Error adding lead: {str(e)}')
    
    return render(request, 'leads/add_lead.html')

def my_leads(request):
    return render(request, 'leads/my_leads.html', {'leads': []})

def assign_lead(request):
    return JsonResponse({'message': 'Assign lead functionality'})

def update_lead_stage(request):
    return JsonResponse({'message': 'Update stage functionality'})

def add_lead_note(request):
    return JsonResponse({'message': 'Add note functionality'})

def lead_calls(request, lead_id):
    return render(request, 'leads/call_panel.html', {'lead_id': lead_id})

def send_whatsapp(request):
    return JsonResponse({'message': 'WhatsApp functionality'})

def google_leads_webhook(request):
    return JsonResponse({'message': 'Google webhook'})

def test_google_webhook(request):
    return JsonResponse({'message': 'Test webhook'})

def import_google_sheet_leads(request):
    return JsonResponse({'message': 'Import Google sheets'})

def sync_google_sheet(request):
    return JsonResponse({'message': 'Sync Google sheet'})

def refresh_google_leads(request):
    return JsonResponse({'message': 'Refresh Google leads'})

def sheet_config(request):
    return render(request, 'leads/sheet_config.html')

def save_sheet_config(request):
    return JsonResponse({'message': 'Save sheet config'})

def test_sheet_connection(request):
    return JsonResponse({'message': 'Test sheet connection'})

# Add missing functions that were in the original file
def debug_leads(request):
    return JsonResponse({'message': 'Debug leads'})

def schedule_whatsapp(request):
    return JsonResponse({'message': 'Schedule WhatsApp'})

def process_scheduled_messages(request):
    return JsonResponse({'message': 'Process scheduled messages'})

def check_scheduled_messages(request):
    return JsonResponse({'message': 'Check scheduled messages'})

def auto_process_scheduled(request):
    return JsonResponse({'message': 'Auto process scheduled'})

def scheduled_messages_page(request):
    return render(request, 'leads/scheduled_messages.html')

def source_mapping_page(request):
    return render(request, 'leads/source_mapping.html')

def save_source_mapping(request):
    return JsonResponse({'message': 'Save source mapping'})

def auto_sync_status(request):
    return JsonResponse({'message': 'Auto sync status'})

def zoho_config_page(request):
    return render(request, 'leads/zoho_config.html')

def save_zoho_config(request):
    return JsonResponse({'message': 'Save Zoho config'})

def zoho_auth(request):
    return JsonResponse({'message': 'Zoho auth'})

def zoho_callback(request):
    return JsonResponse({'message': 'Zoho callback'})

def reset_zoho_config(request):
    return JsonResponse({'message': 'Reset Zoho config'})

def zoho_status_page(request):
    return render(request, 'leads/zoho_status.html')

def test_zoho_connection(request):
    return JsonResponse({'message': 'Test Zoho connection'})

def sync_lead_to_zoho(request):
    return JsonResponse({'message': 'Sync lead to Zoho'})

def refresh_zoho_token_endpoint(request):
    return JsonResponse({'message': 'Refresh Zoho token'})

def properties_page(request):
    return render(request, 'leads/properties.html')

def property_mapping_page(request):
    return render(request, 'leads/property_mapping.html')

def date_range_analysis(request):
    return JsonResponse({'message': 'Date range analysis'})

def check_meta_forms(request):
    return JsonResponse({'message': 'Check Meta forms'})

def check_todays_leads(request):
    """Check today's leads and form breakdown"""
    try:
        from datetime import date
        from django.db.models import Count
        
        today = date.today()
        
        # Get today's leads
        todays_leads = Lead.objects.filter(created_time__date=today)
        total_today = todays_leads.count()
        
        # Get form breakdown for today
        form_breakdown = todays_leads.values('form_name').annotate(
            count=Count('form_name')
        ).order_by('-count')[:10]
        
        # Get recent leads (last 5)
        recent_leads = todays_leads.order_by('-created_time')[:5].values(
            'full_name', 'form_name', 'created_time', 'phone_number'
        )
        
        return JsonResponse({
            'success': True,
            'today_date': today.strftime('%Y-%m-%d'),
            'todays_leads_count': total_today,
            'form_breakdown': list(form_breakdown),
            'recent_leads': list(recent_leads)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)})

def sync_gaur_acp_leads(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'})
    
    try:
        from datetime import date, timedelta
        from django.db.models import Count, Q
        
        yesterday = date.today() - timedelta(days=1)
        yesterday_leads = Lead.objects.filter(created_time__date=yesterday)
        total_yesterday = yesterday_leads.count()
        
        form_breakdown = yesterday_leads.values('form_name').annotate(
            count=Count('form_name')
        ).order_by('-count')[:10]
        
        return JsonResponse({
            'success': True,
            'message': f'Yesterday analysis complete',
            'total_synced': total_yesterday,
            'yesterday_date': yesterday.strftime('%Y-%m-%d'),
            'form_breakdown': list(form_breakdown)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)})

def call_analytics(request):
    return render(request, 'leads/call_analytics.html')

def tata_data(request):
    return render(request, 'leads/tata_data.html')

def tagged_leads(request):
    return render(request, 'leads/tagged_leads.html')

def interest_analytics(request):
    return render(request, 'leads/interest_analytics.html')

@csrf_exempt
def initiate_call(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        data = json.loads(request.body)
        lead_id = data.get('lead_id')
        
        if not lead_id:
            return JsonResponse({'error': 'Lead ID required'}, status=400)
        
        try:
            lead = Lead.objects.get(id=lead_id)
        except Lead.DoesNotExist:
            return JsonResponse({'error': 'Lead not found'}, status=404)
        
        return JsonResponse({
            'success': True,
            'message': 'Call initiated successfully',
            'lead': {
                'id': lead.id,
                'name': lead.full_name,
                'phone': lead.phone_number
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def generate_message(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        data = json.loads(request.body)
        lead_id = data.get('lead_id')
        
        if not lead_id:
            return JsonResponse({'error': 'Lead ID required'}, status=400)
        
        try:
            lead = Lead.objects.get(id=lead_id)
        except Lead.DoesNotExist:
            return JsonResponse({'error': 'Lead not found'}, status=404)
        
        message = f"Hi {lead.full_name}, thank you for your interest in our project. We have received your inquiry and our team will contact you shortly."
        
        return JsonResponse({
            'success': True,
            'message': message,
            'lead_name': lead.full_name
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def lead_detail_api(request, lead_id):
    try:
        lead = Lead.objects.get(id=lead_id)
        
        return JsonResponse({
            'success': True,
            'lead': {
                'id': lead.id,
                'full_name': lead.full_name,
                'email': lead.email,
                'phone_number': lead.phone_number,
                'city': lead.city,
                'budget': lead.budget,
                'source': lead.source,
                'form_name': lead.form_name,
                'configuration': lead.configuration,
                'created_time': lead.created_time.isoformat() if lead.created_time else None,
                'stage': getattr(lead, 'stage', 'new')
            }
        })
        
    except Lead.DoesNotExist:
        return JsonResponse({'error': 'Lead not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def generate_follow_up(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        data = json.loads(request.body)
        lead_id = data.get('lead_id')
        
        if not lead_id:
            return JsonResponse({'error': 'Lead ID required'}, status=400)
        
        try:
            lead = Lead.objects.get(id=lead_id)
        except Lead.DoesNotExist:
            return JsonResponse({'error': 'Lead not found'}, status=404)
        
        message = f"Hi {lead.full_name}, I hope you're doing well. I wanted to follow up on your interest in our {lead.form_name or 'project'}. Are you available for a quick discussion about your requirements?"
        
        return JsonResponse({
            'success': True,
            'message': message,
            'lead_name': lead.full_name
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def acefone_call(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        data = json.loads(request.body)
        lead_id = data.get('lead_id')
        phone = data.get('phone')
        
        if not lead_id or not phone:
            return JsonResponse({'error': 'Lead ID and phone required'}, status=400)
        
        try:
            lead = Lead.objects.get(id=lead_id)
        except Lead.DoesNotExist:
            return JsonResponse({'error': 'Lead not found'}, status=404)
        
        api_key = "bc422db39aa327234a911dd901accfcfa975623ee84c65c83aae9c4f844ffdb8"
        
        def get_agent_id(lead):
            form_name = (lead.form_name or '').lower()
            if 'gaur' in form_name or 'yamuna' in form_name:
                return "6923ff797a5d5a94d5a5dfcf"
            elif 'au' in form_name or 'realty' in form_name:
                if lead.id % 2 == 0:
                    return "692d5b6ad10e948b7bbfc2db"
                else:
                    return "69294d3d2cc1373b1f3a3972"
            return "692d5b6ad10e948b7bbfc2db"
        
        agent_id = get_agent_id(lead)
        
        if not phone.startswith('+'):
            phone = f"+91{phone}" if len(phone) == 10 else f"+{phone}"
        
        payload = {
            "to_number": phone,
            "agent_id": agent_id,
            "metadata": {
                "name": lead.full_name,
                "city": lead.city or "Unknown",
                "budget": lead.budget or "Not specified",
                "form_name": lead.form_name or "Unknown",
                "lead_id": str(lead.id)
            },
            "priority": 1
        }
        
        headers = {
            "Content-Type": "application/json",
            "X-API-KEY": api_key
        }
        
        print(f"\n{'='*60}")
        print(f"CALL KARO AI - INITIATING CALL")
        print(f"{'='*60}")
        print(f"Lead: {lead.full_name} (ID: {lead.id})")
        print(f"Phone: {phone}")
        print(f"Agent ID: {agent_id}")
        print(f"Project: {lead.form_name or 'Unknown'}")
        
        agent_names = {
            "6923ff797a5d5a94d5a5dfcf": "Gaur Yamuna Agent",
            "692d5b6ad10e948b7bbfc2db": "AU Realty Agent 1", 
            "69294d3d2cc1373b1f3a3972": "AU Realty Agent 2"
        }
        print(f"Agent: {agent_names.get(agent_id, 'Unknown Agent')}")
        print(f"API Key: {api_key[:20]}...")
        print(f"Metadata: {payload['metadata']}")
        print(f"{'='*60}")
        
        try:
            response = requests.post(
                "https://api.callkaro.ai/call/outbound",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            print(f"API Response Status: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                api_response = response.json()
                print(f"SUCCESS: {api_response}")
                
                return JsonResponse({
                    'success': True,
                    'message': f'Call initiated successfully to {phone}',
                    'call_id': api_response.get('call_id', 'unknown'),
                    'lead_name': lead.full_name,
                    'api_response': api_response
                })
            else:
                error_msg = response.text
                print(f"API ERROR: {error_msg}")
                
                return JsonResponse({
                    'success': False,
                    'error': f'Call Karo AI Error: {error_msg}',
                    'status_code': response.status_code
                }, status=400)
                
        except requests.exceptions.Timeout:
            print(f"TIMEOUT: API request timed out")
            return JsonResponse({'error': 'API request timed out'}, status=408)
            
        except requests.exceptions.RequestException as e:
            print(f"CONNECTION ERROR: {str(e)}")
            return JsonResponse({'error': f'Connection error: {str(e)}'}, status=503)
            
        finally:
            print(f"{'='*60}\n")
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        print(f"UNEXPECTED ERROR: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def test_callkaro_agent(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    api_key = "bc422db39aa327234a911dd901accfcfa975623ee84c65c83aae9c4f844ffdb8"
    agent_id = "6923ff797a5d5a94d5a5dfcf"
    
    payload = {
        "to_number": "+919876543210",
        "agent_id": agent_id,
        "metadata": {
            "name": "Test User",
            "test": True
        },
        "priority": 1
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": api_key
    }
    
    print(f"\n{'='*60}")
    print(f"TESTING CALL KARO AI AGENT")
    print(f"{'='*60}")
    print(f"API Key: {api_key[:20]}...")
    print(f"Agent ID: {agent_id}")
    print(f"Test Number: +919876543210")
    print(f"{'='*60}")
    
    try:
        response = requests.post(
            "https://api.callkaro.ai/call/outbound",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            api_response = response.json()
            print(f"AGENT TEST SUCCESS: {api_response}")
            
            return JsonResponse({
                'success': True,
                'message': 'Agent configuration is valid',
                'api_response': api_response
            })
        else:
            print(f"AGENT TEST FAILED: {response.text}")
            
            return JsonResponse({
                'success': False,
                'error': f'Agent test failed: {response.text}',
                'status_code': response.status_code
            })
            
    except Exception as e:
        print(f"AGENT TEST ERROR: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
    finally:
        print(f"{'='*60}\n")

def sync_gaur_acp_leads(request):
    """Sync leads from yesterday specifically"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'})
    
    try:
        from datetime import date, timedelta
        from django.db.models import Count, Q
        
        yesterday = date.today() - timedelta(days=1)
        
        # Get yesterday's leads
        yesterday_leads = Lead.objects.filter(created_time__date=yesterday)
        total_yesterday = yesterday_leads.count()
        
        # Get form breakdown
        form_breakdown = yesterday_leads.values('form_name').annotate(
            count=Count('form_name')
        ).order_by('-count')[:10]
        
        return JsonResponse({
            'success': True,
            'message': f'Yesterday analysis complete',
            'total_synced': total_yesterday,
            'yesterday_date': yesterday.strftime('%Y-%m-%d'),
            'form_breakdown': list(form_breakdown)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)})

def call_analytics(request):
    return render(request, 'leads/call_analytics.html')

def tata_data(request):
    return render(request, 'leads/tata_data.html')

def tagged_leads(request):
    return render(request, 'leads/tagged_leads.html')

def interest_analytics(request):
    return render(request, 'leads/interest_analytics.html')

@csrf_exempt
def initiate_call(request):
    """Initiate a call for a lead"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        data = json.loads(request.body)
        lead_id = data.get('lead_id')
        
        if not lead_id:
            return JsonResponse({'error': 'Lead ID required'}, status=400)
        
        # Get lead details
        try:
            lead = Lead.objects.get(id=lead_id)
        except Lead.DoesNotExist:
            return JsonResponse({'error': 'Lead not found'}, status=404)
        
        # Return success response with lead info
        return JsonResponse({
            'success': True,
            'message': 'Call initiated successfully',
            'lead': {
                'id': lead.id,
                'name': lead.full_name,
                'phone': lead.phone_number
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def generate_message(request):
    """Generate AI message for a lead"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        data = json.loads(request.body)
        lead_id = data.get('lead_id')
        
        if not lead_id:
            return JsonResponse({'error': 'Lead ID required'}, status=400)
        
        # Get lead details
        try:
            lead = Lead.objects.get(id=lead_id)
        except Lead.DoesNotExist:
            return JsonResponse({'error': 'Lead not found'}, status=404)
        
        # Generate a simple message based on lead data
        message = f"Hi {lead.full_name}, thank you for your interest in our project. We have received your inquiry and our team will contact you shortly."
        
        return JsonResponse({
            'success': True,
            'message': message,
            'lead_name': lead.full_name
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def lead_detail_api(request, lead_id):
    """API endpoint for lead details"""
    try:
        lead = Lead.objects.get(id=lead_id)
        
        return JsonResponse({
            'success': True,
            'lead': {
                'id': lead.id,
                'full_name': lead.full_name,
                'email': lead.email,
                'phone_number': lead.phone_number,
                'city': lead.city,
                'budget': lead.budget,
                'source': lead.source,
                'form_name': lead.form_name,
                'configuration': lead.configuration,
                'created_time': lead.created_time.isoformat() if lead.created_time else None,
                'stage': getattr(lead, 'stage', 'new')
            }
        })
        
    except Lead.DoesNotExist:
        return JsonResponse({'error': 'Lead not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
@csrf_exempt
def generate_follow_up(request):
    """Generate AI follow-up message for a lead"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        data = json.loads(request.body)
        lead_id = data.get('lead_id')
        
        if not lead_id:
            return JsonResponse({'error': 'Lead ID required'}, status=400)
        
        try:
            lead = Lead.objects.get(id=lead_id)
        except Lead.DoesNotExist:
            return JsonResponse({'error': 'Lead not found'}, status=404)
        
        # Generate follow-up message
        message = f"Hi {lead.full_name}, I hope you're doing well. I wanted to follow up on your interest in our {lead.form_name or 'project'}. Are you available for a quick discussion about your requirements?"
        
        return JsonResponse({
            'success': True,
            'message': message,
            'lead_name': lead.full_name
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def acefone_call(request):
    """Initiate Call Karo AI call"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        data = json.loads(request.body)
        lead_id = data.get('lead_id')
        phone = data.get('phone')
        
        if not lead_id or not phone:
            return JsonResponse({'error': 'Lead ID and phone required'}, status=400)
        
        try:
            lead = Lead.objects.get(id=lead_id)
        except Lead.DoesNotExist:
            return JsonResponse({'error': 'Lead not found'}, status=404)
        
        # Call Karo AI API integration
        api_key = "bc422db39aa327234a911dd901accfcfa975623ee84c65c83aae9c4f844ffdb8"
        
        # Select agent based on project/form
        def get_agent_id(lead):
            form_name = (lead.form_name or '').lower()
            
            # Gaur Yamuna agent
            if 'gaur' in form_name or 'yamuna' in form_name:
                return "6923ff797a5d5a94d5a5dfcf"
            
            # AU Realty agents (rotate between 2)
            elif 'au' in form_name or 'realty' in form_name:
                if lead.id % 2 == 0:
                    return "692d5b6ad10e948b7bbfc2db"
                else:
                    return "69294d3d2cc1373b1f3a3972"
            
            # Default to first AU agent
            return "692d5b6ad10e948b7bbfc2db"
        
        agent_id = get_agent_id(lead)
        
        # Clean and format phone number properly
        original_phone = phone
        phone = phone.strip()
        
        # Extract only digits
        digits_only = ''.join(filter(str.isdigit, phone))
        
        # Take last 10 digits (right to left)
        if len(digits_only) >= 10:
            phone = f"+91{digits_only[-10:]}"
        else:
            return JsonResponse({
                'success': False,
                'error': f'Invalid phone number format: {original_phone} (only {len(digits_only)} digits)'
            }, status=400)
        
        # Prepare API payload
        payload = {
            "to_number": phone,
            "agent_id": agent_id,
            "metadata": {
                "name": lead.full_name,
                "city": lead.city or "Unknown",
                "budget": lead.budget or "Not specified",
                "form_name": lead.form_name or "Unknown",
                "lead_id": str(lead.id)
            },
            "priority": 1
        }
        
        headers = {
            "Content-Type": "application/json",
            "X-API-KEY": api_key
        }
        
        print(f"\n{'='*60}")
        print(f"🤖 CALL KARO AI - INITIATING CALL")
        print(f"{'='*60}")
        print(f"📞 Lead: {lead.full_name} (ID: {lead.id})")
        print(f"📱 Phone: {phone}")
        print(f"🎯 Agent ID: {agent_id}")
        print(f"🏢 Project: {lead.form_name or 'Unknown'}")
        
        # Show which agent is being used
        agent_names = {
            "6923ff797a5d5a94d5a5dfcf": "Gaur Yamuna Agent",
            "692d5b6ad10e948b7bbfc2db": "AU Realty Agent 1", 
            "69294d3d2cc1373b1f3a3972": "AU Realty Agent 2"
        }
        print(f"🤖 Agent: {agent_names.get(agent_id, 'Unknown Agent')}")
        print(f"🔑 API Key: {api_key[:20]}...")
        print(f"📋 Metadata: {payload['metadata']}")
        print(f"{'='*60}")
        
        try:
            # Make API call to Call Karo AI
            response = requests.post(
                "https://api.callkaro.ai/call/outbound",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            print(f"📡 API Response Status: {response.status_code}")
            print(f"📄 Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                api_response = response.json()
                print(f"✅ SUCCESS: {api_response}")
                
                # Log the call
                from .models import CallLog, TeamMember
                try:
                    team_member = TeamMember.objects.get(name='System') if TeamMember.objects.filter(name='System').exists() else TeamMember.objects.first()
                    CallLog.objects.create(
                        lead=lead,
                        team_member=team_member,
                        phone_number=phone,
                        call_type='manual',
                        status='initiated'
                    )
                    
                    # Update lead stage to 'contacted'
                    lead.stage = 'contacted'
                    lead.save()
                    print(f"📝 Call logged and stage updated to 'contacted' for {lead.full_name}")
                except Exception as log_error:
                    print(f"⚠️ Failed to log call: {log_error}")
                
                return JsonResponse({
                    'success': True,
                    'message': f'Call initiated successfully to {phone}',
                    'call_id': api_response.get('call_id', 'unknown'),
                    'lead_name': lead.full_name,
                    'api_response': api_response
                })
            else:
                error_msg = response.text
                print(f"❌ API ERROR: {error_msg}")
                
                # Log failed call
                from .models import CallLog, TeamMember
                try:
                    team_member = TeamMember.objects.get(name='System') if TeamMember.objects.filter(name='System').exists() else TeamMember.objects.first()
                    CallLog.objects.create(
                        lead=lead,
                        team_member=team_member,
                        phone_number=phone,
                        call_type='manual',
                        status='failed'
                    )
                    print(f"📝 Failed call logged for {lead.full_name}")
                except Exception as log_error:
                    print(f"⚠️ Failed to log failed call: {log_error}")
                
                return JsonResponse({
                    'success': False,
                    'error': f'Call Karo AI Error: {error_msg}',
                    'status_code': response.status_code
                }, status=400)
                
        except requests.exceptions.Timeout:
            print(f"⏰ TIMEOUT: API request timed out")
            return JsonResponse({'error': 'API request timed out'}, status=408)
            
        except requests.exceptions.RequestException as e:
            print(f"🔌 CONNECTION ERROR: {str(e)}")
            return JsonResponse({'error': f'Connection error: {str(e)}'}, status=503)
            
        finally:
            print(f"{'='*60}\n")
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        print(f"💥 UNEXPECTED ERROR: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

def call_logs(request):
    """View call logs"""
    from .models import CallLog
    logs = CallLog.objects.select_related('lead', 'team_member').order_by('-initiated_at')[:100]
    return JsonResponse({
        'call_logs': [{
            'lead_name': log.lead.full_name,
            'phone': log.phone_number,
            'status': log.status,
            'initiated_at': log.initiated_at.isoformat(),
            'team_member': log.team_member.name
        } for log in logs]
    })