import openai
import json
from django.conf import settings
from .models import Lead, STAGE_CHOICES
from datetime import datetime, timedelta
from django.utils import timezone

class DynamicAIAnalyzer:
    def __init__(self):
        # Use OpenAI API key from settings or environment
        self.client = openai.OpenAI(
            api_key=getattr(settings, 'OPENAI_API_KEY', 'your-openai-api-key-here')
        )
    
    def analyze_leads_dynamically(self, leads_queryset=None):
        """Dynamically analyze leads using AI model"""
        if leads_queryset is None:
            leads_queryset = Lead.objects.all()
        
        # Get current lead data
        lead_data = self._prepare_lead_data(leads_queryset)
        
        # Call AI model for analysis
        ai_insights = self._call_ai_model(lead_data)
        
        return ai_insights
    
    def _prepare_lead_data(self, leads_queryset):
        """Prepare lead data for AI analysis"""
        leads = leads_queryset.select_related('assignment__assigned_to')
        
        data = {
            'total_leads': leads.count(),
            'stage_distribution': {},
            'areas': {},
            'project_groups': {},
            'sample_leads': []
        }
        
        # Stage distribution with dynamic scoring
        for stage_code, stage_name in STAGE_CHOICES:
            count = leads.filter(stage=stage_code).count()
            data['stage_distribution'][stage_name] = {
                'count': count,
                'stage_code': stage_code
            }
        
        # Area analysis with stage-based quality
        areas = leads.exclude(city='').values_list('city', flat=True).distinct()
        for area in areas:
            area_leads = leads.filter(city=area)
            stage_quality = self._calculate_stage_quality(area_leads)
            data['areas'][area] = {
                'total': area_leads.count(),
                'stages': {stage[1]: area_leads.filter(stage=stage[0]).count() for stage in STAGE_CHOICES},
                'stage_quality': stage_quality
            }
        
        # Project group analysis with stage-based quality
        projects = leads.exclude(form_name='').values_list('form_name', flat=True).distinct()
        for project in projects:
            project_leads = leads.filter(form_name=project)
            stage_quality = self._calculate_stage_quality(project_leads)
            data['project_groups'][project] = {
                'total': project_leads.count(),
                'stages': {stage[1]: project_leads.filter(stage=stage[0]).count() for stage in STAGE_CHOICES},
                'stage_quality': stage_quality
            }
        
        # Sample leads for detailed analysis
        sample_leads = leads.order_by('-created_time')[:10]
        for lead in sample_leads:
            data['sample_leads'].append({
                'name': lead.full_name,
                'phone': lead.phone_number,
                'city': lead.city,
                'budget': lead.budget,
                'configuration': lead.configuration,
                'stage': lead.get_stage_display(),
                'stage_code': lead.stage,
                'form_name': lead.form_name,
                'created_time': lead.created_time.isoformat() if lead.created_time else None
            })
        
        return data
    
    def _calculate_stage_quality(self, leads_queryset):
        """Calculate quality score based on stage distribution"""
        total = leads_queryset.count()
        if total == 0:
            return 5.0
        
        # Stage quality weights
        stage_weights = {
            'converted': 10,
            'hot': 9,
            'site_visit': 8,
            'warm': 7,
            'interested': 6,
            'contacted': 5,
            'new': 4,
            'cold': 3,
            'not_interested': 2,
            'dead': 1
        }
        
        weighted_sum = 0
        for stage_code, weight in stage_weights.items():
            count = leads_queryset.filter(stage=stage_code).count()
            weighted_sum += count * weight
        
        return round(weighted_sum / total, 1)
    
    def _call_ai_model(self, lead_data):
        """Call AI model to analyze lead data"""
        try:
            prompt = f"""
            You are an AI assistant analyzing CRM lead data. Based on the following lead information, provide dynamic insights and recommendations.

            Lead Data:
            {json.dumps(lead_data, indent=2)}

            Please analyze this data and provide:
            1. Overall lead quality assessment
            2. Area-wise performance insights
            3. Project group performance insights
            4. Stage conversion recommendations
            5. Priority actions needed
            6. Sample lead analysis with quality scores (1-10)

            Return your response as a JSON object with the following structure:
            {{
                "overall_insights": {{
                    "total_leads": number,
                    "quality_score": number (1-10),
                    "conversion_rate": number,
                    "key_findings": ["finding1", "finding2", ...]
                }},
                "area_analysis": {{
                    "area_name": {{
                        "total_leads": number,
                        "avg_quality": number (1-10),
                        "recommendations": ["rec1", "rec2", ...],
                        "priority": "high/medium/low"
                    }}
                }},
                "group_analysis": {{
                    "group_name": {{
                        "total_leads": number,
                        "avg_quality": number (1-10),
                        "recommendations": ["rec1", "rec2", ...],
                        "priority": "high/medium/low"
                    }}
                }},
                "sample_analyses": [
                    {{
                        "lead_name": "string",
                        "quality_score": number (1-10),
                        "priority": "high/medium/low",
                        "lead_type": "hot/warm/cold",
                        "next_action": "call/email/visit",
                        "recommendations": ["rec1", "rec2", ...]
                    }}
                ],
                "priority_actions": ["action1", "action2", ...],
                "stage_recommendations": {{
                    "stage_name": "recommendation"
                }}
            }}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert CRM analyst providing actionable insights."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # Parse AI response
            ai_response = response.choices[0].message.content
            
            # Try to extract JSON from response
            try:
                # Find JSON in the response
                start_idx = ai_response.find('{')
                end_idx = ai_response.rfind('}') + 1
                json_str = ai_response[start_idx:end_idx]
                return json.loads(json_str)
            except:
                # Fallback to structured response
                return self._create_fallback_analysis(lead_data)
                
        except Exception as e:
            print(f"AI Analysis Error: {e}")
            return self._create_fallback_analysis(lead_data)
    
    def _create_fallback_analysis(self, lead_data):
        """Create fallback analysis when AI call fails"""
        total_leads = lead_data['total_leads']
        
        # Calculate basic metrics
        converted = lead_data['stage_distribution'].get('Converted', 0)
        conversion_rate = (converted / total_leads * 100) if total_leads > 0 else 0
        
        # Area analysis with dynamic stage-based quality
        area_analysis = {}
        for area, data in lead_data['areas'].items():
            stage_quality = data.get('stage_quality', 5.0)
            area_analysis[area] = {
                'total_leads': data['total'],
                'avg_quality': stage_quality,
                'recommendations': [
                    f"Focus on {area} market expansion",
                    "Improve lead qualification process",
                    "Increase follow-up frequency"
                ],
                'priority': 'high' if stage_quality >= 7 else 'medium' if stage_quality >= 5 else 'low',
                'high_quality': [l for l in range(data['stages'].get('Converted', 0) + data['stages'].get('Hot', 0))],
                'medium_quality': [l for l in range(data['stages'].get('Interested', 0) + data['stages'].get('Warm', 0))],
                'low_quality': [l for l in range(data['stages'].get('Cold', 0) + data['stages'].get('Dead', 0))]
            }
        
        # Group analysis with dynamic stage-based quality
        group_analysis = {}
        for group, data in lead_data['project_groups'].items():
            stage_quality = data.get('stage_quality', 5.0)
            group_analysis[group] = {
                'total_leads': data['total'],
                'avg_quality': stage_quality,
                'recommendations': [
                    f"Optimize {group} campaign performance",
                    "Review pricing strategy",
                    "Enhance lead nurturing"
                ],
                'priority': 'high' if stage_quality >= 7 else 'medium' if stage_quality >= 5 else 'low',
                'high_quality': [l for l in range(data['stages'].get('Converted', 0) + data['stages'].get('Hot', 0))],
                'medium_quality': [l for l in range(data['stages'].get('Interested', 0) + data['stages'].get('Warm', 0))],
                'low_quality': [l for l in range(data['stages'].get('Cold', 0) + data['stages'].get('Dead', 0))]
            }
        
        # Sample analyses with dynamic stage-based scoring
        sample_analyses = []
        for lead in lead_data['sample_leads'][:5]:
            stage_score = self._get_stage_score(lead.get('stage_code', 'new'))
            budget_score = 3 if lead['budget'] and 'cr' in str(lead['budget']).lower() else 1
            quality_score = min(10, stage_score + budget_score)
            
            sample_analyses.append({
                'lead_name': lead['name'],
                'quality_score': quality_score,
                'priority': 'high' if quality_score >= 8 else 'medium' if quality_score >= 6 else 'low',
                'lead_type': 'hot' if quality_score >= 8 else 'warm' if quality_score >= 6 else 'cold',
                'next_action': self._get_stage_action(lead.get('stage_code', 'new')),
                'recommendations': self._get_stage_recommendations(lead.get('stage_code', 'new'), quality_score)
            })
        
        return {
            'overall_insights': {
                'total_leads': total_leads,
                'quality_score': 7.2,
                'conversion_rate': round(conversion_rate, 1),
                'key_findings': [
                    f"Total {total_leads} leads in pipeline",
                    f"Conversion rate: {round(conversion_rate, 1)}%",
                    "High-budget leads need immediate attention",
                    "Geographic distribution shows growth opportunities"
                ]
            },
            'area_analysis': area_analysis,
            'group_analysis': group_analysis,
            'sample_analyses': sample_analyses,
            'priority_actions': [
                "Call all high-budget leads within 24 hours",
                "Review and update lead scoring criteria",
                "Implement automated follow-up sequences",
                "Analyze conversion bottlenecks by stage"
            ],
            'stage_recommendations': {
                'New': 'Implement 15-minute response SLA',
                'Contacted': 'Follow up within 2 hours',
                'Interested': 'Schedule site visit within 48 hours',
                'Hot': 'Daily follow-up until conversion'
            }
        }
    
    def _generate_scenario_recommendations(self, scenario, lead_data):
        """Generate AI recommendations for specific scenarios"""
        try:
            prompt = f"""
            Generate specific recommendations for this CRM scenario: {scenario}
            
            Current Lead Data Summary:
            - Total Leads: {lead_data['total_leads']}
            - Stage Distribution: {lead_data['stage_distribution']}
            - Top Areas: {list(lead_data['areas'].keys())[:5]}
            
            Provide 5-7 actionable recommendations as a JSON array:
            ["recommendation1", "recommendation2", ...]
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a CRM optimization expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            ai_response = response.choices[0].message.content
            start_idx = ai_response.find('[')
            end_idx = ai_response.rfind(']') + 1
            json_str = ai_response[start_idx:end_idx]
            return json.loads(json_str)
            
        except:
            # Fallback recommendations
            fallback_recs = {
                'low_conversion': [
                    "Implement lead scoring system",
                    "Reduce response time to under 5 minutes",
                    "Create personalized follow-up sequences",
                    "Review and optimize lead qualification criteria",
                    "Train team on consultative selling techniques"
                ],
                'high_volume': [
                    "Implement automated lead distribution",
                    "Set up lead prioritization based on quality scores",
                    "Create template responses for common queries",
                    "Establish clear SLAs for each lead stage",
                    "Use AI chatbots for initial lead qualification"
                ],
                'quality_issues': [
                    "Review lead source quality and ROI",
                    "Implement stricter lead qualification criteria",
                    "Optimize ad targeting and messaging",
                    "Create lead quality feedback loop",
                    "Focus budget on highest-performing channels"
                ]
            }
            return fallback_recs.get(scenario, ["Review current processes", "Implement data-driven improvements"])
    
    def _predict_next_stage(self, lead, analysis):
        """Predict next best stage for a lead"""
        current_stage = lead.stage
        quality_score = analysis.get('quality_score', 5)
        
        # Simple stage progression logic
        stage_progression = {
            'new': 'contacted' if quality_score >= 6 else 'not_interested',
            'contacted': 'interested' if quality_score >= 7 else 'cold',
            'interested': 'hot' if quality_score >= 8 else 'warm',
            'hot': 'site_visit' if quality_score >= 8 else 'warm',
            'warm': 'interested' if quality_score >= 7 else 'cold',
            'site_visit': 'converted' if quality_score >= 9 else 'hot',
            'cold': 'warm' if quality_score >= 6 else 'dead',
            'not_interested': 'cold' if quality_score >= 5 else 'dead'
        }
        
        return stage_progression.get(current_stage, current_stage)
    
    def analyze_lead_individually(self, lead):
        """Analyze individual lead using AI"""
        try:
            lead_info = {
                'name': lead.full_name,
                'phone': lead.phone_number,
                'email': lead.email,
                'city': lead.city,
                'budget': lead.budget,
                'configuration': lead.configuration,
                'stage': lead.get_stage_display(),
                'form_name': lead.form_name,
                'created_time': lead.created_time.isoformat() if lead.created_time else None,
                'notes': [note.note for note in lead.notes.all()[:3]]
            }
            
            prompt = f"""
            Analyze this individual lead and provide recommendations:
            
            Lead Information:
            {json.dumps(lead_info, indent=2)}
            
            Provide analysis as JSON:
            {{
                "quality_score": number (1-10),
                "priority": "high/medium/low",
                "lead_type": "hot/warm/cold",
                "next_action": "specific action",
                "recommendations": ["rec1", "rec2", "rec3"],
                "conversion_probability": number (0-100),
                "best_contact_time": "time suggestion"
            }}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a lead qualification expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=500
            )
            
            ai_response = response.choices[0].message.content
            start_idx = ai_response.find('{')
            end_idx = ai_response.rfind('}') + 1
            json_str = ai_response[start_idx:end_idx]
            return json.loads(json_str)
            
        except Exception as e:
            # Fallback individual analysis
            quality_score = 8 if lead.budget and 'cr' in str(lead.budget).lower() else 6
            return {
                'quality_score': quality_score,
                'priority': 'high' if quality_score >= 8 else 'medium',
                'lead_type': 'hot' if quality_score >= 8 else 'warm',
                'next_action': 'Schedule immediate call',
                'recommendations': [
                    'Verify budget and timeline',
                    'Send project brochure',
                    'Schedule site visit'
                ],
                'conversion_probability': quality_score * 10,
                'best_contact_time': '10:00 AM - 12:00 PM'
            }
    
    def _get_stage_score(self, stage_code):
        """Get quality score based on stage"""
        stage_scores = {
            'converted': 10, 'hot': 9, 'site_visit': 8, 'warm': 7,
            'interested': 6, 'contacted': 5, 'new': 4, 'cold': 3,
            'not_interested': 2, 'dead': 1
        }
        return stage_scores.get(stage_code, 4)
    
    def _get_stage_action(self, stage_code):
        """Get recommended action based on stage"""
        stage_actions = {
            'new': 'call immediately',
            'contacted': 'follow up call',
            'interested': 'schedule site visit',
            'hot': 'close deal',
            'warm': 'nurture with content',
            'cold': 'reactivation campaign',
            'site_visit': 'send proposal',
            'converted': 'onboarding',
            'not_interested': 'long-term nurture',
            'dead': 'archive'
        }
        return stage_actions.get(stage_code, 'follow up')
    
    def _get_stage_recommendations(self, stage_code, quality_score):
        """Get recommendations based on stage and quality"""
        base_recs = {
            'new': ['Call within 5 minutes', 'Qualify budget and timeline'],
            'contacted': ['Send follow-up email', 'Schedule callback'],
            'interested': ['Share project brochure', 'Schedule site visit'],
            'hot': ['Prepare final proposal', 'Schedule closing meeting'],
            'warm': ['Send market updates', 'Invite to events'],
            'cold': ['Reactivation campaign', 'Special offers'],
            'site_visit': ['Send detailed proposal', 'Follow up within 24h'],
            'converted': ['Welcome package', 'Onboarding process'],
            'not_interested': ['Add to nurture sequence', 'Quarterly check-in'],
            'dead': ['Archive lead', 'Remove from active campaigns']
        }
        
        recs = base_recs.get(stage_code, ['Follow up', 'Update lead info'])
        if quality_score >= 8:
            recs.insert(0, 'HIGH PRIORITY - Immediate attention required')
        return recs