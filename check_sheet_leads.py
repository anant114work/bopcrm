import os
import sys
import django

sys.path.append('d:\\AI-proto\\CRM\\drip')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import Lead
from django.db.models import Q

# Your sheet data
sheet_leads = [
    {"name": "Anil Kumar", "phone": "7015837345", "email": "anilparbhuwala1@gmail.com"},
    {"name": "Satya pramanik", "phone": "8130118019", "email": "satyapramaniksmb@gmail.com"},
    {"name": "Chinedu onyekelu", "phone": "9863543954", "email": "chineduonyekelu0@gmail.com"},
    {"name": "Praveen Kumar", "phone": "7042628066", "email": "pkhdfc0439@gmail.com"},
    {"name": "Subhashu", "phone": "9810890895", "email": ""},
    {"name": "Sanjana", "phone": "9029187544", "email": "sanjnavalmiki558@gmail.com"},
    {"name": "Kanha", "phone": "9555516935", "email": ""},
    {"name": "Kaif khan", "phone": "9235351936", "email": ""},
    {"name": "Ajay Kumar Das", "phone": "7044145429", "email": "ajaykumardas18@gmail.com"},
    {"name": "D. V. Mittal", "phone": "9911912299", "email": ""},
    {"name": "Rakesh Chawla", "phone": "9999453225", "email": "realtychawla@gmail.com"},
    {"name": "MD Hask", "phone": "7775065369", "email": "mdhask99@gmail.com"},
    {"name": "Anil kumar Rawat", "phone": "9210881700", "email": "anilrawat1700@gmail.com"},
    {"name": "Mukesh Chaudhary", "phone": "7838964509", "email": "mukesh4139@gmail.com"},
    {"name": "Ashish Goyal", "phone": "9871032444", "email": ""},
]

print("=== CHECKING SHEET LEADS IN CRM ===")
print(f"Checking {len(sheet_leads)} leads from your sheet data...")

found_count = 0
missing_count = 0

for lead_data in sheet_leads:
    phone = lead_data["phone"]
    name = lead_data["name"]
    
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
        Q(full_name__icontains=name.split()[0])  # Search by first name
    ).first()
    
    if crm_lead:
        print(f"FOUND: {name} ({phone}) -> CRM: {crm_lead.full_name} ({crm_lead.phone_number}) - {crm_lead.source}")
        found_count += 1
    else:
        print(f"MISSING: {name} ({phone})")
        missing_count += 1

print(f"\n=== SUMMARY ===")
print(f"Found in CRM: {found_count}")
print(f"Missing from CRM: {missing_count}")
print(f"Total Google Sheets leads in CRM: {Lead.objects.filter(source='Google Sheets').count()}")