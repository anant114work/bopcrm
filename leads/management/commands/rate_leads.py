from django.core.management.base import BaseCommand
from leads.models import Lead, LeadRating
from leads.llama_rating import LlamaLeadRater

class Command(BaseCommand):
    help = 'Rate all leads using Llama 3.1-8B-Instruct'
    
    def handle(self, *args, **options):
        rater = LlamaLeadRater()
        leads = Lead.objects.filter(ai_rating__isnull=True)[:50]  # Rate 50 at a time
        
        self.stdout.write(f'Rating {leads.count()} leads...')
        
        for lead in leads:
            try:
                rating_data = rater.rate_lead(lead)
                LeadRating.objects.create(lead=lead, **rating_data)
                self.stdout.write(f'Rated: {lead.full_name} - Score: {rating_data["score"]}')
            except Exception as e:
                self.stdout.write(f'Error rating {lead.full_name}: {e}')
        
        self.stdout.write(self.style.SUCCESS('Lead rating completed!'))