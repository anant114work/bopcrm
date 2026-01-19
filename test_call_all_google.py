import os
import django
import requests
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import Lead, CallLog, TeamMember
from leads.project_models import Project
from datetime import date

spj = Project.objects.filter(name__icontains='spj').first()
if not spj:
    print('No SPJ project found')
    exit()

print(f'Project: {spj.name}')

google_leads = spj.get_leads().filter(
    source='Google Sheets',
    phone_number__isnull=False
).exclude(phone_number='')

today = date.today()
called_today = CallLog.objects.filter(
    initiated_at__date=today,
    call_type__contains='google'
).values_list('phone_number', flat=True)

excluded = list(called_today)
leads_to_call = google_leads.exclude(phone_number__in=excluded)

print(f'Total Google leads: {google_leads.count()}')
print(f'Already called: {len(excluded)}')
print(f'To call: {leads_to_call.count()}')

api_key = "bc422db39aa327234a911dd901accfcfa975623ee84c65c83aae9c4f844ffdb8"
agent_id = "69294d3d2cc1373b1f3a3972"

success = 0
failed = 0

print(f'\nStarting calls...\n')

for i, lead in enumerate(leads_to_call, 1):
    try:
        phone = lead.phone_number.strip()
        digits_only = ''.join(filter(str.isdigit, phone))
        
        if len(digits_only) < 10:
            print(f'[{i}/{leads_to_call.count()}] SKIP: {lead.full_name} - Invalid phone')
            failed += 1
            continue
        
        phone = f"+91{digits_only[-10:]}"
        
        print(f'[{i}/{leads_to_call.count()}] Calling: {lead.full_name} ({phone})')
        
        payload = {
            "to_number": phone,
            "agent_id": agent_id,
            "metadata": {
                "name": lead.full_name or "Unknown",
                "source": "auto_call_all_google",
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
            
            admin_user = TeamMember.objects.filter(role='Admin').first() or TeamMember.objects.first()
            CallLog.objects.create(
                lead=lead,
                team_member=admin_user,
                phone_number=phone,
                call_type='auto_call_all_google',
                status='initiated',
                call_sid=call_sid
            )
            
            success += 1
            print(f'  SUCCESS: {call_sid}')
        else:
            print(f'  FAILED: {response.status_code}')
            failed += 1
        
        # Small delay between calls
        time.sleep(0.5)
            
    except Exception as e:
        print(f'  ERROR: {str(e)}')
        failed += 1

print(f'\n{"="*60}')
print(f'SUCCESS: {success}')
print(f'FAILED: {failed}')
print(f'{"="*60}')
