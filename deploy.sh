#!/bin/bash

# Django CRM Deployment Script for Hostinger VPS
# Run this script on your VPS after uploading the project

echo "🚀 Starting Django CRM Deployment..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
echo "🐍 Installing Python and dependencies..."
sudo apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib redis-server

# Create virtual environment
echo "🔧 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python packages
echo "📚 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Setup PostgreSQL database
echo "🗄️ Setting up PostgreSQL database..."
sudo -u postgres psql -c "CREATE DATABASE crm_db;"
sudo -u postgres psql -c "CREATE USER crm_user WITH PASSWORD 'your_secure_password';"
sudo -u postgres psql -c "ALTER ROLE crm_user SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE crm_user SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE crm_user SET timezone TO 'Asia/Kolkata';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE crm_db TO crm_user;"

# Create .env file
echo "⚙️ Creating .env file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️ Please edit .env file with your actual credentials"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p staticfiles media logs

# Collect static files
echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput

# Run migrations
echo "🔄 Running database migrations..."
python manage.py migrate

# Create superuser (optional)
echo "👤 Create Django superuser (optional)..."
python manage.py createsuperuser --noinput --username admin --email admin@example.com || true

# Setup Gunicorn service
echo "🔧 Setting up Gunicorn service..."
sudo tee /etc/systemd/system/crm.service > /dev/null <<EOF
[Unit]
Description=Django CRM Gunicorn daemon
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

# Setup Nginx
echo "🌐 Setting up Nginx..."
sudo tee /etc/nginx/sites-available/crm > /dev/null <<EOF
server {
    listen 80;
    server_name your_domain.com www.your_domain.com;

    client_max_body_size 100M;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias $(pwd)/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias $(pwd)/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:$(pwd)/crm.sock;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header Host \$host;
        proxy_redirect off;
    }
}
EOF

# Enable Nginx site
sudo ln -sf /etc/nginx/sites-available/crm /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Start services
echo "🚀 Starting services..."
sudo systemctl start crm
sudo systemctl enable crm
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Setup Celery (optional)
echo "⚙️ Setting up Celery worker..."
sudo tee /etc/systemd/system/celery.service > /dev/null <<EOF
[Unit]
Description=Celery Service
After=network.target

[Service]
Type=forking
User=$USER
Group=www-data
WorkingDirectory=$(pwd)
Environment="PATH=$(pwd)/venv/bin"
ExecStart=$(pwd)/venv/bin/celery -A crm worker -l info

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl start celery
sudo systemctl enable celery

# Setup Celery Beat (optional)
sudo tee /etc/systemd/system/celerybeat.service > /dev/null <<EOF
[Unit]
Description=Celery Beat Service
After=network.target

[Service]
Type=simple
User=$USER
Group=www-data
WorkingDirectory=$(pwd)
Environment="PATH=$(pwd)/venv/bin"
ExecStart=$(pwd)/venv/bin/celery -A crm beat -l info

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl start celerybeat
sudo systemctl enable celerybeat

echo "✅ Deployment completed!"
echo ""
echo "📝 Next steps:"
echo "1. Edit .env file with your actual credentials"
echo "2. Update Nginx config with your domain name"
echo "3. Run: sudo systemctl restart crm nginx"
echo "4. Setup SSL with: sudo certbot --nginx -d your_domain.com"
echo ""
echo "🔗 Your application should be running at http://your_domain.com"
