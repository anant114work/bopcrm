from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .integration_models import MetaConfig, GoogleSheetsConfig
import requests
import json

def integration_panel(request):
    """Admin integration panel"""
    # Check if user is admin through team system or Django admin
    if not (request.session.get('team_member_name') == 'ADMIN USER' or (hasattr(request, 'user') and request.user.is_staff)):
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Access denied. Admin privileges required.")
    
    meta_configs = MetaConfig.objects.all()
    google_configs = GoogleSheetsConfig.objects.all()
    
    return render(request, 'leads/integration_panel.html', {
        'meta_configs': meta_configs,
        'google_configs': google_configs
    })

@csrf_exempt
def save_meta_config(request):
    """Save Meta configuration"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'})
    
    try:
        data = json.loads(request.body)
        
        config, created = MetaConfig.objects.update_or_create(
            page_id=data['page_id'],
            defaults={
                'name': data.get('name', f"Meta Page {data['page_id']}"),
                'access_token': data['access_token'],
                'app_id': data.get('app_id', ''),
                'app_secret': data.get('app_secret', ''),
                'user_access_token': data.get('user_access_token', ''),
                'is_active': data.get('is_active', True)
            }
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Meta config {"created" if created else "updated"}',
            'config_id': config.id
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)})

@csrf_exempt
def save_google_config(request):
    """Save Google Sheets configuration"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'})
    
    try:
        data = json.loads(request.body)
        
        config, created = GoogleSheetsConfig.objects.update_or_create(
            sheet_url=data['sheet_url'],
            defaults={
                'name': data.get('name', 'Google Sheet'),
                'sheet_name': data.get('sheet_name', 'Sheet1'),
                'service_account_json': data.get('service_account_json', ''),
                'is_active': data.get('is_active', True)
            }
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Google config {"created" if created else "updated"}',
            'config_id': config.id
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)})

@csrf_exempt
def test_meta_connection(request):
    """Test Meta API connection"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'})
    
    try:
        data = json.loads(request.body)
        access_token = data['access_token']
        page_id = data['page_id']
        
        # Test API call
        url = f'https://graph.facebook.com/v23.0/{page_id}/leadgen_forms'
        response = requests.get(url, params={'access_token': access_token})
        
        if response.status_code == 200:
            forms_data = response.json()
            forms_count = len(forms_data.get('data', []))
            
            return JsonResponse({
                'success': True,
                'message': f'Connection successful! Found {forms_count} forms',
                'forms_count': forms_count
            })
        else:
            return JsonResponse({
                'success': False,
                'error': f'API Error: {response.status_code} - {response.text}'
            })
            
    except Exception as e:
        return JsonResponse({'error': str(e)})

@csrf_exempt
def test_google_connection(request):
    """Test Google Sheets connection"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'})
    
    try:
        data = json.loads(request.body)
        sheet_url = data['sheet_url']
        
        # Extract sheet ID from URL
        if '/spreadsheets/d/' in sheet_url:
            sheet_id = sheet_url.split('/spreadsheets/d/')[1].split('/')[0]
            csv_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv'
            
            response = requests.get(csv_url)
            if response.status_code == 200:
                lines = response.text.split('\n')
                return JsonResponse({
                    'success': True,
                    'message': f'Connection successful! Found {len(lines)} rows',
                    'rows_count': len(lines)
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Sheet not accessible or not public'
                })
        else:
            return JsonResponse({'error': 'Invalid Google Sheets URL'})
            
    except Exception as e:
        return JsonResponse({'error': str(e)})

@csrf_exempt
def delete_config(request):
    """Delete integration config"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'})
    
    try:
        data = json.loads(request.body)
        config_type = data['type']
        config_id = data['id']
        
        if config_type == 'meta':
            MetaConfig.objects.filter(id=config_id).delete()
        elif config_type == 'google':
            GoogleSheetsConfig.objects.filter(id=config_id).delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Configuration deleted'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)})