#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append('d:\\AI-proto\\CRM\\drip')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.acefone_models import AcefoneConfig

def setup_acefone_config():
    print("Setting up Acefone configuration...")
    
    # Check if config exists
    config = AcefoneConfig.objects.filter(is_active=True).first()
    
    if config:
        print(f"Acefone config exists: {config.base_url}")
    else:
        # Create default config
        config = AcefoneConfig.objects.create(
            token='your_acefone_token_here',
            base_url='https://api.acefone.in/v1',
            is_active=True
        )
        print(f"Created Acefone config: {config.base_url}")
    
    print("Acefone setup complete!")

if __name__ == '__main__':
    setup_acefone_config()