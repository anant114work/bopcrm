#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import Lead

# Remove fake/test leads
from django.db.models import Q

fake_leads = Lead.objects.filter(
    Q(full_name__in=['John Doe', 'Jane Smith', 'Mike Johnson']) |
    Q(email__icontains='example.com') |
    Q(phone_number__in=['9876543210', '9876543211', '9876543212'])
)

count = fake_leads.count()
print(f"Found {count} fake leads to delete:")

for lead in fake_leads:
    print(f"- {lead.full_name} ({lead.email}) - {lead.phone_number}")

if count > 0:
    # Delete each lead individually with its relationships
    from leads.models import LeadAssignment, LeadNote
    
    deleted_count = 0
    for lead in fake_leads:
        try:
            # Delete assignments
            LeadAssignment.objects.filter(lead=lead).delete()
            # Delete notes
            LeadNote.objects.filter(lead=lead).delete()
            # Delete the lead
            lead.delete()
            deleted_count += 1
            print(f"[OK] Deleted {lead.full_name}")
        except Exception as e:
            print(f"[ERROR] Failed to delete {lead.full_name}: {e}")
    
    print(f"\nDeleted {deleted_count}/{count} fake leads successfully!")
else:
    print("No fake leads found.")