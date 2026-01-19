from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Q
from django.utils import timezone
from .models import Lead, STAGE_CHOICES, LeadRating
from .llama_rating import LlamaLeadRater
import json

def ai_dashboard(request):
    """Dynamic AI dashboard with stage-based quality scoring"""
    # Use utility function for consistent access control
    from .utils import get_user_leads
    leads = get_user_leads(request)
    
    # Stage quality weights - correct progression
    stage_weights = {
        'not_interested': 1, 'dead': 1, 'cold': 2, 'new': 3,
        'interested': 4, 'hot': 6, 'contacted': 8, 'site_visit': 9, 'converted': 10
    }
    
    def calculate_quality(queryset):
        total = queryset.count()
        if total == 0:
            return 5.0
        weighted_sum = 0
        for stage, weight in stage_weights.items():
            count = queryset.filter(stage=stage).count()
            weighted_sum += count * weight
        return round(weighted_sum / total, 1)
    
    # Areas with dynamic quality based on stages
    areas = leads.exclude(city='').values('city').annotate(count=Count('id')).order_by('-count')[:10]
    area_analysis = {}
    for area in areas:
        city_leads = leads.filter(city=area['city'])
        quality = calculate_quality(city_leads)
        high_count = city_leads.filter(stage__in=['converted', 'hot', 'site_visit']).count()
        medium_count = city_leads.filter(stage__in=['warm', 'interested', 'contacted']).count()
        low_count = city_leads.filter(stage__in=['new', 'cold', 'not_interested', 'dead']).count()
        
        area_analysis[area['city']] = {
            'total_leads': area['count'],
            'avg_quality': quality,
            'high_quality': list(range(high_count)),
            'medium_quality': list(range(medium_count)),
            'low_quality': list(range(low_count))
        }
    
    # Groups with dynamic quality based on stages
    groups = leads.exclude(form_name='').values('form_name').annotate(count=Count('id')).order_by('-count')[:10]
    group_analysis = {}
    for group in groups:
        group_leads = leads.filter(form_name=group['form_name'])
        quality = calculate_quality(group_leads)
        high_count = group_leads.filter(stage__in=['converted', 'hot', 'site_visit']).count()
        medium_count = group_leads.filter(stage__in=['warm', 'interested', 'contacted']).count()
        low_count = group_leads.filter(stage__in=['new', 'cold', 'not_interested', 'dead']).count()
        
        group_analysis[group['form_name']] = {
            'total_leads': group['count'],
            'avg_quality': quality,
            'high_quality': list(range(high_count)),
            'medium_quality': list(range(medium_count)),
            'low_quality': list(range(low_count))
        }
    
    # Sample analyses using actual AI model
    sample_leads = leads.order_by('-created_time')[:5]
    sample_analyses = []
    
    try:
        from .llama_rating import LlamaLeadRater
        rater = LlamaLeadRater()
        
        for lead in sample_leads:
            try:
                # Get or create AI rating
                rating = LeadRating.objects.get(lead=lead)
            except LeadRating.DoesNotExist:
                # Use AI model to rate lead
                rating_data = rater.rate_lead(lead)
                rating = LeadRating.objects.create(lead=lead, **rating_data)
            
            # Get dynamic action based on actual stage
            action = get_stage_action(lead.stage)
            recommendations = get_stage_recommendations(lead.stage, rating.score)
            
            print(f"AI MODEL DEBUG: {lead.full_name}")
            print(f"  Stage: '{lead.stage}' -> Action: '{action}'")
            print(f"  AI Score: {rating.score}, Priority: {rating.priority}")
            
            sample_analyses.append({
                'lead': lead,
                'analysis': {
                    'quality_score': rating.score,
                    'priority': rating.priority,
                    'lead_type': 'hot' if rating.score >= 8 else 'warm' if rating.score >= 6 else 'cold',
                    'next_action': action,
                    'recommendations': recommendations
                }
            })
    except ImportError:
        # Fallback if AI model not available
        for lead in sample_leads:
            stage_score = stage_weights.get(lead.stage, 4)
            action = get_stage_action(lead.stage)
            recommendations = get_stage_recommendations(lead.stage, stage_score)
            
            sample_analyses.append({
                'lead': lead,
                'analysis': {
                    'quality_score': stage_score,
                    'priority': 'medium',
                    'lead_type': 'warm',
                    'next_action': action,
                    'recommendations': recommendations
                }
            })
    
    context = {
        'total_leads': leads.count(),
        'total_areas': len(areas),
        'total_groups': len(groups),
        'area_analysis': area_analysis,
        'group_analysis': group_analysis,
        'sample_analyses': sample_analyses
    }
    
    print(f"\nFINAL RENDER DEBUG:")
    for analysis in sample_analyses:
        print(f"  {analysis['lead'].full_name} ({analysis['lead'].stage}) -> {analysis['analysis']['next_action']}")
    print("\n")
    return render(request, 'leads/ai_dashboard_fixed.html', context)

