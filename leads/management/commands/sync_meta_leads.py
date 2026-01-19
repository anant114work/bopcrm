from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.conf import settings
from leads.models import Lead
import requests

class Command(BaseCommand):
    help = 'Sync ALL historical leads from Meta (Facebook)'

    def handle(self, *args, **options):
        ACCESS_TOKEN = settings.META_ACCESS_TOKEN
        PAGE_ID = settings.META_PAGE_ID
        
        if not ACCESS_TOKEN or not PAGE_ID:
            self.stdout.write(self.style.ERROR('META_ACCESS_TOKEN or META_PAGE_ID not configured'))
            return
        
        self.stdout.write('='*60)
        self.stdout.write(self.style.SUCCESS('SYNCING ALL HISTORICAL META LEADS'))
        self.stdout.write('='*60)
        
        # Get all forms
        forms_url = f"https://graph.facebook.com/v21.0/{PAGE_ID}/leadgen_forms"
        forms_response = requests.get(forms_url, params={'access_token': ACCESS_TOKEN})
        
        if forms_response.status_code != 200:
            self.stdout.write(self.style.ERROR(f'Failed to fetch forms: {forms_response.text}'))
            return
        
        forms_data = forms_response.json()
        forms = forms_data.get('data', [])
        
        if not forms:
            self.stdout.write(self.style.WARNING('No forms found'))
            return
        
        self.stdout.write(f'Found {len(forms)} forms')
        
        total_synced = 0
        total_skipped = 0
        
        for idx, form in enumerate(forms, 1):
            form_id = form['id']
            form_name = form.get('name', 'Unknown Form')
            
            self.stdout.write(f'\n[{idx}/{len(forms)}] Processing: {form_name}')
            
            form_synced = 0
            form_skipped = 0
            
            # Fetch ALL leads with pagination
            leads_url = f"https://graph.facebook.com/v21.0/{form_id}/leads"
            params = {
                'access_token': ACCESS_TOKEN,
                'fields': 'id,created_time,field_data',
                'limit': 500
            }
            
            page_num = 1
            while leads_url:
                self.stdout.write(f'  Fetching page {page_num}...', ending='')
                
                leads_response = requests.get(leads_url, params=params)
                
                if leads_response.status_code != 200:
                    self.stdout.write(self.style.ERROR(f' FAILED: {leads_response.text}'))
                    break
                
                leads_data = leads_response.json()
                page_leads = leads_data.get('data', [])
                
                self.stdout.write(f' {len(page_leads)} leads')
                
                for lead_data in page_leads:
                    lead_id = lead_data.get('id')
                    
                    if Lead.objects.filter(lead_id=lead_id).exists():
                        form_skipped += 1
                        continue
                    
                    # Parse field data
                    field_data = {}
                    for item in lead_data.get('field_data', []):
                        field_name = item.get('name', '')
                        field_values = item.get('values', [])
                        if field_values:
                            field_data[field_name] = field_values[0]
                    
                    # Parse created_time
                    created_time_str = lead_data.get('created_time')
                    if created_time_str:
                        created_time = parse_datetime(created_time_str)
                    else:
                        created_time = timezone.now()
                    
                    # Get budget from multiple possible field names
                    budget = (field_data.get('budget', '') or 
                             field_data.get('what_is_your_budget_range?', '') or
                             field_data.get('what_is_your_budget?', ''))
                    
                    # Create lead
                    Lead.objects.create(
                        lead_id=lead_id,
                        full_name=field_data.get('full_name', ''),
                        email=field_data.get('email', ''),
                        phone_number=field_data.get('phone_number', ''),
                        city=field_data.get('city', ''),
                        budget=budget,
                        source='Meta',
                        form_name=form_name,
                        configuration=field_data.get('configuration', ''),
                        created_time=created_time
                    )
                    
                    form_synced += 1
                
                # Check for next page
                paging = leads_data.get('paging', {})
                leads_url = paging.get('next')
                params = {}  # Next URL already has params
                page_num += 1
            
            self.stdout.write(f'  Result: {form_synced} new, {form_skipped} skipped')
            total_synced += form_synced
            total_skipped += form_skipped
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS(f'SYNC COMPLETE'))
        self.stdout.write(self.style.SUCCESS(f'Total New Leads: {total_synced}'))
        self.stdout.write(self.style.WARNING(f'Total Skipped: {total_skipped}'))
        self.stdout.write('='*60)
