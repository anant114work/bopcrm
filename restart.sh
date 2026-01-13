#!/bin/bash

# Quick restart script for Django CRM

echo "🔄 Restarting Django CRM..."

# Activate virtual environment
source venv/bin/activate

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

# Run migrations
echo "🔄 Running migrations..."
python manage.py migrate

# Restart services
echo "🚀 Restarting services..."
sudo systemctl restart crm
sudo systemctl restart nginx

# Check status
echo "✅ Checking service status..."
sudo systemctl status crm --no-pager

echo ""
echo "✅ Restart completed!"
echo "🔗 Check your application at your domain"
