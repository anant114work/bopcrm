import requests
from django.utils import timezone
from django.conf import settings
from django.db import models
from .models import Lead
from .ai_agent_models import AIAgent, AICallLog
from .form_mapping_models import FormSourceMapping

class AutoAICallService:
    """Service to automatically call new leads with mapped AI agents"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'CALLKARO_API_KEY', 'bc422db39aa327234a911dd901accfcfa975623ee84c65c83aae9c4f844ffdb8')
        self.api_url = "https://api.callkaro.ai/call/outbound"
    
    def process_new_lead(self, lead):
        """Process a single new lead - find project and trigger AI call"""
        
        # Check if already called
        if self._is_already_called(lead):
            print(f"⏭️ Lead {lead.full_name} already called, skipping")
            return {'skipped': True, 'reason': 'Already called'}
        
        # Find project from form mapping
        project = self._find_project_for_lead(lead)
        if not project:
            print(f"❌ No project mapping found for form: {lead.form_name}")
            return {'skipped': True, 'reason': 'No project mapping'}
        
        # Get AI agent for project
        agent = self._get_agent_for_project(project)
        if not agent:
            print(f"❌ No AI agent configured for project: {project.name}")
            return {'skipped': True, 'reason': 'No AI agent'}
        
        # Validate phone number
        if not lead.phone_number or len(lead.phone_number.strip()) < 10:
            print(f"❌ Invalid phone number for lead: {lead.full_name}")
            return {'skipped': True, 'reason': 'Invalid phone'}
        
        # Trigger AI call
        result = self._trigger_ai_call(lead, agent, project)
        return result
    
    def _is_already_called(self, lead):
        """Check if lead was already called"""
        return AICallLog.objects.filter(
            lead=lead,
            status__in=['initiated', 'connected']
        ).exists()
    
    def _find_project_for_lead(self, lead):
        """Find project based on form mapping"""
        # Try exact form name match first
        mapping = FormSourceMapping.objects.filter(
            form_name__iexact=lead.form_name,
            is_active=True
        ).first()
        
        if mapping:
            return mapping.project
        
        # Try partial match
        mapping = FormSourceMapping.objects.filter(
            is_active=True
        ).filter(
            form_name__icontains=lead.form_name
        ).first() or FormSourceMapping.objects.filter(
            is_active=True
        ).filter(
            models.Q(form_name__in=lead.form_name)
        ).first()
        
        if mapping:
            return mapping.project
        
        # Fallback to project keyword matching
        from .project_models import Project
        for project in Project.objects.filter(status='Active'):
            for keyword in project.form_keywords:
                if keyword.lower() in lead.form_name.lower():
                    return project
        
        return None
    
    def _get_agent_for_project(self, project):
        """Get active AI agent for project"""
        return AIAgent.objects.filter(
            project=project,
            is_active=True
        ).first()
    
    def _trigger_ai_call(self, lead, agent, project):
        """Trigger AI call via Call Karo AI"""
        
        # Format phone number
        phone = lead.phone_number.strip()
        digits_only = ''.join(filter(str.isdigit, phone))
        
        if len(digits_only) >= 10:
            phone = f"+91{digits_only[-10:]}"
        else:
            return {'success': False, 'error': 'Invalid phone format'}
        
        # Prepare payload
        payload = {
            "to_number": phone,
            "agent_id": agent.agent_id,
            "metadata": {
                "name": lead.full_name,
                "city": lead.city or "Unknown",
                "budget": lead.budget or "Not specified",
                "form_name": lead.form_name or "Unknown",
                "project": project.name,
                "lead_id": str(lead.id)
            },
            "priority": 1
        }
        
        headers = {
            "Content-Type": "application/json",
            "X-API-KEY": self.api_key
        }
        
        print(f"\n{'='*60}")
        print(f"🤖 AUTO AI CALL - {project.name}")
        print(f"{'='*60}")
        print(f"📞 Lead: {lead.full_name} (ID: {lead.id})")
        print(f"📱 Phone: {phone}")
        print(f"🎯 Agent: {agent.name} ({agent.agent_id})")
        print(f"🏢 Project: {project.name}")
        print(f"{'='*60}")
        
        # Create call log
        call_log = AICallLog.objects.create(
            lead=lead,
            agent=agent,
            phone_number=phone,
            status='initiated'
        )
        
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                api_response = response.json()
                call_log.status = 'connected'
                call_log.call_id = api_response.get('call_id', '')
                call_log.completed_at = timezone.now()
                call_log.save()
                
                # Update lead stage
                lead.stage = 'contacted'
                lead.save()
                
                print(f"✅ SUCCESS: Call initiated for {lead.full_name}")
                
                return {
                    'success': True,
                    'call_id': call_log.call_id,
                    'lead_name': lead.full_name,
                    'project': project.name
                }
            else:
                call_log.status = 'failed'
                call_log.error_message = response.text
                call_log.save()
                
                print(f"❌ FAILED: {response.text}")
                
                return {
                    'success': False,
                    'error': response.text
                }
        
        except Exception as e:
            call_log.status = 'failed'
            call_log.error_message = str(e)
            call_log.save()
            
            print(f"💥 ERROR: {str(e)}")
            
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            print(f"{'='*60}\n")
    
    def process_batch(self, leads):
        """Process multiple leads"""
        results = {
            'total': len(leads),
            'called': 0,
            'skipped': 0,
            'failed': 0,
            'details': []
        }
        
        for lead in leads:
            result = self.process_new_lead(lead)
            
            if result.get('skipped'):
                results['skipped'] += 1
            elif result.get('success'):
                results['called'] += 1
            else:
                results['failed'] += 1
            
            results['details'].append({
                'lead_id': lead.id,
                'lead_name': lead.full_name,
                'result': result
            })
        
        return results
