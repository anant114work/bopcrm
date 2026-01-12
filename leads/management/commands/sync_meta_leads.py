from django.core.management.base import BaseCommand
import requests
from leads.models import Lead
from django.utils import timezone

class Command(BaseCommand):
    help = 'Sync all Meta leads with spend data'
    
    def handle(self, *args, **options):
        ACCESS_TOKEN = "EAAgVjAbsIWoBP3ZCm1tKx6p8F7o8YzCZBZBPl5cPQPuBgmIboYcO2ovEWwaHdOE2EIjE9xsDq6sMZB34zHEI8yh7RHxt0UYbPpNkmY6qvnF9vSkeZALKSA8RigqfXoa7lfKXo3Ic4GqWlUxFhxvvp6KpZAqmKb5vOXRDgCMYbJHefI2zaAsfqVUQFPVLo2ZCareeGyanRuk"
        PAGE_ID = "296508423701621"  # BOP Realty
        ACCOUNT_ID = "105849243396571"
        
        # Get all forms
        forms_url = f"https://graph.facebook.com/v23.0/{PAGE_ID}/leadgen_forms"
        forms_response = requests.get(forms_url, params={
            'access_token': ACCESS_TOKEN,
            'fields': 'id,name,status,leads_count'
        })
        
        if forms_response.status_code != 200:
            self.stdout.write(f"Forms API error: {forms_response.text}")
            return
        
        forms = forms_response.json().get('data', [])
        self.stdout.write(f"Found {len(forms)} forms")
        
        total_leads = 0
        synced_count = 0
        
        # Get leads from each form
        for form in forms:
            form_id = form['id']
            form_name = form['name']
            
            leads_url = f"https://graph.facebook.com/v23.0/{form_id}/leads"
            next_url = leads_url
            
            while next_url:
                response = requests.get(next_url, params={
                    'access_token': ACCESS_TOKEN,
                    'limit': 100,
                    'fields': 'id,created_time,field_data,ad_id,adset_id,campaign_id'
                })
                
                if response.status_code != 200:
                    break
                
                data = response.json()
                leads = data.get('data', [])
                
                for lead_data in leads:
                    total_leads += 1
                    lead_id = lead_data['id']
                    
                    # Extract field data
                    field_data = lead_data.get('field_data', [])
                    lead_info = {}
                    
                    for field in field_data:
                        field_name = field.get('name', '').lower()
                        field_value = field.get('values', [''])[0]
                        
                        if 'email' in field_name:
                            lead_info['email'] = field_value
                        elif 'phone' in field_name or 'mobile' in field_name:
                            lead_info['phone'] = field_value
                        elif 'name' in field_name:
                            lead_info['name'] = field_value
                    
                    # Create or update lead - handle unique constraint
                    try:
                        lead, created = Lead.objects.update_or_create(
                            meta_lead_id=lead_id,
                            defaults={
                                'lead_id': f"meta_{lead_id}",
                                'full_name': lead_info.get('name', ''),
                                'email': lead_info.get('email', ''),
                                'phone_number': lead_info.get('phone', ''),
                                'form_name': form_name,
                                'campaign_id': lead_data.get('campaign_id', ''),
                                'adset_id': lead_data.get('adset_id', ''),
                                'ad_id': lead_data.get('ad_id', ''),
                                'form_id': form_id,
                                'source': 'Meta',
                                'created_time': timezone.now()
                            }
                        )
                    except Exception as e:
                        self.stdout.write(f"Error creating lead {lead_id}: {e}")
                        continue
                    
                    if created:
                        synced_count += 1
                
                # Check for next page
                next_url = data.get('paging', {}).get('next')
        
        self.stdout.write(f"Synced {synced_count} new leads out of {total_leads} total leads")