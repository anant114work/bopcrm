import os
import django
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import Lead, CallLog, TeamMember
from leads.project_models import Project
from datetime import date

# Get SPJ project
spj = Project.objects.filter(name__icontains='spj').first()
if not spj:
    print('No SPJ project found')
    exit()

print(f'Project: {spj.name} (ID: {spj.id})')

# Get all Google leads with phone numbers
google_leads = spj.get_leads().filter(
    source='Google Sheets',
    phone_number__isnull=False
).exclude(phone_number='')

print(f'Total Google leads: {google_leads.count()}')

# Get already called numbers today
today = date.today()
called_today = CallLog.objects.filter(
    initiated_at__date=today
).values_list('phone_number', flat=True)

excluded_numbers = list(called_today)
print(f'Already called today: {len(excluded_numbers)}')

# Filter out already called
leads_to_call = google_leads.exclude(phone_number__in=excluded_numbers)
print(f'Leads to call: {leads_to_call.count()}')

# Call Karo AI configuration
api_key = "bc422db39aa327234a911dd901accfcfa975623ee84c65c83aae9c4f844ffdb8"
agent_id = "69294d3d2cc1373b1f3a3972"

success = 0
failed = 0

print(f'\nStarting calls...\n')

for lead in leads_to_call[:5]:  # Test with first 5 leads
    try:
        phone = lead.phone_number.strip()
        digits_only = ''.join(filter(str.isdigit, phone))
        
        if len(digits_only) >= 10:
            phone = f"+91{digits_only[-10:]}"
        else:
            print(f'[SKIP] {lead.full_name}: Invalid phone {lead.phone_number}')
            failed += 1
            continue
        
        print(f'[CALLING] {lead.full_name}: {phone}')
        
        payload = {
            "to_number": phone,
            "agent_id": agent_id,
            "metadata": {
                "name": lead.full_name or "Unknown",
                "source": "test_google_call",
                "project": spj.name,
                "lead_source": lead.source
            },
            "priority": 1,
            "language": "hi"
        }
        
        response = requests.post(
            "https://api.callkaro.ai/call/outbound",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "X-API-KEY": api_key
            },
            timeout=10
        )
        
        if response.status_code == 200:
            api_response = response.json()
            call_sid = api_response.get('call_sid', '')
            print(f'[SUCCESS] Call initiated: {call_sid}')
            
            # Log the call
            admin_user = TeamMember.objects.filter(role='Admin').first() or TeamMember.objects.first()
            CallLog.objects.create(
                lead=lead,
                team_member=admin_user,
                phone_number=phone,
                call_type='test_google_call',
                status='initiated',
                call_sid=call_sid
            )
            
            success += 1
        else:
            print(f'[FAILED] Status: {response.status_code}, Response: {response.text}')
            failed += 1
            
    except Exception as e:
        print(f'[ERROR] {lead.full_name}: {str(e)}')
        failed += 1

print(f'\n{"="*60}')
print(f'Success: {success}')
print(f'Failed: {failed}')
print(f'{"="*60}')