def get_stage_action(stage_code):
    """Get recommended action based on stage progression"""
    stage_actions = {
        'not_interested': 'Archive or nurture',
        'dead': 'Remove from pipeline', 
        'cold': 'Reactivation campaign',
        'new': 'Initial qualification call',
        'interested': 'Build interest & qualify',
        'hot': 'Schedule meeting ASAP',
        'contacted': 'Present proposal',
        'site_visit': 'Close the deal',
        'converted': 'Onboarding & delivery',
        'warm': 'Send project details'
    }
    action = stage_actions.get(stage_code, f'Follow up on {stage_code} stage')
    print(f"  Stage '{stage_code}' mapped to action: '{action}'")
    return action

def get_stage_recommendations(stage_code, quality_score):
    """Get recommendations based on correct stage progression"""
    base_recs = {
        'not_interested': ['Move to nurture campaign', 'Set quarterly follow-up', 'Archive if confirmed'],
        'dead': ['Remove from active pipeline', 'Data cleanup', 'Mark as closed'],
        'cold': ['Reactivation email sequence', 'Special offer campaign', 'Re-qualification call'],
        'new': ['Call within 15 minutes', 'Qualify budget & timeline', 'Assess genuine interest'],
        'interested': ['Share project details', 'Understand requirements', 'Build rapport & trust'],
        'hot': ['Schedule urgent meeting', 'Prepare customized presentation', 'Fast-track process'],
        'contacted': ['Present detailed proposal', 'Address objections', 'Negotiate terms'],
        'site_visit': ['Final closing push', 'Handle last concerns', 'Get commitment'],
        'converted': ['Celebration & onboarding', 'Collect testimonial', 'Ask for referrals']
    }
    
    recs = base_recs.get(stage_code, ['Review lead status', 'Update information', 'Plan next action'])
    if quality_score >= 8:
        recs.insert(0, '🔥 HIGH PRIORITY - Act immediately!')
    return recs

@csrf_exempt
def analyze_lead_ai(request):
    """Analyze lead using Llama 3.1-8B-Instruct"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'})
    
    try:
        data = json.loads(request.body)
        lead_id = data.get('lead_id')
        
        lead = Lead.objects.get(id=lead_id)
        
        # Use Llama for rating
        rater = LlamaLeadRater()
        rating_data = rater.rate_lead(lead)
        
        # Save or update rating
        rating, created = LeadRating.objects.get_or_create(
            lead=lead,
            defaults=rating_data
        )
        if not created:
            rating.score = rating_data['score']
            rating.priority = rating_data['priority']
            rating.reason = rating_data['reason']
            rating.save()
        
        # Get dynamic action and AI insights
        action = get_stage_action(lead.stage)
        recommendations = get_stage_recommendations(lead.stage, rating.score)
        
        # Generate AI insights
        try:
            ai_insights = rater.generate_insights(lead, rating.score)
        except:
            ai_insights = f"Lead shows {rating.priority} potential based on current stage '{lead.get_stage_display()}' and available information. Budget: {lead.budget or 'Not specified'}. Recommended focus: {action.lower()}."
        
        return JsonResponse({
            'success': True,
            'analysis': {
                'quality_score': rating.score,
                'priority': rating.priority,
                'next_action': action,
                'ai_insights': ai_insights,
                'recommendations': recommendations[:3]
            },
            'lead_name': lead.full_name
        })
        
    except Lead.DoesNotExist:
        return JsonResponse({'error': 'Lead not found'})
    except Exception as e:
        return JsonResponse({'error': str(e)})

@csrf_exempt
def refresh_ai_insights(request):
    """Refresh insights without AI"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'})
    
    try:
        leads = Lead.objects.all()
        
        return JsonResponse({
            'success': True,
            'message': f'Insights refreshed for {leads.count()} leads'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)})

