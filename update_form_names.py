#!/usr/bin/env python
"""
Update form names to match current ad names
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import Lead

def update_form_names():
    """Update existing form names to match current ads"""
    
    # Mapping: old_name_pattern -> new_name
    form_mappings = {
        'SPJ Vedatam': 'Vedatam - Static',
        'EBC form': 'EBC - Static', 
        'Gaur ACP- Meerut': 'Gaur ACP New - Video 3',
        'Gaur ACP - UP': 'Gaur ACP New - Video 1', 
        'Gaur ACP - Agra': 'Gaur ACP New - Static'
    }
    
    print("Updating form names to match current ads...")
    
    total_updated = 0
    
    for old_pattern, new_name in form_mappings.items():
        # Find leads with old form name pattern
        leads = Lead.objects.filter(form_name__icontains=old_pattern)
        count = leads.count()
        
        if count > 0:
            # Update all matching leads
            updated = leads.update(form_name=new_name)
            print(f"Updated {updated} leads: '{old_pattern}' -> '{new_name}'")
            total_updated += updated
        else:
            print(f"No leads found for pattern: '{old_pattern}'")
    
    print(f"\nTotal leads updated: {total_updated}")
    
    # Show current form names after update
    print("\nCurrent form names containing your keywords:")
    keywords = ['vedatam', 'ebc', 'gaur acp']
    
    for keyword in keywords:
        forms = Lead.objects.filter(form_name__icontains=keyword).values_list('form_name', flat=True).distinct()
        print(f"\n{keyword.upper()} forms:")
        for form in forms[:5]:  # Show first 5
            count = Lead.objects.filter(form_name=form).count()
            print(f"  {form} ({count} leads)")

if __name__ == '__main__':
    update_form_names()