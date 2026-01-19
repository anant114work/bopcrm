import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.form_mapping_models import FormSourceMapping
from leads.models import Lead
from leads.project_models import Project

# Check SPJ mappings
spj = Project.objects.get(name='SPJ')
mappings = FormSourceMapping.objects.filter(project=spj, is_active=True)

print(f"SPJ Form Mappings: {mappings.count()}")
for m in mappings:
    print(f"  - {m.form_name}")

# Check recent SPJ leads
recent_leads = Lead.objects.filter(form_name__icontains='spj').order_by('-created_time')[:5]
print(f"\nRecent SPJ Leads (last 5):")
for lead in recent_leads:
    print(f"  - {lead.full_name} | {lead.form_name} | {lead.created_time}")

# Check if they match
print(f"\nLeads returned by project.get_leads(): {spj.get_leads().count()}")
