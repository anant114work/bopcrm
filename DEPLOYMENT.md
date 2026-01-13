# Django CRM - Hostinger VPS Deployment Guide

## Prerequisites
- Hostinger VPS with Ubuntu 20.04/22.04
- Domain name pointed to your VPS IP
- SSH access to your VPS

## Quick Deployment Steps

### 1. Upload Project to VPS
```bash
# On your local machine
scp -r /path/to/drip root@your-vps-ip:/var/www/

# Or use Git
ssh root@your-vps-ip
cd /var/www
git clone your-repository-url drip
cd drip
```

### 2. Run Deployment Script
```bash
chmod +x deploy.sh
./deploy.sh
```

### 3. Configure Environment Variables
```bash
nano .env
```

Update these critical values:
```
SECRET_KEY=generate-new-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your-vps-ip
DATABASE_URL=postgresql://crm_user:your_secure_password@localhost:5432/crm_db
```

### 4. Update Nginx Configuration
```bash
sudo nano /etc/nginx/sites-available/crm
```

Replace `your_domain.com` with your actual domain.

### 5. Restart Services
```bash
sudo systemctl restart crm
sudo systemctl restart nginx
```

### 6. Setup SSL Certificate (Recommended)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

## Manual Deployment (Alternative)

### 1. Install Dependencies
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv nginx postgresql redis-server
```

### 2. Setup Database
```bash
sudo -u postgres psql
CREATE DATABASE crm_db;
CREATE USER crm_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE crm_db TO crm_user;
\q
```

### 3. Setup Python Environment
```bash
cd /var/www/drip
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Configure Django
```bash
cp .env.example .env
nano .env  # Edit with your settings
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py createsuperuser
```

### 5. Setup Gunicorn
```bash
gunicorn --bind 0.0.0.0:8000 crm.wsgi:application
```

Test if it works, then setup as systemd service (see deploy.sh).

### 6. Configure Nginx
Create `/etc/nginx/sites-available/crm`:
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location /static/ {
        alias /var/www/drip/staticfiles/;
    }
    
    location /media/ {
        alias /var/www/drip/media/;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/crm /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Useful Commands

### Check Service Status
```bash
sudo systemctl status crm
sudo systemctl status nginx
sudo systemctl status redis-server
```

### View Logs
```bash
sudo journalctl -u crm -f
sudo tail -f /var/log/nginx/error.log
```

### Restart Services
```bash
sudo systemctl restart crm
sudo systemctl restart nginx
```

### Update Application
```bash
cd /var/www/drip
source venv/bin/activate
git pull  # If using Git
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart crm
```

## Troubleshooting

### Static Files Not Loading
```bash
python manage.py collectstatic --noinput
sudo systemctl restart nginx
```

### Database Connection Error
Check DATABASE_URL in .env file and PostgreSQL service:
```bash
sudo systemctl status postgresql
```

### Permission Issues
```bash
sudo chown -R $USER:www-data /var/www/drip
sudo chmod -R 755 /var/www/drip
```

## Security Checklist
- ✅ Set DEBUG=False in production
- ✅ Use strong SECRET_KEY
- ✅ Configure ALLOWED_HOSTS properly
- ✅ Setup SSL certificate
- ✅ Use PostgreSQL instead of SQLite
- ✅ Setup firewall (UFW)
- ✅ Regular backups of database
- ✅ Keep dependencies updated

## Support
For issues, check logs:
- Application: `sudo journalctl -u crm -f`
- Nginx: `sudo tail -f /var/log/nginx/error.log`
- Django: Check `logs/` directory in project
