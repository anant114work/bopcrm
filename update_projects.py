#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.project_models import Project

print("Updating project locations and redistributing leads...")

# Update Alaknanda location
try:
    alaknanda = Project.objects.get(code='ALK001')
    alaknanda.location = 'Dehradun'
    alaknanda.save()
    print(f'Updated Alaknanda location to: {alaknanda.location}')
except Project.DoesNotExist:
    print('Alaknanda project not found')

# Update Max Antara location  
try:
    max_antara = Project.objects.get(code='MAX001')
    max_antara.location = 'Gurgaon'
    max_antara.save()
    print(f'Updated Max Antara location to: {max_antara.location}')
except Project.DoesNotExist:
    print('Max Antara project not found')

# Transfer Migsun Alpha Central leads to Migsun Retail
try:
    alpha_central = Project.objects.get(code='PRJ383328')
    migsun_retail = Project.objects.get(code='MIG001')
    
    print(f'Before: Alpha Central has {alpha_central.lead_count} leads')
    print(f'Before: Migsun Retail has {migsun_retail.lead_count} leads')
    
    # Add alpha central keywords to retail
    retail_keywords = list(migsun_retail.form_keywords) + list(alpha_central.form_keywords)
    migsun_retail.form_keywords = list(set(retail_keywords))  # Remove duplicates
    migsun_retail.save()
    
    # Clear alpha central keywords so it shows 0 leads
    alpha_central.form_keywords = []
    alpha_central.save()
    
    print(f'After: Alpha Central has {alpha_central.lead_count} leads')
    print(f'After: Migsun Retail has {migsun_retail.lead_count} leads')
    print('Redistributed Migsun Alpha Central leads to Migsun Retail')
    
except Project.DoesNotExist as e:
    print(f'Project not found: {e}')

print("\nFinal project status:")
for project in Project.objects.all().order_by('name'):
    print(f"{project.name}: {project.location} - {project.lead_count} leads")