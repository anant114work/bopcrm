import requests
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def simple_ai_call(request):
    """Simple AI call using Call Karo AI"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            phone_number = data.get('phone_number')
            lead_name = data.get('lead_name', 'Lead')
            
            if not phone_number:
                return JsonResponse({'error': 'Phone number required'}, status=400)
            
            # Your API key and agent ID
            api_key = "bc422db39aa327234a911dd901accfcfa975623ee84c65c83aae9c4f844ffdb8"
            agent_id = "69294d3d2cc1373b1f3a3972"  # Updated agent ID
            
            # Call Karo AI API
            url = "https://api.callkaro.ai/call/outbound"
            headers = {
                "Content-Type": "application/json",
                "X-API-KEY": api_key
            }
            
            payload = {
                "to_number": phone_number,
                "agent_id": agent_id,
                "metadata": {
                    "name": lead_name,
                    "source": "CRM"
                }
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return JsonResponse({
                    'success': True,
                    'message': f'AI call initiated to {phone_number}',
                    'call_id': result.get('call_id')
                })
            else:
                error_data = response.json() if response.content else {}
                return JsonResponse({
                    'success': False,
                    'error': error_data.get('message', f'API Error: {response.status_code}')
                }, status=400)
                
        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': f'Network error: {str(e)}'}, status=500)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)