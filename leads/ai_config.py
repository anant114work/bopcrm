"""
AI Configuration for Janus-Pro Integration
"""

# Hugging Face API Configuration
HUGGINGFACE_API_TOKEN = "hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # Replace with your actual token
JANUS_PRO_MODEL = "deepseek-ai/Janus-Pro-7B"
API_BASE_URL = "https://api-inference.huggingface.co/models/"

# Fallback responses when AI is unavailable
FALLBACK_ENABLED = True

# API timeout settings
REQUEST_TIMEOUT = 10  # seconds

# Model parameters
DEFAULT_TEMPERATURE = 0.3
MAX_TOKENS = 200