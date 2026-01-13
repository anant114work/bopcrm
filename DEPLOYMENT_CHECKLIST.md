# Pre-Deployment Checklist for Hostinger VPS

## ✅ Before Deployment

### 1. Environment Configuration
- [ ] Copy `.env.example` to `.env`
- [ ] Generate new SECRET_KEY (use: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
- [ ] Set `DEBUG=False`
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Setup `DATABASE_URL` for PostgreSQL
- [ ] Add all API keys (Meta, WhatsApp, OpenAI, etc.)

### 2. Database Setup
- [ ] Install PostgreSQL on VPS
- [ ] Create database: `crm_db`
- [ ] Create database user with password
- [ ] Grant privileges to user
- [ ] Update DATABASE_URL in .env

### 3. Static & Media Files
- [ ] Create `staticfiles/` directory
- [ ] Create `media/` directory
- [ ] Set proper permissions (755)
- [ ] Run `python manage.py collectstatic`

### 4. Security Settings
- [ ] Generate strong SECRET_KEY
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS properly
- [ ] Setup HTTPS/SSL certificate
- [ ] Enable firewall (UFW)
- [ ] Change default PostgreSQL password

### 5. Dependencies
- [ ] Install all packages from requirements.txt
- [ ] Install system packages (nginx, postgresql, redis)
- [ ] Setup virtual environment
- [ ] Verify Python version (3.8+)

## 🚀 Deployment Steps

### 1. Upload to VPS
```bash
# Option 1: SCP
scp -r /local/path/drip root@your-vps-ip:/var/www/

# Option 2: Git
ssh root@your-vps-ip
cd /var/www
git clone your-repo-url drip
```

### 2. Run Deployment Script
```bash
cd /var/www/drip
chmod +x deploy.sh
./deploy.sh
```

### 3. Configure Services
- [ ] Edit Nginx config with your domain
- [ ] Setup Gunicorn systemd service
- [ ] Enable and start services
- [ ] Setup SSL with Certbot

### 4. Database Migration
```bash
source venv/bin/activate
python manage.py migrate
python manage.py createsuperuser
```

### 5. Collect Static Files
```bash
python manage.py collectstatic --noinput
```

## 🔍 Post-Deployment Verification

### 1. Service Status
```bash
sudo systemctl status crm
sudo systemctl status nginx
sudo systemctl status postgresql
sudo systemctl status redis-server
```

### 2. Test Endpoints
- [ ] Visit https://yourdomain.com
- [ ] Check /admin/ login
- [ ] Test /health/ endpoint
- [ ] Verify static files loading
- [ ] Test media file upload

### 3. Functionality Tests
- [ ] Login to admin panel
- [ ] Create test lead
- [ ] Test lead sync
- [ ] Send test WhatsApp message
- [ ] Test AI features
- [ ] Verify team member access

### 4. Performance Check
- [ ] Check page load times
- [ ] Verify database queries
- [ ] Test with multiple users
- [ ] Monitor memory usage
- [ ] Check Redis connection

## 🔐 Security Checklist

- [ ] HTTPS enabled (SSL certificate)
- [ ] Firewall configured (UFW)
- [ ] SSH key authentication only
- [ ] Strong passwords for all services
- [ ] Database not exposed to internet
- [ ] Regular backups configured
- [ ] Security headers configured
- [ ] CSRF protection enabled
- [ ] XSS protection enabled

## 📊 Monitoring Setup

- [ ] Setup log rotation
- [ ] Configure error notifications
- [ ] Setup uptime monitoring
- [ ] Database backup automation
- [ ] Disk space monitoring
- [ ] Memory usage alerts

## 🔄 Backup Strategy

### Database Backup
```bash
# Create backup script
sudo nano /usr/local/bin/backup-crm-db.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/crm"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
pg_dump crm_db > $BACKUP_DIR/crm_db_$DATE.sql
# Keep only last 7 days
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
```

```bash
chmod +x /usr/local/bin/backup-crm-db.sh
# Add to crontab: 0 2 * * * /usr/local/bin/backup-crm-db.sh
```

### Media Files Backup
```bash
# Backup media files
tar -czf /var/backups/crm/media_$(date +%Y%m%d).tar.gz /var/www/drip/media/
```

## 🐛 Common Issues & Solutions

### Static Files Not Loading
```bash
python manage.py collectstatic --noinput
sudo systemctl restart nginx
```

### 502 Bad Gateway
```bash
sudo systemctl status crm
sudo journalctl -u crm -f
# Check Gunicorn socket file exists
```

### Database Connection Error
```bash
sudo systemctl status postgresql
# Verify DATABASE_URL in .env
```

### Permission Denied
```bash
sudo chown -R $USER:www-data /var/www/drip
sudo chmod -R 755 /var/www/drip
```

## 📝 Important URLs

- Application: https://yourdomain.com
- Admin Panel: https://yourdomain.com/admin/
- Health Check: https://yourdomain.com/health/
- API Docs: https://yourdomain.com/api/docs/ (if enabled)

## 🔗 Useful Commands

```bash
# Restart application
sudo systemctl restart crm

# View logs
sudo journalctl -u crm -f
sudo tail -f /var/log/nginx/error.log

# Update application
cd /var/www/drip
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart crm

# Database backup
pg_dump crm_db > backup.sql

# Database restore
psql crm_db < backup.sql
```

## 📞 Support Contacts

- VPS Provider: Hostinger Support
- Domain Registrar: [Your registrar]
- SSL Certificate: Let's Encrypt (Certbot)

## ✅ Final Checklist

- [ ] All services running
- [ ] HTTPS working
- [ ] Admin panel accessible
- [ ] Static files loading
- [ ] Database connected
- [ ] Backups configured
- [ ] Monitoring setup
- [ ] Documentation updated
- [ ] Team members notified
- [ ] DNS propagated

## 🎉 Deployment Complete!

Your Django CRM is now live at: **https://yourdomain.com**

Remember to:
1. Monitor logs regularly
2. Keep dependencies updated
3. Backup database daily
4. Review security settings monthly
5. Update SSL certificates (auto-renewed by Certbot)
