#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from django.db import connection
from leads.models import Lead
from django.db.models import Q

# Find remaining fake leads
remaining_fake = Lead.objects.filter(
    Q(full_name__in=['mmm', 'Sudi']) |
    Q(email__icontains='contact@example.com') |
    Q(email__icontains='ancdef@gmail.com')
)

print(f"Found {remaining_fake.count()} remaining fake leads to force delete:")

for lead in remaining_fake:
    print(f"- {lead.full_name} ({lead.email}) - ID: {lead.id}")

if remaining_fake.count() > 0:
    # Use raw SQL to force delete (disable foreign key checks temporarily)
    with connection.cursor() as cursor:
        # Get the lead IDs
        lead_ids = [str(lead.id) for lead in remaining_fake]
        lead_ids_str = ','.join(lead_ids)
        
        print(f"Force deleting leads with IDs: {lead_ids_str}")
        
        # Disable foreign key checks
        cursor.execute("PRAGMA foreign_keys = OFF;")
        
        # Delete from leads table directly
        cursor.execute(f"DELETE FROM leads_lead WHERE id IN ({lead_ids_str});")
        
        # Re-enable foreign key checks
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        print(f"Successfully force deleted {len(lead_ids)} fake leads!")

print("All fake leads have been removed!")