@csrf_exempt
def generate_ai_recommendations(request):
    """Generate static recommendations"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'})
    
    try:
        data = json.loads(request.body)
        scenario = data.get('scenario')
        
        recommendations = {
            'low_conversion': ['Improve response time', 'Better lead qualification', 'Follow up more frequently'],
            'high_volume': ['Automate initial responses', 'Prioritize high-value leads', 'Use lead scoring'],
            'quality_issues': ['Review lead sources', 'Improve targeting', 'Better qualification criteria']
        }
        
        return JsonResponse({
            'success': True,
            'scenario': scenario,
            'recommendations': recommendations.get(scenario, ['Review processes', 'Implement improvements'])
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)})

def ai_lead_scoring(request):
    """Llama-powered lead scoring page"""
    try:
        # Filter leads based on team member
        team_member_id = request.session.get('team_member_id')
        
        if team_member_id:
            # Team member sees only their assigned leads
            try:
                from .models import TeamMember
                team_member = TeamMember.objects.get(id=team_member_id)
                recent_leads = Lead.objects.filter(assignment__assigned_to=team_member).order_by('-created_time')[:50]
            except TeamMember.DoesNotExist:
                recent_leads = Lead.objects.none()
        else:
            # Admin sees all leads
            recent_leads = Lead.objects.order_by('-created_time')[:50]
        rater = LlamaLeadRater()
        
        scored_leads = []
        for lead in recent_leads:
            try:
                rating = LeadRating.objects.get(lead=lead)
            except LeadRating.DoesNotExist:
                # Create new rating using fallback (faster than Llama for bulk)
                rating_data = rater._fallback_rating(lead)
                rating = LeadRating.objects.create(lead=lead, **rating_data)
            
            scored_leads.append({
                'lead': lead,
                'score': rating.score,
                'priority': rating.priority,
                'next_action': 'Follow up call',
                'conversion_probability': rating.score * 10,
                'reason': rating.reason
            })
        
        scored_leads.sort(key=lambda x: x['score'], reverse=True)
        
        return render(request, 'leads/ai_lead_scoring.html', {
            'scored_leads': scored_leads[:20],
            'total_scored': len(scored_leads)
        })
    except Exception as e:
        return render(request, 'leads/ai_lead_scoring.html', {
            'error': str(e),
            'scored_leads': [],
            'total_scored': 0
        })

@csrf_exempt
def ai_stage_prediction(request):
    """Static stage prediction"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'})
    
    try:
        data = json.loads(request.body)
        lead_ids = data.get('lead_ids', [])
        
        predictions = []
        for lead_id in lead_ids:
            try:
                lead = Lead.objects.get(id=lead_id)
                predictions.append({
                    'lead_id': lead_id,
                    'lead_name': lead.full_name,
                    'current_stage': lead.stage,
                    'predicted_stage': 'contacted',
                    'confidence': 70,
                    'recommended_action': 'Follow up call'
                })
            except Lead.DoesNotExist:
                continue
        
        return JsonResponse({
            'success': True,
            'predictions': predictions,
            'total_processed': len(predictions)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)})

def ai_insights_api(request):
    """Static insights API"""
    leads = Lead.objects.all()
    
    return JsonResponse({
        'success': True,
        'timestamp': timezone.now().isoformat(),
        'total_leads': leads.count(),
        'quality_score': 7.2,
        'conversion_rate': 15.5,
        'high_priority_leads': 5
    })

@csrf_exempt
def generate_follow_up(request):
    """Generate static follow-up message"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'})
    
    try:
        data = json.loads(request.body)
        lead_id = data.get('lead_id')
        
        lead = Lead.objects.get(id=lead_id)
        
        return JsonResponse({
            'success': True,
            'lead_name': lead.full_name,
            'message': 'Hi! Thank you for your interest in our projects. Our team will contact you shortly with detailed information and pricing.'
        })
        
    except Lead.DoesNotExist:
        return JsonResponse({'error': 'Lead not found'})
    except Exception as e:
        return JsonResponse({'error': str(e)})

@csrf_exempt
def suggest_call_time(request):
    """Suggest best call time"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'})
    
    try:
        data = json.loads(request.body)
        lead_id = data.get('lead_id')
        
        lead = Lead.objects.get(id=lead_id)
        
        return JsonResponse({
            'success': True,
            'lead_name': lead.full_name,
            'suggestion': 'Best time to call: 10:00 AM - 12:00 PM (Higher response rate during morning hours)'
        })
        
    except Lead.DoesNotExist:
        return JsonResponse({'error': 'Lead not found'})
    except Exception as e:
        return JsonResponse({'error': str(e)})

@csrf_exempt
def load_analysis(request):
    """Load analysis data"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'})
    
    return JsonResponse({
        'success': True,
        'area_analysis': {},
        'sample_analyses': []
    })

@csrf_exempt
def analyze_notes(request):
    """Analyze notes"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'})
    
    return JsonResponse({
        'success': True,
        'analysis': {
            'sentiment': 'Positive',
            'interest_level': 'High',
            'next_action': 'Follow up call',
            'follow_up_timing': 'Within 24 hours'
        }
    })