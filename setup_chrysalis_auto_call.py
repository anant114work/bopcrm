#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append('d:\\AI-proto\\CRM\\drip')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import TeamMember, AutoCallConfig

def setup_chrysalis_auto_call():
    print("Setting up Chrysalis Auto Call...")
    
    # Find or create Anat
    anat, created = TeamMember.objects.get_or_create(
        name__icontains='anat',
        defaults={
            'name': 'Anat',
            'email': 'anat@crm.com',
            'phone': '9999999999',
            'role': 'Sales Executive - T5',
            'is_active': True
        }
    )
    
    if created:
        print(f"Created agent: {anat.name}")
    else:
        print(f"Found existing agent: {anat.name}")
    
    # Create Chrysalis auto call configuration
    config, created = AutoCallConfig.objects.get_or_create(
        project_name='Chrysalis',
        defaults={
            'mapped_agent': anat,
            'is_active': True
        }
    )
    
    if created:
        print(f"Created auto call config: Chrysalis -> {anat.name}")
    else:
        print(f"Auto call config already exists: Chrysalis -> {config.mapped_agent.name}")
    
    print("\n✅ Chrysalis Auto Call Setup Complete!")
    print(f"📞 New Chrysalis leads will automatically trigger calls to {anat.name}")
    print("🔧 Configure more projects at: /auto-call-config/")

if __name__ == '__main__':
    setup_chrysalis_auto_call()