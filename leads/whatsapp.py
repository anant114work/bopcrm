import requests
import json

AISENSY_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY4ZGVhNzVlYTM3MDcyNTJiYzJhZWY1NyIsIm5hbWUiOiJBQkMgRGlnaXRhbCBJbmMiLCJhcHBOYW1lIjoiQWlTZW5zeSIsImNsaWVudElkIjoiNjhkZWE3NWVhMzcwNzI1MmJjMmFlZjUyIiwiYWN0aXZlUGxhbiI6IkZSRUVfRk9SRVZFUiIsImlhdCI6MTc1OTQyMjMwMn0.GzXAy0qINll2QxsM9Q73B8SHBPeHMXiXZ1ypm8ScNbE"
AISENSY_URL = "https://backend.aisensy.com/campaign/t1/api/v2"

def send_whatsapp_message(lead, template_name="crm3"):
    """Send WhatsApp message to a lead using AiSensy API"""
    
    if not lead.phone_number:
        return False, "No phone number available"
    
    # Format phone number for India
    phone = lead.phone_number.strip().replace(' ', '').replace('-', '')
    if not phone.startswith('+'):
        if phone.startswith('91'):
            phone = '+' + phone
        elif phone.startswith('0'):
            phone = '+91' + phone[1:]
        else:
            phone = '+91' + phone
    
    # Get source mapping
    from .models import SourceMapping
    source_mapping = SourceMapping.objects.filter(source_name=lead.form_name, is_active=True).first()
    
    if source_mapping:
        project_name = source_mapping.project_name
        location = source_mapping.location
    else:
        project_name = lead.form_name or "our project"
        location = lead.city or "your area"
    
    # Template-specific parameters
    if template_name == "followupcampaign":
        template_params = [
            lead.full_name or "user",
            project_name,
            location
        ]
        source = "new-landing-page form"
    else:
        template_params = [lead.full_name or "Customer"]
        source = "CRM Lead"
    
    payload = {
        "apiKey": AISENSY_API_KEY,
        "campaignName": template_name,
        "destination": phone.replace('+', ''),
        "userName": "ABC Digital Inc",
        "templateParams": template_params,
        "source": source,
        "media": {},
        "buttons": [],
        "carouselCards": [],
        "location": {},
        "attributes": {},
        "paramsFallbackValue": {
            "FirstName": lead.full_name or "user"
        }
    }
    
    try:
        response = requests.post(AISENSY_URL, json=payload, timeout=10)
        if response.status_code == 200:
            return True, "Message sent successfully"
        else:
            return False, f"API Error: {response.status_code}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def get_available_templates():
    """Get list of available WhatsApp templates"""
    return [
        {"name": "crm3", "display": "CRM Template v3"},
        {"name": "followupcampaign", "display": "Follow-up Campaign"}
    ]