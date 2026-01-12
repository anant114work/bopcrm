#!/usr/bin/env python3
"""
Check Project Form Mapping
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.project_models import Project
from leads.form_mapping_models import FormSourceMapping
from leads.models import Lead

def check_au_project():
    """Check AU project mapping"""
    print("CHECKING AU PROJECT MAPPING")
    print("=" * 40)
    
    # Find AU project
    au_projects = Project.objects.filter(name__icontains='AU')
    
    for project in au_projects:
        print(f"\nProject: {project.name}")
        print(f"Developer: {project.developer}")
        
        # Check form mappings
        mappings = FormSourceMapping.objects.filter(project=project, is_active=True)
        print(f"Form mappings: {mappings.count()}")
        
        for mapping in mappings:
            print(f"  - {mapping.form_name}")
            
            # Check leads for this form
            leads = Lead.objects.filter(form_name__iexact=mapping.form_name)
            print(f"    Leads: {leads.count()}")
            
            if leads.count() > 0:
                recent = leads.order_by('-created_time')[:3]
                for lead in recent:
                    print(f"      {lead.full_name} - {lead.created_time.strftime('%Y-%m-%d %H:%M')}")
        
        # Check project's get_leads method
        project_leads = project.get_leads()
        print(f"Project get_leads(): {project_leads.count()}")

def check_au_forms():
    """Check AU forms in leads"""
    print("\nCHECKING AU FORMS IN LEADS")
    print("=" * 40)
    
    au_forms = Lead.objects.filter(form_name__icontains='AU').values_list('form_name', flat=True).distinct()
    
    print(f"Found {len(au_forms)} AU forms:")
    for form in au_forms:
        count = Lead.objects.filter(form_name=form).count()
        print(f"  {form}: {count} leads")

if __name__ == "__main__":
    check_au_project()
    check_au_forms()
    print("\nCHECK COMPLETE!")