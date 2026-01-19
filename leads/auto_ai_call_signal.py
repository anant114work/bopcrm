from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Lead
from .auto_ai_call_service import AutoAICallService

@receiver(post_save, sender=Lead)
def auto_call_new_lead(sender, instance, created, **kwargs):
    """Automatically trigger AI call when a new lead is created"""
    if created:
        try:
            service = AutoAICallService()
            result = service.process_new_lead(instance)
            
            if result.get('success'):
                print(f"✅ Auto AI call triggered for lead: {instance.full_name}")
            elif result.get('skipped'):
                print(f"⏭️ Auto AI call skipped for lead: {instance.full_name} - {result.get('reason')}")
            else:
                print(f"❌ Auto AI call failed for lead: {instance.full_name} - {result.get('error')}")
        except Exception as e:
            print(f"💥 Error in auto AI call signal: {str(e)}")
