# Server Deployment Commands

## Quick Deploy (One Command)
```bash
cd /var/www/drip && git pull origin main && source venv/bin/activate && python create_admin_login.py && python manage.py collectstatic --noinput && sudo systemctl restart crm
```

## Step-by-Step Commands

### 1. Navigate to project directory
```bash
cd /var/www/drip
```

### 2. Pull latest code
```bash
git pull origin main
```

### 3. Activate virtual environment
```bash
source venv/bin/activate
```

### 4. Create admin user
```bash
python create_admin_login.py
```

### 5. Collect static files
```bash
python manage.py collectstatic --noinput
```

### 6. Restart application
```bash
sudo systemctl restart crm
```

## Verify Deployment

### Check service status
```bash
sudo systemctl status crm
```

### View logs
```bash
sudo journalctl -u crm -f
```

## Admin Login Details

- **URL**: `https://yourdomain.com/team/login/`
- **Username**: `admin`
- **Password**: `8882443789`

## User Management

- **URL**: `https://yourdomain.com/user-management/`
- **Access**: Admin only

## Troubleshooting

### If service fails to restart
```bash
sudo systemctl stop crm
sudo systemctl start crm
sudo systemctl status crm
```

### Check for errors
```bash
sudo journalctl -u crm -n 50
```

### Test admin login
```bash
python manage.py shell
>>> from leads.models import TeamMember
>>> admin = TeamMember.objects.get(phone='8882443789')
>>> print(f"Name: {admin.name}, Role: {admin.role}")
```
