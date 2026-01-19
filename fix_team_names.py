import re
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import TeamMember

for member in TeamMember.objects.all():
    original_name = member.name
    cleaned_name = re.sub(r'^\d+\.\s*', '', member.name)
    
    if original_name != cleaned_name:
        member.name = cleaned_name
        member.save()
        print(f"Updated: '{original_name}' -> '{cleaned_name}'")

print("Done!")
