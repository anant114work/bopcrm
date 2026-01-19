#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import Lead
from django.db.models import Q

# Find remaining fake leads
remaining_fake = Lead.objects.filter(
    Q(full_name__in=['mmm', 'Sudi']) |
    Q(email__icontains='contact@example.com') |
    Q(email__icontains='ancdef@gmail.com')
)

print(f"Found {remaining_fake.count()} remaining fake leads:")

for lead in remaining_fake:
    print(f"- {lead.full_name} ({lead.email}) - {lead.phone_number}")
    
    # Check all related objects
    from leads.models import LeadAssignment, LeadNote
    try:
        from tata_integration.models import TataCall
        calls = TataCall.objects.filter(lead=lead)
        print(f"  - Has {calls.count()} call records")
        calls.delete()
    except:
        pass
    
    try:
        from leads.whatsapp_models import WhatsAppCampaignAssignment
        campaigns = WhatsAppCampaignAssignment.objects.filter(lead=lead)
        print(f"  - Has {campaigns.count()} campaign assignments")
        campaigns.delete()
    except:
        pass
    
    try:
        from leads.models import ScheduledMessage
        messages = ScheduledMessage.objects.filter(lead=lead)
        print(f"  - Has {messages.count()} scheduled messages")
        messages.delete()
    except:
        pass
    
    # Delete assignments and notes
    assignments = LeadAssignment.objects.filter(lead=lead)
    notes = LeadNote.objects.filter(lead=lead)
    print(f"  - Has {assignments.count()} assignments, {notes.count()} notes")
    
    assignments.delete()
    notes.delete()
    
    # Now try to delete the lead
    try:
        lead.delete()
        print(f"  [OK] Deleted {lead.full_name}")
    except Exception as e:
        print(f"  [ERROR] Still can't delete {lead.full_name}: {e}")

print("\nCleanup completed!")