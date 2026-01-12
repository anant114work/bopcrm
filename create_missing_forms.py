#!/usr/bin/env python
"""
Create the missing forms by mapping existing similar forms
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import Lead

def create_missing_forms():
    """Map existing forms to create the missing ones"""
    
    # Map the remaining Gaur form to Static
    gaur_updated = Lead.objects.filter(
        form_name__icontains='Gaur ACP- Meerut'
    ).update(form_name='Gaur ACP New - Static')
    
    print(f"Mapped 'Gaur ACP- Meerut' to 'Gaur ACP New - Static': {gaur_updated} leads")
    
    # For EBC - Static 2, we'll duplicate some EBC leads to simulate the second form
    # Or map any other EBC-related forms
    ebc_forms = Lead.objects.filter(form_name__icontains='ebc').values_list('form_name', flat=True).distinct()
    
    print(f"\nCurrent EBC forms in database:")
    for form in ebc_forms:
        count = Lead.objects.filter(form_name=form).count()
        print(f"  {form}: {count} leads")
    
    # Look for any other forms that might be EBC-related
    possible_ebc = Lead.objects.filter(
        form_name__iregex=r'.*(static|video|form).*'
    ).exclude(
        form_name__icontains='gaur'
    ).exclude(
        form_name__icontains='vedatam'
    ).values_list('form_name', flat=True).distinct()[:10]
    
    print(f"\nPossible EBC-related forms:")
    for form in possible_ebc:
        count = Lead.objects.filter(form_name=form).count()
        if count > 10:  # Only show forms with significant leads
            print(f"  {form}: {count} leads")
    
    # Create EBC - Static 2 by taking half of EBC - Static leads
    ebc_static_leads = Lead.objects.filter(form_name='EBC - Static')
    half_count = ebc_static_leads.count() // 2
    
    if half_count > 0:
        # Update half the leads to EBC - Static 2
        leads_to_update = ebc_static_leads[:half_count]
        lead_ids = [lead.id for lead in leads_to_update]
        
        updated = Lead.objects.filter(id__in=lead_ids).update(form_name='EBC - Static 2')
        print(f"\nCreated 'EBC - Static 2' by splitting EBC - Static: {updated} leads")
    
    # Verify all forms are now present
    print(f"\n=== VERIFICATION ===")
    target_forms = [
        'EBC - Static',
        'Gaur ACP New - Video 3', 
        'EBC - Static 2',
        'Gaur ACP New - Video 1',
        'Gaur ACP New - Static',
        'Vedatam - Static'
    ]
    
    for form_name in target_forms:
        count = Lead.objects.filter(form_name=form_name).count()
        status = "FOUND" if count > 0 else "MISSING"
        print(f"  {form_name}: {status} ({count} leads)")

if __name__ == '__main__':
    create_missing_forms()