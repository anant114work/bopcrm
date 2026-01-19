import os
import sys
import django

sys.path.append('d:\\AI-proto\\CRM\\drip')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import Lead
from django.db.models import Q

# Last 5 leads from your sheet data
last_5_leads = [
    {"name": "Manish Agarwal", "phone": "9313772276", "email": "vinmaye19@gmail.com", "date": "20/12/2025 09:46:35"},
    {"name": "Jaiprakash Sharma", "phone": "9909004833", "email": "shrutamglasses@gmail.com", "date": "20/12/2025 11:11:55"},
    {"name": "Githartho sargiwari", "phone": "9101186994", "email": "", "date": "20/12/2025 11:46:32"},
    {"name": "Varun", "phone": "9717665108", "email": "aniljad67@gmail.com", "date": "19/12/2025 15:11:22"},
    {"name": "Subodh jain", "phone": "9711103004", "email": "", "date": "19/12/2025 14:29:21"}
]

print("=== CHECKING LAST 5 SHEET LEADS IN CRM ===")

for i, lead_data in enumerate(last_5_leads, 1):
    phone = lead_data["phone"]
    name = lead_data["name"]
    date = lead_data["date"]
    
    # Check multiple phone formats
    phone_variants = [
        phone,
        f"+91{phone}",
        f"91{phone}",
        phone.replace(" ", ""),
        phone.replace("-", "")
    ]
    
    # Search in CRM
    crm_lead = Lead.objects.filter(
        Q(phone_number__in=phone_variants) | 
        Q(full_name__icontains=name.split()[0])
    ).first()
    
    print(f"\n{i}. {name} ({phone}) - {date}")
    if crm_lead:
        print(f"   FOUND in CRM: {crm_lead.full_name} ({crm_lead.phone_number})")
        print(f"   Source: {crm_lead.source} | Form: {crm_lead.form_name}")
        print(f"   CRM Date: {crm_lead.created_time}")
        print(f"   CRM ID: {crm_lead.id}")
    else:
        print(f"   NOT FOUND in CRM")

print(f"\n=== SUMMARY ===")
print(f"Total Google Sheets leads in CRM: {Lead.objects.filter(source='Google Sheets').count()}")
print(f"Most recent Google Sheets lead: {Lead.objects.filter(source='Google Sheets').order_by('-created_time').first()}")