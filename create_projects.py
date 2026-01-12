#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.project_models import Project

# Create 15 key projects based on form names and existing data
projects_data = [
    {
        'name': 'Godrej Avenue 9',
        'code': 'PRJ408248',
        'developer': 'Godrej',
        'location': 'Greater Noida',
        'form_keywords': ['godrej avenue', 'avenue 9', 'avenue nine']
    },
    {
        'name': 'Migsun Alpha Central',
        'code': 'PRJ383328',
        'developer': 'Migsun',
        'location': 'Greater Noida',
        'form_keywords': ['migsun alpha', 'alpha central', 'migsun-alpha']
    },
    {
        'name': 'Shapoorji Pallonji Dualis',
        'code': 'PRJ301835',
        'developer': 'Shapoorji Pallonji',
        'location': 'Gurgaon',
        'form_keywords': ['spj', 'dualis', 'shapoorji']
    },
    {
        'name': 'Ekana Business Centre',
        'code': 'PRJ441055',
        'developer': 'EBC',
        'location': 'Lucknow',
        'form_keywords': ['ebc', 'ekana']
    },
    {
        'name': 'Gaur Aspire Centurion Park',
        'code': 'PRJ350002',
        'developer': 'Gaurs',
        'location': 'Greater Noida',
        'form_keywords': ['gaur', 'centurian', 'aspire', 'leisure park']
    },
    {
        'name': 'Godrej Majesty',
        'code': 'GVH002',
        'developer': 'Godrej',
        'location': 'Greater Noida',
        'form_keywords': ['majesty']
    },
    {
        'name': 'Hi-Life',
        'code': 'PRJ326114',
        'developer': 'Yatharth & Great Value',
        'location': 'Greater Noida',
        'form_keywords': ['hi-life', 'hilife']
    },
    {
        'name': 'Migsun Retail',
        'code': 'MIG001',
        'developer': 'Migsun',
        'location': 'Greater Noida',
        'form_keywords': ['migsun retail', 'migsun-retail']
    },
    {
        'name': 'Migsun Studio',
        'code': 'MIG002',
        'developer': 'Migsun',
        'location': 'Greater Noida',
        'form_keywords': ['migsun-studio', 'studio']
    },
    {
        'name': 'Eldeco',
        'code': 'ELD001',
        'developer': 'Eldeco',
        'location': 'Greater Noida',
        'form_keywords': ['eldeco']
    },
    {
        'name': 'Max Antara',
        'code': 'MAX001',
        'developer': 'Max Estate',
        'location': 'Noida',
        'form_keywords': ['max antara', 'max estate', 'max-']
    },
    {
        'name': 'Lodha Vrindavan',
        'code': 'PRJ499270',
        'developer': 'HOABL',
        'location': 'Vrindavan',
        'form_keywords': ['lodha', 'vrindavan']
    },
    {
        'name': 'Great India Homes',
        'code': 'GIH001',
        'developer': 'Great India',
        'location': 'Greater Noida',
        'form_keywords': ['great india']
    },
    {
        'name': 'Bhutani Grand Central',
        'code': 'SKY001',
        'developer': 'Bhutani',
        'location': 'Noida',
        'form_keywords': ['bgc', 'bhutani', 'grand central']
    },
    {
        'name': 'Alaknanda',
        'code': 'ALK001',
        'developer': 'Alaknanda Group',
        'location': 'Delhi',
        'form_keywords': ['alaknanda']
    }
]

print("Creating projects...")
for project_data in projects_data:
    project, created = Project.objects.get_or_create(
        code=project_data['code'],
        defaults=project_data
    )
    if created:
        print(f"Created: {project.name}")
    else:
        print(f"Exists: {project.name}")

print(f"\nTotal projects: {Project.objects.count()}")

# Show lead counts
print("\nProject lead counts:")
for project in Project.objects.all():
    count = project.lead_count
    print(f"{project.name}: {count} leads")