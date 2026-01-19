from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Lead, LeadNote, LeadRating
from .llama_rating import LlamaLeadRater

@receiver(post_save, sender=Lead)
def update_lead_rating_on_stage_change(sender, instance, created, **kwargs):
    """Update lead rating when stage changes and trigger auto call for NEW leads only"""
    if created:
        # For new leads: sync to BOP CRM AND trigger auto-call
        from datetime import date
        
        # Sync new lead to BOP CRM
        try:
            from .bop_sync import sync_lead_to_bop_crm
            success, message = sync_lead_to_bop_crm(instance)
            if success:
                print(f"BOP sync successful for NEW lead {instance.full_name}: {message}")
            else:
                print(f"BOP sync failed for NEW lead {instance.full_name}: {message}")
        except Exception as e:
            print(f"BOP sync error for NEW lead {instance.full_name}: {e}")
        
        # Trigger auto-call only for leads created TODAY
        if instance.created_time.date() == date.today():
            try:
                from .auto_call_service import trigger_auto_call_for_lead
                success, message = trigger_auto_call_for_lead(instance)
                if success:
                    print(f"Auto call triggered for NEW lead {instance.full_name}: {message}")
                else:
                    print(f"Auto call failed for NEW lead {instance.full_name}: {message}")
            except Exception as e:
                print(f"Auto call error for NEW lead {instance.id}: {e}")
        else:
            print(f"Skipping auto-call for old lead {instance.full_name} (created: {instance.created_time.date()})")
        
        # Trigger auto WhatsApp campaigns
        try:
            from .auto_whatsapp_service import trigger_auto_campaigns_for_lead
            sent_count = trigger_auto_campaigns_for_lead(instance)
            if sent_count > 0:
                print(f"Auto WhatsApp sent for NEW lead {instance.full_name}: {sent_count} messages")
        except Exception as e:
            print(f"Auto WhatsApp error for NEW lead {instance.full_name}: {e}")
            
        # Always sync new leads to BOP CRM regardless of date
        try:
            from .bop_sync import sync_lead_to_bop_crm
            success, message = sync_lead_to_bop_crm(instance)
            if success:
                print(f"BOP sync successful for NEW lead {instance.full_name}: {message}")
            else:
                print(f"BOP sync failed for NEW lead {instance.full_name}: {message}")
        except Exception as e:
            print(f"BOP sync error for NEW lead {instance.full_name}: {e}")
    else:
        # For lead updates, sync to BOP CRM and update rating
        try:
            # Sync to BOP CRM when lead is updated
            from .bop_sync import sync_lead_to_bop_crm
            success, message = sync_lead_to_bop_crm(instance)
            if success:
                print(f"BOP sync successful for {instance.full_name}: {message}")
            else:
                print(f"BOP sync failed for {instance.full_name}: {message}")
        except Exception as e:
            print(f"BOP sync error for {instance.full_name}: {e}")
            
        try:
            # Always re-rate on any lead update (stage, notes, etc.)
            rater = LlamaLeadRater()
            rating_data = rater.rate_lead(instance)
            
            rating, rating_created = LeadRating.objects.get_or_create(
                lead=instance,
                defaults=rating_data
            )
            if not rating_created:
                rating.score = rating_data['score']
                rating.priority = rating_data['priority']
                rating.reason = rating_data['reason']
                rating.save()
                print(f"Updated rating for {instance.full_name}: Score {rating.score}, Priority {rating.priority}")
        except Exception as e:
            print(f"Error updating rating for {instance.full_name}: {e}")

@receiver(post_save, sender=LeadNote)
def update_lead_rating_on_note_add(sender, instance, created, **kwargs):
    """Update lead rating when new note is added"""
    if created:
        try:
            # Re-rate the lead using Llama
            rater = LlamaLeadRater()
            rating_data = rater.rate_lead(instance.lead)
            
            rating, rating_created = LeadRating.objects.get_or_create(
                lead=instance.lead,
                defaults=rating_data
            )
            if not rating_created:
                rating.score = rating_data['score']
                rating.priority = rating_data['priority']
                rating.reason = rating_data['reason']
                rating.save()
                print(f"Updated rating after note for {instance.lead.full_name}: Score {rating.score}")
        except Exception as e:
            print(f"Error updating rating after note: {e}")