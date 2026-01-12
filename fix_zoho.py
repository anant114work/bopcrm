import re

# Read the views.py file
with open('leads/views.py', 'r') as f:
    content = f.read()

# Find the test_zoho_connection function and replace it
old_function = '''@csrf_exempt
def test_zoho_connection(request):
    """Test Zoho API connection"""
    config = ZohoConfig.objects.first()
    if not config or not config.access_token:
        return JsonResponse({'error': 'Zoho not configured or authorized'})
    
    try:
        # Test API call - simple endpoint to verify connection
        headers = {'Authorization': f'Zoho-oauthtoken {config.access_token}'}
        
        # Use a simple test endpoint - correct Zoho Marketing Automation format
        if 'zoho.in' in config.api_domain:
            test_url = "https://marketingautomation.zoho.in/api/v1/getmailinglists.json"
        else:
            test_url = "https://marketingautomation.zoho.com/api/v1/getmailinglists.json"
        
        response = requests.get(test_url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            lists_count = len(data.get('list_of_details', []))
            return JsonResponse({
                'success': True,
                'message': 'Connection successful',
                'api_domain': config.api_domain,
                'response_code': response.status_code,
                'lists_count': lists_count
            })
        elif response.status_code == 401:
            return JsonResponse({
                'success': False,
                'error': 'Invalid access token. Please re-authorize Zoho.',
                'response_code': response.status_code
            })
        else:
            return JsonResponse({
                'success': False,
                'error': f'API Error: HTTP {response.status_code}',
                'response_code': response.status_code,
                'response_text': response.text[:200]
            })
            
    except Exception as e:
        return JsonResponse({'error': str(e)})'''

new_function = '''@csrf_exempt
def test_zoho_connection(request):
    """Test Zoho API connection"""
    config = ZohoConfig.objects.first()
    if not config or not config.access_token:
        return JsonResponse({'error': 'Zoho not configured or authorized'})
    
    try:
        # Test API call - simple endpoint to verify connection
        headers = {'Authorization': f'Zoho-oauthtoken {config.access_token}'}
        
        # Use a simple test endpoint - correct Zoho Marketing Automation format
        if 'zoho.in' in config.api_domain:
            test_url = "https://marketingautomation.zoho.in/api/v1/getmailinglists.json"
        else:
            test_url = "https://marketingautomation.zoho.com/api/v1/getmailinglists.json"
        
        response = requests.get(test_url, headers=headers, timeout=10)
        
        # Check if response has content
        if not response.text.strip():
            return JsonResponse({
                'success': False,
                'error': f'Empty response from Zoho API. Status: {response.status_code}',
                'response_code': response.status_code
            })
        
        try:
            if response.status_code == 200:
                data = response.json()
                lists_count = len(data.get('list_of_details', []))
                return JsonResponse({
                    'success': True,
                    'message': 'Connection successful',
                    'api_domain': config.api_domain,
                    'response_code': response.status_code,
                    'lists_count': lists_count
                })
            elif response.status_code == 401:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid access token. Please re-authorize Zoho.',
                    'response_code': response.status_code
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': f'API Error: HTTP {response.status_code}',
                    'response_code': response.status_code,
                    'response_text': response.text[:200]
                })
        except ValueError as json_error:
            return JsonResponse({
                'success': False,
                'error': f'Invalid JSON response. Status: {response.status_code}, Content: {response.text[:100]}',
                'response_code': response.status_code
            })
            
    except Exception as e:
        return JsonResponse({'error': str(e)})'''

# Replace the function
if old_function in content:
    content = content.replace(old_function, new_function)
    
    # Write back to file
    with open('leads/views.py', 'w') as f:
        f.write(content)
    
    print("Fixed Zoho connection test with proper JSON error handling")
else:
    print("Function not found - manual fix needed")