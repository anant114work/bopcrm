from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Lead
from .project_models import Project
from django.views.decorators.csrf import csrf_exempt
import json

def leads_analytics(request):
    """Main leads analytics dashboard with AI insights"""
    from django.db.models import Count, Q
    from datetime import datetime, timedelta
    import json
    
    # Get basic stats
    total_leads = Lead.objects.count()
    meta_leads = Lead.objects.exclude(lead_id__startswith='GF_').exclude(lead_id__startswith='GS_').count()
    google_leads = Lead.objects.filter(Q(lead_id__startswith='GF_') | Q(lead_id__startswith='GS_')).count()
    converted_leads = Lead.objects.filter(stage='converted').count()
    conversion_rate = round((converted_leads / total_leads * 100) if total_leads > 0 else 0, 1)
    
    # AI-powered insights
    try:
        from .ai_assistant import LeadAIAssistant
        ai_assistant = LeadAIAssistant()
        
        # Get AI insights for top performing areas
        top_cities = Lead.objects.values('city').annotate(
            count=Count('id')
        ).filter(count__gt=10).order_by('-count')[:5]
        
        ai_insights = []
        for city_data in top_cities:
            if city_data['city']:
                city_leads = Lead.objects.filter(city=city_data['city'])[:10]
                sample_lead = city_leads.first()
                if sample_lead:
                    lead_data = {
                        'full_name': sample_lead.full_name,
                        'city': sample_lead.city,
                        'budget': sample_lead.budget,
                        'form_name': sample_lead.form_name
                    }
                    analysis = ai_assistant.analyze_lead_quality(lead_data)
                    ai_insights.append({
                        'city': city_data['city'],
                        'lead_count': city_data['count'],
                        'quality_score': analysis.get('quality_score', 5),
                        'recommendations': analysis.get('recommendations', [])
                    })
    except Exception as e:
        ai_insights = []
    
    # Project data (leads by form_name)
    project_stats = Lead.objects.values('form_name').annotate(
        count=Count('id')
    ).filter(count__gt=0).order_by('-count')[:5]
    
    project_labels = []
    project_values = []
    for stat in project_stats:
        if stat['form_name']:
            name = stat['form_name'][:20] + '...' if len(stat['form_name']) > 20 else stat['form_name']
            project_labels.append(name)
            project_values.append(stat['count'])
    
    # Stage data
    stage_stats = Lead.objects.values('stage').annotate(
        count=Count('id')
    ).filter(count__gt=0).order_by('-count')
    
    stage_labels = []
    stage_values = []
    for stat in stage_stats:
        stage_labels.append(stat['stage'].title() if stat['stage'] else 'Unknown')
        stage_values.append(stat['count'])
    
    # Daily activity (last 7 days)
    daily_labels = []
    daily_values = []
    for i in range(6, -1, -1):
        date = datetime.now().date() - timedelta(days=i)
        count = Lead.objects.filter(created_time__date=date).count()
        daily_labels.append(date.strftime('%b %d'))
        daily_values.append(count)
    
    context = {
        'total_leads': total_leads,
        'meta_leads': meta_leads,
        'google_leads': google_leads,
        'conversion_rate': conversion_rate,
        'ai_insights': ai_insights,
        'project_data': json.dumps({
            'labels': project_labels,
            'values': project_values
        }),
        'stage_data': json.dumps({
            'labels': stage_labels,
            'values': stage_values
        }),
        'daily_data': json.dumps({
            'labels': daily_labels,
            'values': daily_values
        })
    }
    
    return render(request, 'leads/leads_analytics.html', context)

def leads_per_project_data(request):
    """API endpoint for leads per project chart data"""
    try:
        from django.db.models import Count
        from leads.models import Lead
        
        # Get leads grouped by form_name (project)
        projects_data = []
        
        # Get form names with lead counts
        form_counts = Lead.objects.values('form_name').annotate(
            lead_count=Count('id')
        ).filter(lead_count__gt=0).order_by('-lead_count')
        
        for form_data in form_counts:
            if form_data['form_name']:
                projects_data.append({
                    'name': form_data['form_name'][:30],  # Truncate long names
                    'leads': form_data['lead_count'],
                    'location': 'Various',
                    'developer': 'Multiple'
                })
        
        # If no data, add sample data
        if not projects_data:
            projects_data = [{
                'name': 'No Projects',
                'leads': 0,
                'location': 'N/A',
                'developer': 'N/A'
            }]
        
        return JsonResponse({
            'success': True,
            'data': projects_data
        })
    except Exception as e:
        return JsonResponse({'error': str(e), 'success': False})

def leads_per_day_data(request):
    """API endpoint for leads per day chart data"""
    try:
        # Get leads for last 30 days
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=29)
        
        daily_data = []
        current_date = start_date
        
        while current_date <= end_date:
            lead_count = Lead.objects.filter(
                created_time__date=current_date
            ).count()
            
            daily_data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'day': current_date.strftime('%b %d'),
                'leads': lead_count
            })
            
            current_date += timedelta(days=1)
        
        return JsonResponse({
            'success': True,
            'data': daily_data
        })
    except Exception as e:
        return JsonResponse({'error': str(e)})

