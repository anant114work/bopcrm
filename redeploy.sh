#!/bin/bash

echo "=========================================="
echo "CRM Server Reset & Redeploy Script"
echo "=========================================="

# Stop all running processes
echo "Stopping Django server..."
pkill -f "python manage.py runserver" || true
pkill -f "gunicorn" || true

# Backup database (optional)
echo "Creating database backup..."
python manage.py dumpdata > backup_$(date +%Y%m%d_%H%M%S).json

# Pull latest code from GitHub
echo "Pulling latest code from GitHub..."
git fetch origin
git reset --hard origin/main
git pull origin main

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate || source venv/Scripts/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run migrations
echo "Running database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Update SPJ agent configuration
echo "Updating SPJ Vedatam agent..."
python manage.py shell << EOF
from leads.ai_calling_models import AICallingAgent
agent, created = AICallingAgent.objects.get_or_create(
    name='SPJ Vedatam',
    defaults={
        'agent_id': '69609b8f9cd0a3ca06a3792b',
        'phone_number': '917943595082',
        'is_active': True
    }
)
if not created:
    agent.agent_id = '69609b8f9cd0a3ca06a3792b'
    agent.phone_number = '917943595082'
    agent.is_active = True
    agent.save()
print(f"Agent configured: {agent.name} - {agent.agent_id}")
EOF

# Restart server
echo "Starting Django server..."
nohup python manage.py runserver 0.0.0.0:8000 > server.log 2>&1 &

echo "=========================================="
echo "Deployment Complete!"
echo "Server running on port 8000"
echo "Check logs: tail -f server.log"
echo "=========================================="
