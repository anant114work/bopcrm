#!/bin/bash

# Automated Server Setup Script for Django CRM
# This script sets up everything automatically

set -e

echo "🚀 Django CRM - Automated Server Setup"
echo "========================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Get server IP
SERVER_IP=$(hostname -I | awk '{print $1}')

echo -e "${GREEN}✓${NC} Server IP: $SERVER_IP"

# 1. Update system
echo -e "\n${YELLOW}[1/15]${NC} Updating system packages..."
sudo apt update -qq && sudo apt upgrade -y -qq

# 2. Install dependencies
echo -e "${YELLOW}[2/15]${NC} Installing dependencies..."
sudo apt install -y -qq python3 python3-pip python3-venv nginx postgresql postgresql-contrib redis-server

# 3. Setup PostgreSQL
echo -e "${YELLOW}[3/15]${NC} Setting up PostgreSQL database..."
DB_PASSWORD="CRM$(openssl rand -base64 12 | tr -dc 'a-zA-Z0-9')"
sudo -u postgres psql -c "DROP DATABASE IF EXISTS crm_db;" 2>/dev/null || true
sudo -u postgres psql -c "DROP USER IF EXISTS crm_user;" 2>/dev/null || true
sudo -u postgres psql << EOF
CREATE DATABASE crm_db;
CREATE USER crm_user WITH PASSWORD '$DB_PASSWORD';
ALTER ROLE crm_user SET client_encoding TO 'utf8';
ALTER ROLE crm_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE crm_user SET timezone TO 'Asia/Kolkata';
GRANT ALL PRIVILEGES ON DATABASE crm_db TO crm_user;
EOF

# 4. Create virtual environment
echo -e "${YELLOW}[4/15]${NC} Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# 5. Install Python packages
echo -e "${YELLOW}[5/15]${NC} Installing Python packages..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

# 6. Generate SECRET_KEY
echo -e "${YELLOW}[6/15]${NC} Generating SECRET_KEY..."
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")

# 7. Create .env file
echo -e "${YELLOW}[7/15]${NC} Creating .env configuration..."
cat > .env << EOF
SECRET_KEY=$SECRET_KEY
DEBUG=False
ALLOWED_HOSTS=*

DATABASE_URL=postgresql://crm_user:$DB_PASSWORD@localhost:5432/crm_db

META_ACCESS_TOKEN=your-meta-token
META_PAGE_ID=your-page-id
WHATSAPP_TOKEN=your-whatsapp-token
WHATSAPP_PHONE_ID=your-phone-id

TATA_API_TOKEN=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIzMTE2MDAiLCJjciI6dHJ1ZSwiaXNzIjoiaHR0cHM6Ly9jbG91ZHBob25lLnRhdGF0ZWxlc2VydmljZXMuY29tL3Rva2VuL2dlbmVyYXRlIiwiaWF0IjoxNzUxOTc4Nzg5LCJleHAiOjIwNTE5Nzg3ODksIm5iZiI6MTc1MTk3ODc4OSwianRpIjoiY3Bvc1Z4TW9oOHpWZ2d3MCJ9.G8qzkWIN0i3Dj5zxnct5JW-PpBlk6DUjXlSq6sWvc9I

OPENAI_API_KEY=your-openai-key
CALLKARO_API_KEY=your-callkaro-key
CALLKARO_DEFAULT_AGENT_ID=your-agent-id

AUTO_SYNC_ENABLED=True
SYNC_INTERVAL_MINUTES=30
REDIS_URL=redis://localhost:6379/0
EOF

# 8. Create directories
echo -e "${YELLOW}[8/15]${NC} Creating directories..."
mkdir -p staticfiles media logs

# 9. Run migrations
echo -e "${YELLOW}[9/15]${NC} Running database migrations..."
python manage.py migrate --noinput

# 10. Collect static files
echo -e "${YELLOW}[10/15]${NC} Collecting static files..."
python manage.py collectstatic --noinput

# 11. Create superuser
echo -e "${YELLOW}[11/15]${NC} Creating admin user..."
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@crm.com', 'admin123')" | python manage.py shell

# 12. Setup Gunicorn service
echo -e "${YELLOW}[12/15]${NC} Setting up Gunicorn service..."
sudo tee /etc/systemd/system/crm.service > /dev/null << EOF
[Unit]
Description=Django CRM Gunicorn
After=network.target

[Service]
User=$USER
Group=www-data
WorkingDirectory=$(pwd)
Environment="PATH=$(pwd)/venv/bin"
ExecStart=$(pwd)/venv/bin/gunicorn --workers 3 --bind unix:$(pwd)/crm.sock crm.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

# 13. Setup Nginx
echo -e "${YELLOW}[13/15]${NC} Setting up Nginx..."
sudo tee /etc/nginx/sites-available/crm > /dev/null << EOF
server {
    listen 80;
    server_name $SERVER_IP _;
    client_max_body_size 100M;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias $(pwd)/staticfiles/;
        expires 30d;
    }

    location /media/ {
        alias $(pwd)/media/;
        expires 30d;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:$(pwd)/crm.sock;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/crm /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t

# 14. Set permissions
echo -e "${YELLOW}[14/15]${NC} Setting permissions..."
sudo chown -R $USER:www-data $(pwd)
sudo chmod -R 755 $(pwd)

# 15. Start services
echo -e "${YELLOW}[15/15]${NC} Starting services..."
sudo systemctl daemon-reload
sudo systemctl start crm
sudo systemctl enable crm
sudo systemctl restart nginx
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Print summary
echo -e "\n${GREEN}✅ Installation Complete!${NC}"
echo "========================================"
echo -e "${GREEN}✓${NC} Application URL: http://$SERVER_IP"
echo -e "${GREEN}✓${NC} Admin Panel: http://$SERVER_IP/admin/"
echo -e "${GREEN}✓${NC} Admin Username: admin"
echo -e "${GREEN}✓${NC} Admin Password: admin123"
echo -e "${GREEN}✓${NC} Database Password: $DB_PASSWORD"
echo ""
echo -e "${YELLOW}⚠️  Important:${NC}"
echo "1. Change admin password after first login"
echo "2. Update API keys in .env file"
echo "3. Setup domain and SSL certificate"
echo ""
echo -e "${GREEN}Commands:${NC}"
echo "  View logs: sudo journalctl -u crm -f"
echo "  Restart: sudo systemctl restart crm nginx"
echo "  Status: sudo systemctl status crm"
echo ""
echo -e "${GREEN}🎉 Your CRM is ready!${NC}"
