import os
import django
from enhanced_meta_client import EnhancedMetaClient

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drip.settings')
django.setup()

def fix_meta_leads_sync():
    """Fix Meta leads sync to get ALL leads with spend data"""
    from leads.models import Lead
    from django.utils import timezone
    
    # Your credentials
    ACCESS_TOKEN = "EAAgVjAbsIWoBPw4ggkNHJaO3igkkILRQ1ccESdGdhJp7wrZAHYIExnD2xbvZCxHXPQZAzvtd4nxDq2gj3STKTpcs9CMfv9YjZAf507vQIkwKYZBzCzqhKHcpa1wDecXRBxLx4YH3AUG1QzeMxfUZCF7EsJtVwwTMZBpwf6xavBZBx9N6EplcTeL0CuZBDDKa83JxEpXAwOhT6KFQ0SNbvp3GUliKIz6WrWhLsIATtGed2hQ3egRo4W49cVlD6vfdJOZB5vYZBseuk155XLFjVrFdsU6LAZDZD"
    PAGE_ID = "724725327387557"  # The Great Indian Property Show
    ACCOUNT_ID = "105849243396571"  # ABC Digital
    
    client = EnhancedMetaClient(ACCESS_TOKEN)
    
    # Get all leads with spend data
    result = client.sync_leads_with_spend(PAGE_ID, ACCOUNT_ID)
    
    if 'error' in result:
        print(f"Error: {result['error']}")
        return
    
    synced_count = 0
    
    for lead_data in result['leads']:
        # Extract lead info
        lead_id = lead_data['id']
        created_time = lead_data['created_time']
        
        # Extract field data (name, email, phone)
        field_data = lead_data.get('field_data', [])
        lead_info = {}
        for field in field_data:
            field_name = field.get('name', '').lower()
            field_value = field.get('values', [''])[0]
            
            if 'email' in field_name:
                lead_info['email'] = field_value
            elif 'phone' in field_name or 'mobile' in field_name:
                lead_info['phone'] = field_value
            elif 'name' in field_name and 'full' in field_name:
                lead_info['name'] = field_value
        
        # Extract spend data
        campaign_spend = 0
        adset_spend = 0
        ad_spend = 0
        
        if 'campaign_data' in lead_data:
            insights = lead_data['campaign_data'].get('insights', {}).get('data', [])
            if insights:
                campaign_spend = float(insights[0].get('spend', 0))
        
        if 'adset_data' in lead_data:
            insights = lead_data['adset_data'].get('insights', {}).get('data', [])
            if insights:
                adset_spend = float(insights[0].get('spend', 0))
        
        if 'ad_data' in lead_data:
            insights = lead_data['ad_data'].get('insights', {}).get('data', [])
            if insights:
                ad_spend = float(insights[0].get('spend', 0))
        
        # Create or update lead
        lead, created = Lead.objects.update_or_create(
            meta_lead_id=lead_id,
            defaults={
                'lead_id': lead_id,
                'full_name': lead_info.get('name', ''),
                'email': lead_info.get('email', ''),
                'phone_number': lead_info.get('phone', ''),
                'source': 'Meta',
                'campaign_id': lead_data.get('campaign_id', ''),
                'adset_id': lead_data.get('adset_id', ''),
                'ad_id': lead_data.get('ad_id', ''),
                'form_id': lead_data.get('form_id', ''),
                'form_name': lead_data.get('form_name', ''),
                'campaign_spend': campaign_spend,
                'adset_spend': adset_spend,
                'ad_spend': ad_spend,
                'created_at': timezone.now()
            }
        )
        
        if created:
            synced_count += 1
    
    print(f"Synced {synced_count} new leads out of {result['total_leads']} total")
    return synced_count

if __name__ == "__main__":
    fix_meta_leads_sync()