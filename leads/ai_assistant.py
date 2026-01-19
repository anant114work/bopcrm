"""
AI Assistant for Lead Handling and Analytics using Janus-Pro
"""
import requests
import json
import re
from typing import Dict, List, Optional

from .ai_config import HUGGINGFACE_API_TOKEN, JANUS_PRO_MODEL, API_BASE_URL, REQUEST_TIMEOUT, DEFAULT_TEMPERATURE, MAX_TOKENS

class LeadAIAssistant:
    def __init__(self):
        self.api_url = f"{API_BASE_URL}{JANUS_PRO_MODEL}"
        self.headers = {"Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"}
        self.timeout = REQUEST_TIMEOUT
        self.fallback_enabled = True
    
    def analyze_lead_quality(self, lead_data: Dict) -> Dict:
        """Analyze lead quality and provide scoring"""
        prompt = f"""
        Analyze this lead and provide a quality score (1-10) and recommendations:
        
        Name: {lead_data.get('full_name', 'Unknown')}
        Phone: {lead_data.get('phone_number', 'Not provided')}
        Email: {lead_data.get('email', 'Not provided')}
        City: {lead_data.get('city', 'Not provided')}
        Budget: {lead_data.get('budget', 'Not specified')}
        Configuration: {lead_data.get('configuration', 'Not specified')}
        Form: {lead_data.get('form_name', 'Unknown source')}
        
        Provide response in JSON format:
        {{
            "quality_score": 8,
            "priority": "high",
            "recommendations": ["Contact within 2 hours", "Focus on budget discussion"],
            "lead_type": "hot_prospect",
            "next_action": "immediate_call"
        }}
        """
        
        try:
            # Use Janus-Pro for analysis
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 200,
                    "temperature": 0.3,
                    "return_full_text": False
                }
            }
            
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get('generated_text', '')
                    # Extract JSON from response
                    json_match = re.search(r'\{.*\}', generated_text, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group())
            
            # Fallback scoring
            return self._fallback_lead_scoring(lead_data)
            
        except Exception as e:
            print(f"AI analysis error: {e}")
            return self._fallback_lead_scoring(lead_data)
    
    def generate_follow_up_message(self, lead_data: Dict, context: str = "") -> str:
        """Generate personalized follow-up message"""
        prompt = f"""
        Create a personalized WhatsApp follow-up message for this lead:
        
        Lead Details:
        - Name: {lead_data.get('full_name', 'Customer')}
        - Budget: {lead_data.get('budget', 'Not specified')}
        - Configuration: {lead_data.get('configuration', 'Not specified')}
        - City: {lead_data.get('city', 'Not specified')}
        
        Context: {context}
        
        Create a professional, friendly message under 160 characters that:
        1. Addresses them by name
        2. References their specific requirements
        3. Includes a clear call-to-action
        
        Message:
        """
        
        try:
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 100,
                    "temperature": 0.7,
                    "return_full_text": False
                }
            }
            
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    message = result[0].get('generated_text', '').strip()
                    # Clean and format response
                    message = message.replace('"', '').replace('Message:', '').strip()
                    return message[:160]  # Ensure under 160 chars
            
            # Fallback message
            return f"Hi {lead_data.get('full_name', 'there')}! Thank you for your interest. Can we schedule a quick call to discuss your requirements? Reply YES to confirm."
            
        except Exception as e:
            print(f"Message generation error: {e}")
            return f"Hi {lead_data.get('full_name', 'there')}! Thank you for your interest. Can we schedule a quick call to discuss your requirements? Reply YES to confirm."
    
    def analyze_call_notes(self, notes: str) -> Dict:
        """Analyze call notes and extract insights"""
        prompt = f"""
        Analyze these call notes and extract key insights:
        
        Notes: "{notes}"
        
        Provide analysis in JSON format:
        {{
            "sentiment": "positive/neutral/negative",
            "interest_level": "high/medium/low",
            "key_points": ["point1", "point2"],
            "next_action": "recommended action",
            "tags": ["tag1", "tag2"],
            "follow_up_timing": "immediate/1day/1week/no_follow_up"
        }}
        """
        
        try:
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 150,
                    "temperature": 0.3,
                    "return_full_text": False
                }
            }
            
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get('generated_text', '')
                    json_match = re.search(r'\{.*\}', generated_text, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group())
            
            return self._fallback_note_analysis(notes)
            
        except Exception as e:
            print(f"Note analysis error: {e}")
            return self._fallback_note_analysis(notes)
    
    def generate_lead_summary(self, leads_data: List[Dict]) -> str:
        """Generate analytics summary for multiple leads"""
        total_leads = len(leads_data)
        with_phone = sum(1 for lead in leads_data if lead.get('phone_number'))
        with_email = sum(1 for lead in leads_data if lead.get('email'))
        
        prompt = f"""
        Generate a brief analytics summary for {total_leads} leads:
        - {with_phone} have phone numbers
        - {with_email} have email addresses
        - Sources: {', '.join(set(lead.get('form_name', 'Unknown') for lead in leads_data[:5]))}
        
        Provide insights and recommendations in 2-3 sentences.
        """
        
        try:
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 150,
                    "temperature": 0.5,
                    "return_full_text": False
                }
            }
            
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get('generated_text', '').strip()
            
            return f"Analyzed {total_leads} leads. {with_phone} leads have contact numbers for immediate follow-up. Focus on high-budget prospects first."
            
        except Exception as e:
            print(f"Summary generation error: {e}")
            return f"Analyzed {total_leads} leads. {with_phone} leads have contact numbers for immediate follow-up. Focus on high-budget prospects first."
    
    def suggest_optimal_call_time(self, lead_data: Dict) -> str:
        """Suggest best time to call based on lead profile"""
        prompt = f"""
        Based on this lead profile, suggest the best time to call:
        
        City: {lead_data.get('city', 'Unknown')}
        Budget: {lead_data.get('budget', 'Unknown')}
        Configuration: {lead_data.get('configuration', 'Unknown')}
        
        Consider time zones and professional calling hours. Respond with just the time suggestion.
        """
        
        try:
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 50,
                    "temperature": 0.3,
                    "return_full_text": False
                }
            }
            
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get('generated_text', '').strip()
            
            return "10:00 AM - 12:00 PM or 2:00 PM - 5:00 PM"
            
        except Exception as e:
            return "10:00 AM - 12:00 PM or 2:00 PM - 5:00 PM"
    
    def _fallback_lead_scoring(self, lead_data: Dict) -> Dict:
        """Fallback lead scoring when AI is unavailable"""
        score = 5  # Base score
        
        # Scoring logic
        if lead_data.get('phone_number'):
            score += 2
        if lead_data.get('email'):
            score += 1
        if lead_data.get('budget') and lead_data['budget'] not in ['', 'na', 'N/A']:
            score += 2
        
        priority = "high" if score >= 8 else "medium" if score >= 6 else "low"
        
        return {
            "quality_score": min(score, 10),
            "priority": priority,
            "recommendations": ["Contact within 24 hours", "Verify requirements"],
            "lead_type": "prospect",
            "next_action": "call"
        }
    
    def _fallback_note_analysis(self, notes: str) -> Dict:
        """Fallback note analysis"""
        notes_lower = notes.lower()
        
        # Simple keyword analysis
        positive_words = ['interested', 'yes', 'good', 'like', 'want', 'need']
        negative_words = ['not interested', 'no', 'busy', 'later', 'expensive']
        
        positive_count = sum(1 for word in positive_words if word in notes_lower)
        negative_count = sum(1 for word in negative_words if word in notes_lower)
        
        if positive_count > negative_count:
            sentiment = "positive"
            interest_level = "high"
        elif negative_count > positive_count:
            sentiment = "negative"
            interest_level = "low"
        else:
            sentiment = "neutral"
            interest_level = "medium"
        
        return {
            "sentiment": sentiment,
            "interest_level": interest_level,
            "key_points": [notes[:50] + "..."],
            "next_action": "follow_up",
            "tags": ["analyzed"],
            "follow_up_timing": "1day"
        }