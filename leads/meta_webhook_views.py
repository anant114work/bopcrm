from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from .models import Lead
import json
import hmac
import hashlib
from django.conf import settings

# Meta App Secret for webhook verification (add to .env)
META_APP_SECRET = settings.META_APP_SECRET if hasattr(settings, 'META_APP_SECRET') else None

@csrf_exempt
def meta_webhook(request):
    """
    Meta Leadgen Webhook Endpoint
    Receives real-time lead notifications from Meta
    """
    
    if request.method == 'GET':
        # Webhook verification (one-time setup)
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')
        
        # Use a verify token (add to .env: META_VERIFY_TOKEN=your_secret_token)
        VERIFY_TOKEN = getattr(settings, 'META_VERIFY_TOKEN', 'meta_webhook_verify_token_12345')
        
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            print(f"✅ Meta Webhook Verified!")
            return HttpResponse(challenge)
        else:
            print(f"❌ Meta Webhook Verification Failed")
            return HttpResponse('Verification failed', status=403)
    
    elif request.method == 'POST':
        # Verify signature (optional but recommended)
        if META_APP_SECRET:
            signature = request.headers.get('X-Hub-Signature-256', '')
            if signature:
                expected_signature = 'sha256=' + hmac.new(
                    META_APP_SECRET.encode('utf-8'),
                    request.body,
                    hashlib.sha256
                ).hexdigest()
                
                if not hmac.compare_digest(signature, expected_signature):
                    print(f"❌ Invalid signature")
                    return HttpResponse('Invalid signature', status=403)
        
        try:
            data = json.loads(request.body)
            print(f"\n{'='*60}")
            print(f"📥 META WEBHOOK - NEW LEAD RECEIVED")
            print(f"{'='*60}")
            print(f"Data: {json.dumps(data, indent=2)}")
            
            # Process leadgen events
            for entry in data.get('entry', []):
                for change in entry.get('changes', []):
                    if change.get('field') == 'leadgen':
                        leadgen_id = change.get('value', {}).get('leadgen_id')
                        form_id = change.get('value', {}).get('form_id')
                        page_id = change.get('value', {}).get('page_id')
                        created_time = change.get('value', {}).get('created_time')
                        
                        print(f"📋 Lead ID: {leadgen_id}")
                        print(f"📝 Form ID: {form_id}")
                        print(f"📄 Page ID: {page_id}")
                        
                        # Fetch full lead data from Meta API
                        import requests
                        
                        lead_url = f"https://graph.facebook.com/v21.0/{leadgen_id}"
                        params = {
                            'access_token': settings.META_ACCESS_TOKEN,
                            'fields': 'id,created_time,field_data'
                        }
                        
                        response = requests.get(lead_url, params=params)
                        
                        if response.status_code == 200:
                            lead_data = response.json()
                            
                            # Get form name
                            form_url = f"https://graph.facebook.com/v21.0/{form_id}"
                            form_response = requests.get(form_url, params={'access_token': settings.META_ACCESS_TOKEN})
                            form_name = form_response.json().get('name', 'Unknown Form') if form_response.status_code == 200 else 'Unknown Form'
                            
                            # Parse field data
                            field_data = {item['name']: item['values'][0] for item in lead_data.get('field_data', [])}
                            
                            # Parse created_time
                            created_time_str = lead_data.get('created_time')
                            if created_time_str:
                                created_time = parse_datetime(created_time_str)
                            else:
                                created_time = timezone.now()
                            
                            # Check if lead already exists
                            if not Lead.objects.filter(lead_id=leadgen_id).exists():
                                # Create new lead
                                lead = Lead.objects.create(
                                    lead_id=leadgen_id,
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
                                
                                print(f"✅ Lead Created: {lead.full_name} ({lead.phone_number})")
                                print(f"📧 Email: {lead.email}")
                                print(f"🏙️ City: {lead.city}")
                                print(f"💰 Budget: {lead.budget}")
                                print(f"{'='*60}\n")
                                
                                # Auto-assign lead if configured
                                try:
                                    from .team_views import auto_assign_hierarchy
                                    auto_assign_hierarchy(None, lead_id=lead.id)
                                    print(f"✅ Lead auto-assigned")
                                except Exception as e:
                                    print(f"⚠️ Auto-assign failed: {e}")
                                
                            else:
                                print(f"⚠️ Lead already exists: {leadgen_id}")
                        else:
                            print(f"❌ Failed to fetch lead data: {response.text}")
            
            return JsonResponse({'success': True, 'message': 'Webhook processed'})
            
        except Exception as e:
            import traceback
            print(f"❌ Webhook Error: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({'error': str(e)}, status=500)
    
    return HttpResponse('Method not allowed', status=405)
