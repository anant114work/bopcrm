import re

# Read the views.py file
with open('leads/views.py', 'r') as f:
    content = f.read()

# Find and replace the test_zoho_connection function
old_pattern = r'        response = requests\.get\(test_url, headers=headers\)\s+if response\.status_code == 200:\s+data = response\.json\(\)\s+lists_count = len\(data\.get\(\'list_of_details\', \[\]\)\)\s+return JsonResponse\(\{\s+\'success\': True,\s+\'message\': \'Connection successful\',\s+\'api_domain\': config\.api_domain,\s+\'response_code\': response\.status_code,\s+\'lists_count\': lists_count\s+\}\)\s+elif response\.status_code == 401:\s+return JsonResponse\(\{\s+\'success\': False,\s+\'error\': \'Invalid access token\. Please re-authorize Zoho\.\',\s+\'response_code\': response\.status_code\s+\}\)\s+else:\s+return JsonResponse\(\{\s+\'success\': False,\s+\'error\': f\'API Error: HTTP \{response\.status_code\}\',\s+\'response_code\': response\.status_code,\s+\'response_text\': response\.text\[:200\]\s+\}\)'

new_code = '''        response = requests.get(test_url, headers=headers)
        
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
        except ValueError:
            return JsonResponse({
                'success': False,
                'error': f'Invalid JSON response. Status: {response.status_code}',
                'response_code': response.status_code,
                'response_text': response.text[:200]
            })'''

# Simple replacement approach
old_section = '''        response = requests.get(test_url, headers=headers)
        
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
            })'''

if old_section in content:
    content = content.replace(old_section, new_code)
    
    # Write back to file
    with open('leads/views.py', 'w') as f:
        f.write(content)
    
    print("Fixed Zoho JSON parsing error handling")
else:
    print("Pattern not found in file")