def leads_per_week_data(request):
    """API endpoint for leads per week chart data"""
    try:
        # Get leads for last 12 weeks
        end_date = timezone.now().date()
        start_date = end_date - timedelta(weeks=11)
        
        weekly_data = []
        current_date = start_date
        
        while current_date <= end_date:
            week_end = min(current_date + timedelta(days=6), end_date)
            
            lead_count = Lead.objects.filter(
                created_time__date__gte=current_date,
                created_time__date__lte=week_end
            ).count()
            
            weekly_data.append({
                'week_start': current_date.strftime('%Y-%m-%d'),
                'week_label': f"{current_date.strftime('%b %d')} - {week_end.strftime('%b %d')}",
                'leads': lead_count
            })
            
            current_date += timedelta(weeks=1)
        
        return JsonResponse({
            'success': True,
            'data': weekly_data
        })
    except Exception as e:
        return JsonResponse({'error': str(e)})

def leads_per_month_data(request):
    """API endpoint for leads per month chart data"""
    try:
        # Get leads for last 12 months
        monthly_data = []
        current_date = timezone.now().date().replace(day=1)
        
        for i in range(12):
            # Calculate month start and end
            if current_date.month == 1:
                prev_month = current_date.replace(year=current_date.year - 1, month=12)
            else:
                prev_month = current_date.replace(month=current_date.month - 1)
            
            # Get next month for range
            if current_date.month == 12:
                next_month = current_date.replace(year=current_date.year + 1, month=1)
            else:
                next_month = current_date.replace(month=current_date.month + 1)
            
            lead_count = Lead.objects.filter(
                created_time__date__gte=current_date,
                created_time__date__lt=next_month
            ).count()
            
            monthly_data.insert(0, {
                'month': current_date.strftime('%Y-%m'),
                'month_label': current_date.strftime('%b %Y'),
                'leads': lead_count
            })
            
            current_date = prev_month
        
        return JsonResponse({
            'success': True,
            'data': monthly_data
        })
    except Exception as e:
        return JsonResponse({'error': str(e)})

def call_analytics_api(request):
    """API endpoint for call analytics data"""
    try:
        from tata_integration.models import TataCall
        from datetime import datetime, timedelta
        from django.utils import timezone
        
        # Get today's calls for stats
        today = timezone.now().date()
        today_calls = TataCall.objects.filter(start_stamp__date=today)
        
        # Get call statistics
        total_calls = today_calls.count()
        answered_calls = today_calls.filter(status__in=['answered', 'completed']).count()
        missed_calls = today_calls.filter(status__in=['missed', 'no-answer', 'busy', 'no_answer']).count()
        avg_duration = today_calls.aggregate(avg=Avg('duration'))['avg'] or 0
        
        # Get recent calls (last 50 calls with valid data)
        recent_calls = TataCall.objects.filter(
            start_stamp__isnull=False
        ).order_by('-start_stamp')[:50]
        
        calls_data = []
        for call in recent_calls:
            # Try to find associated lead for customer name
            customer_name = 'Unknown'
            if call.lead:
                customer_name = call.lead.full_name or 'Unknown'
            elif call.customer_number:
                from leads.models import Lead
                lead = Lead.objects.filter(
                    phone_number__icontains=call.customer_number.replace('+91', '').replace('+', '')
                ).first()
                if lead:
                    customer_name = lead.full_name or 'Unknown'
            
            # Format the call data
            calls_data.append({
                'customer_number': call.customer_number or 'Unknown',
                'customer_name': customer_name,
                'agent_name': call.agent_name or 'System',
                'status': call.status or 'unknown',
                'duration': call.duration or 0,
                'start_time': call.start_stamp.isoformat() if call.start_stamp else None,
                'recording_url': call.recording_url or None,
                'department': call.department or 'General'
            })
        
        return JsonResponse({
            'success': True,
            'total': total_calls,
            'answered': answered_calls,
            'missed': missed_calls,
            'avgDuration': int(avg_duration),
            'calls': calls_data,
            'message': f'Loaded {len(calls_data)} recent calls from {TataCall.objects.count()} total records'
        })
        
    except Exception as e:
        print(f'Call analytics API error: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': str(e),
            'total': 0,
            'answered': 0,
            'missed': 0,
            'avgDuration': 0,
            'calls': []
        })

@csrf_exempt
def sync_calls_api(request):
    """API endpoint to sync calls from Tata"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'})
    
    try:
        # Try to import and use Tata sync
        try:
            from tata_integration.analytics_views import sync_all_calls
            return sync_all_calls(request)
        except ImportError:
            return JsonResponse({
                'success': False,
                'error': 'Tata integration not available. Please configure Tata IVR integration first.'
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })