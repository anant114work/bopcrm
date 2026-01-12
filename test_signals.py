import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import Lead, LeadRating

# Test signal by updating a lead stage
lead = Lead.objects.first()
if lead:
    print(f"Testing signal for lead: {lead.full_name}")
    print(f"Current stage: {lead.stage}")
    
    # Check current rating
    try:
        rating = LeadRating.objects.get(lead=lead)
        print(f"Current rating: Score {rating.score}, Priority {rating.priority}")
    except LeadRating.DoesNotExist:
        print("No rating exists yet")
    
    # Update stage to trigger signal
    old_stage = lead.stage
    new_stage = 'interested' if old_stage != 'interested' else 'hot'
    lead.stage = new_stage
    lead.save()
    
    print(f"Updated stage to: {new_stage}")
    
    # Check if rating was updated
    try:
        rating = LeadRating.objects.get(lead=lead)
        print(f"New rating: Score {rating.score}, Priority {rating.priority}")
        print(f"Reason: {rating.reason}")
    except LeadRating.DoesNotExist:
        print("Still no rating - signal may not be working")
else:
    print("No leads found to test")