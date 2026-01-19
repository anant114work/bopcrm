#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import Lead
from django.db.models import Q

# Check for any remaining fake leads
fake_leads = Lead.objects.filter(
    Q(full_name__in=['John Doe', 'Jane Smith', 'Mike Johnson', 'mmm', 'Sudi']) |
    Q(email__icontains='example.com') |
    Q(phone_number__in=['9876543210', '9876543211', '9876543212', '1234567890'])
)

print(f"Remaining fake leads: {fake_leads.count()}")

if fake_leads.count() > 0:
    for lead in fake_leads:
        print(f"- {lead.full_name} ({lead.email}) - {lead.phone_number}")
else:
    print("[SUCCESS] All fake leads have been successfully removed!")

# Show total leads count
total_leads = Lead.objects.count()
print(f"\nTotal leads in database: {total_leads}")

# Show recent real leads
recent_leads = Lead.objects.exclude(
    Q(full_name__in=['John Doe', 'Jane Smith', 'Mike Johnson', 'mmm', 'Sudi']) |
    Q(email__icontains='example.com')
).order_by('-created_time')[:5]

print(f"\nRecent real leads ({recent_leads.count()}):")
for lead in recent_leads:
    print(f"- {lead.full_name} ({lead.form_name}) - {lead.created_time.strftime('%Y-%m-%d %H:%M')}")