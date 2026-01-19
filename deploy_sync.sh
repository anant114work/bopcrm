#!/bin/bash
# Deploy updated CRM to VPS and sync all leads

echo "=========================================="
echo "DEPLOYING CRM UPDATES TO VPS"
echo "=========================================="

# Configuration
VPS_IP="your-vps-ip"  # CHANGE THIS
VPS_USER="root"
VPS_PATH="/var/www/bopcrm"

echo "Uploading updated files..."

# Upload views.py
scp leads/views.py ${VPS_USER}@${VPS_IP}:${VPS_PATH}/leads/

# Upload management command
scp -r leads/management ${VPS_USER}@${VPS_IP}:${VPS_PATH}/leads/

echo "Connecting to VPS and running sync..."

ssh ${VPS_USER}@${VPS_IP} << 'ENDSSH'
cd /var/www/bopcrm
source venv/bin/activate

echo "Running migrations..."
python manage.py migrate

echo "Syncing ALL historical Meta leads..."
python manage.py sync_meta_leads

echo "Restarting services..."
sudo systemctl restart crm nginx

echo "Checking lead count..."
python manage.py shell -c "from leads.models import Lead; print(f'Total Leads: {Lead.objects.count()}')"

echo "=========================================="
echo "DEPLOYMENT COMPLETE!"
echo "=========================================="
ENDSSH
