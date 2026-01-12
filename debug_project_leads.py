#!/usr/bin/env python3
"""
Debug Project Leads Issue
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

def debug_project_leads():
    """Debug why project shows 0 leads"""
    print("DEBUGGING PROJECT LEADS")
    print("=" * 40)
    
    # Get AU project
    au_project = Project.objects.filter(name__icontains='AU Aspire').first()
    
    if not au_project:
        print("AU project not found!")
        return
    
    print(f"Project: {au_project.name}")
    print(f"ID: {au_project.id}")
    
    # Check form mappings
    mappings = FormSourceMapping.objects.filter(project=au_project, is_active=True)
    print(f"Active form mappings: {mappings.count()}")
    
    for mapping in mappings:
        print(f"  Form: {mapping.form_name}")
        
        # Check leads for this exact form name
        exact_leads = Lead.objects.filter(form_name__iexact=mapping.form_name)
        contains_leads = Lead.objects.filter(form_name__icontains=mapping.form_name)
        
        print(f"    Exact match leads: {exact_leads.count()}")
        print(f"    Contains match leads: {contains_leads.count()}")
        
        if exact_leads.count() > 0:
            recent = exact_leads.order_by('-created_time')[:3]
            for lead in recent:
                print(f"      {lead.full_name} - {lead.created_time}")
    
    # Test project.get_leads() method
    project_leads = au_project.get_leads()
    print(f"\nProject get_leads() method: {project_leads.count()}")
    
    # Check if team filtering is the issue
    all_au_leads = Lead.objects.filter(form_name__icontains='AU')
    print(f"All AU leads in system: {all_au_leads.count()}")

if __name__ == "__main__":
    debug_project_leads()
    print("\nDEBUG COMPLETE!")