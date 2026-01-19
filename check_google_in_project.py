import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import Lead
from leads.project_models import Project

spj = Project.objects.filter(name__icontains='spj').first()
if spj:
    print(f'Project: {spj.name} (ID: {spj.id})')
    google_in_project = spj.get_leads().filter(source='Google Sheets', phone_number__isnull=False).exclude(phone_number='')
    print(f'Google leads in project: {google_in_project.count()}')
    print('\nSample leads:')
    for l in google_in_project[:5]:
        print(f'  {l.full_name}: {l.phone_number}')
else:
    print('No SPJ project found')
    print('\nAll projects:')
    for p in Project.objects.all():
        print(f'  - {p.name}')
