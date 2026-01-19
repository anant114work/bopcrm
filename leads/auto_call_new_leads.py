from django.utils import timezone
from datetime import datetime, timedelta
from .models import Lead
from .callkaro_models import CallKaroCallLog, CallKaroAgent
from .bulk_call_service import initiate_callkaro_call
import logging

logger = logging.getLogger(__name__)

class AutoCallService:
    """Service to automatically call new leads from specific forms"""
    
    def __init__(self):
        self.agent_id = "69294d3d2cc1373b1f3a3972"  # AU Reality Agent
        
    def get_new_leads_for_calling(self, form_names=None, since_minutes=60):
        """Get new leads that need to be called"""
        cutoff_time = timezone.now() - timedelta(minutes=since_minutes)
        
        # Get leads created in the last X minutes
        new_leads = Lead.objects.filter(
            created_time__gte=cutoff_time,
            phone_number__isnull=False
        ).exclude(phone_number='')
        
        # Filter by specific forms if provided
        if form_names:
            new_leads = new_leads.filter(form_name__in=form_names)
        
        # Exclude leads already called
        called_numbers = CallKaroCallLog.objects.values_list('phone_number', flat=True)
        new_leads = new_leads.exclude(phone_number__in=called_numbers)
        
        return new_leads.order_by('-created_time')
    
    def call_new_leads(self, form_names=None, since_minutes=60):
        """Call all new leads from specified forms"""
        new_leads = self.get_new_leads_for_calling(form_names, since_minutes)
        
        results = {
            'total_leads': new_leads.count(),
            'successful_calls': 0,
            'failed_calls': 0,
            'call_logs': []
        }
        
        for lead in new_leads:
            try:
                # Initiate call
                result = initiate_callkaro_call(
                    phone_number=lead.phone_number,
                    name=lead.full_name,
                    agent_id=self.agent_id
                )
                
                # Create call log
                call_log = CallKaroCallLog.objects.create(
                    call_id=result.get('call_id', ''),
                    lead=lead,
                    phone_number=lead.phone_number,
                    agent_id=self.agent_id,
                    status='initiated' if result['success'] else 'failed',
                    metadata={
                        'form_name': lead.form_name,
                        'source': lead.source,
                        'auto_call': True,
                        'city': lead.city,
                        'budget': lead.budget
                    }
                )
                
                if result['success']:
                    results['successful_calls'] += 1
                    logger.info(f"Auto-called lead {lead.full_name} ({lead.phone_number}) successfully")
                else:
                    results['failed_calls'] += 1
                    call_log.error_message = result.get('error', 'Unknown error')
                    call_log.save()
                    logger.error(f"Failed to auto-call lead {lead.full_name}: {result.get('error')}")
                
                results['call_logs'].append({
                    'lead_name': lead.full_name,
                    'phone': lead.phone_number,
                    'form': lead.form_name,
                    'success': result['success'],
                    'call_id': result.get('call_id', ''),
                    'error': result.get('error', '')
                })
                
            except Exception as e:
                results['failed_calls'] += 1
                logger.error(f"Exception calling lead {lead.full_name}: {str(e)}")
                
                results['call_logs'].append({
                    'lead_name': lead.full_name,
                    'phone': lead.phone_number,
                    'form': lead.form_name,
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    def call_au_forms_leads(self, since_minutes=60):
        """Call new leads from AU forms specifically"""
        au_forms = [
            'AU without OTP form 06/12/2025, 16:48',
            'AU Leisure Valley form 18/11/2025, 15:11'
        ]
        
        return self.call_new_leads(form_names=au_forms, since_minutes=since_minutes)

# Global instance
auto_call_service = AutoCallService()