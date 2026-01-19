import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import django
from django.conf import settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drip.settings')
django.setup()

from enhanced_meta_client import EnhancedMetaClient
from leads.models import Lead
from django.utils import timezone

ACCESS_TOKEN = "EAAgVjAbsIWoBPw4ggkNHJaO3igkkILRQ1ccESdGdhJp7wrZAHYIExnD2xbvZCxHXPQZAzvtd4nxDq2gj3STKTpcs9CMfv9YjZAf507vQIkwKYZBzCzqhKHcpa1wDecXRBxLx4YH3AUG1QzeMxfUZCF7EsJtVwwTMZBpwf6xavBZBx9N6EplcTeL0CuZBDDKa83JxEpXAwOhT6KFQ0SNbvp3GUliKIz6WrWhLsIATtGed2hQ3egRo4W49cVlD6vfdJOZB5vYZBseuk155XLFjVrFdsU6LAZDZD"
PAGE_ID = "724725327387557"
ACCOUNT_ID = "105849243396571"

client = EnhancedMetaClient(ACCESS_TOKEN)
result = client.sync_leads_with_spend(PAGE_ID, ACCOUNT_ID)

if 'error' in result:
    print(f"Error: {result['error']}")
else:
    synced_count = 0
    for lead_data in result['leads']:
        lead_id = lead_data['id']
        field_data = lead_data.get('field_data', [])
        lead_info = {}
        
        for field in field_data:
            field_name = field.get('name', '').lower()
            field_value = field.get('values', [''])[0]
            if 'email' in field_name:
                lead_info['email'] = field_value
            elif 'phone' in field_name:
                lead_info['phone'] = field_value
            elif 'name' in field_name:
                lead_info['name'] = field_value
        
        lead, created = Lead.objects.update_or_create(
            meta_lead_id=lead_id,
            defaults={
                'lead_id': lead_id,
                'full_name': lead_info.get('name', ''),
                'email': lead_info.get('email', ''),
                'phone_number': lead_info.get('phone', ''),
                'form_name': lead_data.get('form_name', ''),
                'created_time': timezone.now()
            }
        )
        
        if created:
            synced_count += 1
    
    print(f"Synced {synced_count} new leads out of {result['total_leads']} total")