#!/bin/bash

# Server Deployment Script - Login & User Management Update

echo "=========================================="
echo "Deploying Login & User Management Update"
echo "=========================================="

# Navigate to project directory
cd /var/www/drip || cd ~/drip || { echo "Project directory not found"; exit 1; }

# Pull latest changes
echo "Pulling latest code..."
git pull origin main

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install any new dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create admin user
echo "Creating/updating admin user..."
python create_admin_login.py

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Restart application
echo "Restarting application..."
sudo systemctl restart crm || sudo systemctl restart gunicorn || { echo "Restart service manually"; }

echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "Admin Login Credentials:"
echo "URL: /team/login/"
echo "Username: admin"
echo "Password: 8882443789"
echo ""
echo "User Management: /user-management/"
