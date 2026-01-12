from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Lead
from .bop_sync import sync_lead_to_bop_crm

@csrf_exempt
def test_bop_sync(request, lead_id):
    """Test BOP CRM sync for a specific lead"""
    try:
        lead = Lead.objects.get(id=lead_id)
        print(f"[BOP TEST] Testing sync for lead: {lead.full_name} ({lead.phone_number})")
        
        success, message = sync_lead_to_bop_crm(lead)
        
        return JsonResponse({
            'success': success,
            'message': message,
            'lead_name': lead.full_name,
            'lead_phone': lead.phone_number
        })
        
    except Lead.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Lead not found'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })