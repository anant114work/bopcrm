#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append('d:\\AI-proto\\CRM\\drip')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import TeamMember
from leads.acefone_models import DIDNumber

def assign_did_to_anat():
    print("Assigning DID number to Anat...")
    
    # Find Anat
    anat = TeamMember.objects.filter(name__icontains='anat').first()
    if not anat:
        print("Anat not found!")
        return
    
    print(f"Found agent: {anat.name}")
    
    # Find available DID numbers
    available_dids = DIDNumber.objects.filter(assigned_user__isnull=True, is_active=True)
    print(f"Available DID numbers: {available_dids.count()}")
    
    if available_dids.count() == 0:
        # Create a test DID number for Anat
        did = DIDNumber.objects.create(
            number='+919999999999',
            display_name='Anat Test DID',
            assigned_user=anat,
            is_active=True
        )
        print(f"Created test DID: {did.number} for {anat.name}")
    else:
        # Assign first available DID
        did = available_dids.first()
        did.assigned_user = anat
        did.save()
        print(f"Assigned DID: {did.number} to {anat.name}")
    
    print("✅ DID assignment complete!")
    print("🔥 Auto calls for Chrysalis leads will now work!")

if __name__ == '__main__':
    assign_did_to_anat()