import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-key-for-development-only')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Production-ready ALLOWED_HOSTS
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')
if '*' not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.extend(['localhost', '127.0.0.1', '.hostinger.com', '.hostingersite.com'])

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'leads.apps.LeadsConfig',
    'tata_integration',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'leads.middleware.LeadViewTrackingMiddleware',
]

ROOT_URLCONF = 'crm.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Database configuration
if os.getenv('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.parse(os.getenv('DATABASE_URL'))
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Static files (Production-ready)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')] if os.path.exists(os.path.join(BASE_DIR, 'static')) else []

# Use WhiteNoise for static files in production
if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
else:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Media files (Production-ready)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security settings for production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'
else:
    SECURE_SSL_REDIRECT = False
    SECURE_PROXY_SSL_HEADER = None
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

# API Configuration
META_ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN')
META_PAGE_ID = os.getenv('META_PAGE_ID')
WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN')
WHATSAPP_PHONE_ID = os.getenv('WHATSAPP_PHONE_ID')

# Zoho Configuration
ZOHO_CLIENT_ID = os.getenv('ZOHO_CLIENT_ID')
ZOHO_CLIENT_SECRET = os.getenv('ZOHO_CLIENT_SECRET')
ZOHO_REDIRECT_URI = os.getenv('ZOHO_REDIRECT_URI')

# Tata API Configuration
TATA_API_TOKEN = os.getenv('TATA_API_TOKEN', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIzMTE2MDAiLCJjciI6dHJ1ZSwiaXNzIjoiaHR0cHM6Ly9jbG91ZHBob25lLnRhdGF0ZWxlc2VydmljZXMuY29tL3Rva2VuL2dlbmVyYXRlIiwiaWF0IjoxNzUxOTc4Nzg5LCJleHAiOjIwNTE5Nzg3ODksIm5iZiI6MTc1MTk3ODc4OSwianRpIjoiY3Bvc1Z4TW9oOHpWZ2d3MCJ9.G8qzkWIN0i3Dj5zxnct5JW-PpBlk6DUjXlSq6sWvc9I')

# AI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your-openai-api-key-here')
HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY', 'your-hf-token-here')

# Call Karo AI Configuration
CALLKARO_API_KEY = os.getenv('CALLKARO_API_KEY')
CALLKARO_DEFAULT_AGENT_ID = os.getenv('CALLKARO_DEFAULT_AGENT_ID')

# Auto Sync Configuration
AUTO_SYNC_ENABLED = os.getenv('AUTO_SYNC_ENABLED', 'True').lower() == 'true'
SYNC_INTERVAL_MINUTES = int(os.getenv('SYNC_INTERVAL_MINUTES', '30'))

# Redis Configuration
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Cache Configuration with fallback
try:
    import redis
    # Test Redis connection
    redis.Redis.from_url(REDIS_URL).ping()
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }
    # Use Redis for sessions
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'default'
except:
    # Fallback to database cache and sessions
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
            'LOCATION': 'cache_table',
        }
    }
    # Use database for sessions
    SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Celery Configuration (optional)
try:
    import redis
    redis.Redis.from_url(REDIS_URL).ping()
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_TIMEZONE = TIME_ZONE
    CELERY_BEAT_SCHEDULE = {
        'process-scheduled-messages': {
            'task': 'leads.tasks.process_scheduled_messages',
            'schedule': 60.0,  # Every minute
        },
        'sync-leads': {
            'task': 'leads.tasks.sync_all_leads',
            'schedule': 300.0,  # Every 5 minutes
        },
    }
except:
    # Redis not available, disable Celery
    pass

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'