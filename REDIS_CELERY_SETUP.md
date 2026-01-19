# Redis & Celery Setup Guide

## What is Redis & Celery?

### Redis (Remote Dictionary Server)
- **In-memory database** - Stores data in RAM for super fast access
- **Key-value store** - Simple data structure like Python dictionary
- **Caching system** - Avoids repeated database queries
- **Message broker** - Handles task queues between processes

### Celery (Distributed Task Queue)
- **Async processing** - Runs tasks in background without blocking web requests
- **Retry mechanism** - Automatically retries failed tasks
- **Scheduling** - Run tasks at specific times or intervals
- **Scalability** - Add more workers to handle more tasks

## Where They Help in CRM:

### 1. WhatsApp Messaging
**Before:** User waits 10-30 seconds for each WhatsApp to send
**After:** User gets instant response, messages sent in background

### 2. Lead Sync
**Before:** Syncing 1000 leads takes 5 minutes, user waits
**After:** Sync runs in background, user continues working

### 3. Dashboard Loading
**Before:** Dashboard queries database every time (slow)
**After:** Dashboard loads from cache (instant)

### 4. Scheduled Tasks
**Before:** Manual cron jobs, unreliable
**After:** Automatic scheduling with retry logic

## Installation Steps:

### 1. Install Redis Server
```bash
# Windows (using Chocolatey)
choco install redis-64

# Or download from: https://github.com/microsoftarchive/redis/releases
```

### 2. Install Python Dependencies
```bash
pip install -r requirements_redis.txt
```

### 3. Start Redis Server
```bash
# Windows
redis-server

# Should show: "Ready to accept connections"
```

### 4. Start Celery Worker
```bash
# In project directory
python manage.py start_celery --worker-only
```

### 5. Start Celery Beat (Scheduler)
```bash
# In another terminal
celery -A crm beat --loglevel=info
```

## How It Works:

### Before (Synchronous):
```python
def send_whatsapp(request):
    for lead_id in lead_ids:
        # User waits here for each API call
        response = requests.post(whatsapp_api, data)
    return "Done"  # After 30 seconds
```

### After (Asynchronous):
```python
def send_whatsapp(request):
    for lead_id in lead_ids:
        # Queue task, return immediately
        send_whatsapp_async.delay(lead_id)
    return "Queued"  # Instant response
```

## Caching Example:

### Before:
```python
def dashboard(request):
    # Runs every time (slow)
    total_leads = Lead.objects.count()  # 500ms
    conversions = Lead.objects.filter(stage='converted').count()  # 300ms
    return render(request, 'dashboard.html', data)  # Total: 800ms
```

### After:
```python
def dashboard(request):
    # Check cache first
    data = cache.get('dashboard_data')
    if not data:
        # Only run if not cached
        data = calculate_dashboard_data()
        cache.set('dashboard_data', data, 300)  # Cache for 5 minutes
    return render(request, 'dashboard.html', data)  # Total: 50ms
```

## Task Examples:

### 1. WhatsApp Task
```python
@shared_task(bind=True, max_retries=3)
def send_whatsapp_async(self, lead_id, template):
    try:
        # Send WhatsApp message
        response = requests.post(api_url, data)
        return {'success': True}
    except Exception as e:
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
```

### 2. Scheduled Task
```python
@shared_task
def sync_leads_daily():
    # Runs automatically every day
    sync_meta_leads()
    sync_google_leads()
    return "Sync completed"
```

## Monitoring:

### Check Redis Status:
```bash
redis-cli ping
# Should return: PONG
```

### Check Celery Tasks:
```bash
celery -A crm inspect active
# Shows running tasks
```

### View Task Results:
```python
from leads.tasks import send_whatsapp_async
result = send_whatsapp_async.delay(lead_id, 'template')
print(result.status)  # PENDING, SUCCESS, FAILURE
```

## Benefits:

1. **User Experience**: Instant responses, no waiting
2. **Reliability**: Failed tasks retry automatically
3. **Performance**: Cached data loads instantly
4. **Scalability**: Add more workers as needed
5. **Monitoring**: Track task success/failure rates

## Production Deployment:

### 1. Redis Configuration
```bash
# /etc/redis/redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
```

### 2. Celery as Service
```bash
# systemd service file
[Unit]
Description=Celery Worker
After=network.target

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/path/to/crm
ExecStart=/path/to/venv/bin/celery -A crm worker --detach
Restart=always

[Install]
WantedBy=multi-user.target
```

This setup transforms your CRM from a slow, blocking system to a fast, responsive application that can handle high loads efficiently.