from django.core.management.base import BaseCommand
from leads.callkaro_models import CallKaroAgent, CallKaroConfig

def create_default_agents():
    """Create default CallKaro agents if none exist"""
    
    # Create default config if not exists
    if not CallKaroConfig.objects.exists():
        CallKaroConfig.objects.create(
            api_key="your_callkaro_api_key_here",
            default_agent_id="default_agent",
            is_active=True
        )
        print("✅ Created default CallKaro config")
    
    # Create default agents if none exist
    if not CallKaroAgent.objects.exists():
        agents_data = [
            {
                'agent_id': 'default_agent',
                'name': 'Default Real Estate Agent',
                'description': 'General purpose real estate calling agent'
            },
            {
                'agent_id': 'sales_agent', 
                'name': 'Sales Executive Agent',
                'description': 'Specialized in sales conversations and lead qualification'
            },
            {
                'agent_id': 'property_agent',
                'name': 'Property Consultant Agent', 
                'description': 'Expert in property details and investment guidance'
            }
        ]
        
        for agent_data in agents_data:
            CallKaroAgent.objects.create(**agent_data)
            print(f"✅ Created agent: {agent_data['name']}")
        
        print("✅ All default agents created successfully!")
    else:
        print("ℹ️ CallKaro agents already exist")

if __name__ == "__main__":
    create_default_agents()