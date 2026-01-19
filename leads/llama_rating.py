import requests
import json
from django.conf import settings
from .models import Lead, LeadNote

class LlamaLeadRater:
    def __init__(self):
        # Using Hugging Face Inference API for Llama 3.1-8B-Instruct
        self.api_url = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.1-8B-Instruct"
        self.headers = {"Authorization": f"Bearer {getattr(settings, 'HUGGINGFACE_API_KEY', 'your-hf-token')}"}
    
    def rate_lead(self, lead):
        """Rate a lead using Llama 3.1-8B-Instruct"""
        try:
            # Prepare lead data for analysis
            lead_data = self._prepare_lead_data(lead)
            
            # Create prompt for Llama
            prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are a lead scoring expert. Rate leads from 1-10 based on conversion potential. Respond with only a JSON object.

<|eot_id|><|start_header_id|>user<|end_header_id|>
Rate this lead:
Name: {lead_data['name']}
Phone: {lead_data['phone']}
Email: {lead_data['email']}
City: {lead_data['city']}
Budget: {lead_data['budget']}
Configuration: {lead_data['configuration']}
Stage: {lead_data['stage']}
Recent Notes: {lead_data['notes']}

Return JSON: {{"score": number, "priority": "high/medium/low", "reason": "brief explanation"}}
<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""

            # Call Llama API
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": 150,
                        "temperature": 0.3,
                        "return_full_text": False
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get('generated_text', '')
                    return self._parse_rating(generated_text)
            
            # Fallback rating
            return self._fallback_rating(lead)
            
        except Exception as e:
            print(f"Llama rating error: {e}")
            return self._fallback_rating(lead)
    
    def _prepare_lead_data(self, lead):
        """Prepare lead data for analysis"""
        recent_notes = LeadNote.objects.filter(lead=lead).order_by('-created_at')[:3]
        notes_text = " | ".join([note.note for note in recent_notes]) if recent_notes else "No notes"
        
        return {
            'name': lead.full_name or 'Unknown',
            'phone': lead.phone_number or 'No phone',
            'email': lead.email or 'No email',
            'city': lead.city or 'Unknown',
            'budget': lead.budget or 'Not specified',
            'configuration': lead.configuration or 'Not specified',
            'stage': lead.get_stage_display() or 'New',
            'notes': notes_text[:200]  # Limit notes length
        }
    
    def _parse_rating(self, text):
        """Parse Llama response to extract rating"""
        try:
            # Find JSON in response
            start = text.find('{')
            end = text.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = text[start:end]
                rating = json.loads(json_str)
                
                # Validate and normalize
                score = max(1, min(10, int(rating.get('score', 5))))
                priority = rating.get('priority', 'medium').lower()
                if priority not in ['high', 'medium', 'low']:
                    priority = 'medium'
                
                return {
                    'score': score,
                    'priority': priority,
                    'reason': rating.get('reason', 'AI analysis completed')[:100]
                }
        except:
            pass
        
        return self._fallback_rating(None)
    
    def _fallback_rating(self, lead):
        """Fallback rating when API fails"""
        if lead:
            score = 5
            if lead.budget and any(x in str(lead.budget).lower() for x in ['cr', 'crore', 'lakh']):
                score += 2
            if lead.phone_number:
                score += 1
            if lead.email:
                score += 1
            if lead.stage in ['interested', 'hot']:
                score += 1
            
            score = max(1, min(10, score))
            priority = 'high' if score >= 8 else 'medium' if score >= 6 else 'low'
        else:
            score = 5
            priority = 'medium'
        
        return {
            'score': score,
            'priority': priority,
            'reason': 'Automated scoring based on lead data'
        }