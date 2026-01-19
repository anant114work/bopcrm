import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.form_mapping_models import FormSourceMapping
from leads.models import Lead
from leads.project_models import Project

# Get SPJ project
spj = Project.objects.get(name='SPJ')

# Get all unique SPJ form names
spj_forms = Lead.objects.filter(
    form_name__icontains='spj'
).values_list('form_name', flat=True).distinct()

print(f"Found {len(spj_forms)} unique SPJ forms:")

added = 0
for form_name in spj_forms:
    # Check if mapping exists
    exists = FormSourceMapping.objects.filter(
        project=spj,
        form_name=form_name
    ).exists()
    
    if not exists:
        FormSourceMapping.objects.create(
            project=spj,
            form_name=form_name,
            is_active=True
        )
        print(f"  ✓ Added: {form_name}")
        added += 1
    else:
        print(f"  - Exists: {form_name}")

print(f"\n✅ Added {added} new form mappings")
print(f"Total SPJ mappings now: {FormSourceMapping.objects.filter(project=spj).count()}")
