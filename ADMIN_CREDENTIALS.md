# Admin Login Credentials & Setup

## Current Admin Account

**Username:** `admin`  
**Email:** `admin@test.com`  
**Password:** You need to reset it (see below)

---

## Reset Admin Password

Since you deployed to a new server, you need to reset the admin password:

### Method 1: Django Shell (Recommended)

```bash
python manage.py shell
```

Then run:
```python
from django.contrib.auth.models import User
admin = User.objects.get(username='admin')
admin.set_password('your_new_password')
admin.save()
print("Password updated successfully!")
exit()
```

### Method 2: Django Command

```bash
python manage.py changepassword admin
```

It will prompt you to enter a new password.

### Method 3: Create New Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts:
- Username: (choose your username)
- Email: (your email)
- Password: (choose a strong password)

---

## Login URLs

### Django Admin Panel
`https://your-domain.com/admin/`

**Features:**
- Manage users
- View all database tables
- Edit leads, projects, team members
- System configuration

### CRM Dashboard
`https://your-domain.com/`

**Features:**
- Lead management
- Team dashboard
- Analytics
- WhatsApp campaigns
- Call management

---

## Team Member Login

If you want team members to have their own login:

### Create Team Member Account

1. Go to Django Admin: `/admin/`
2. Navigate to **Team Members**
3. Click **Add Team Member**
4. Fill in details:
   - Name
   - Email
   - Phone
   - Role (Admin/Manager/Sales)
   - Set password

### Team Member Login URL
`https://your-domain.com/team/login/`

---

## Security Best Practices

### 1. Change Default Credentials
```bash
# Never use default passwords in production!
python manage.py changepassword admin
```

### 2. Update SECRET_KEY in .env
```env
# Generate a new secret key
SECRET_KEY=your-new-secret-key-here-make-it-long-and-random
```

Generate a secure key:
```python
python manage.py shell
>>> from django.core.management.utils import get_random_secret_key
>>> print(get_random_secret_key())
```

### 3. Set DEBUG=False in Production
```env
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
```

### 4. Enable HTTPS
```env
SECURE_SSL_REDIRECT=True
SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
```

---

## Common Issues

### "CSRF Verification Failed"

Add your domain to .env:
```env
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

### "Static Files Not Loading"

```bash
python manage.py collectstatic --noinput
sudo systemctl restart nginx
```

### "Can't Login - Invalid Credentials"

Reset password:
```bash
python manage.py changepassword admin
```

### "Database is Empty"

You need to migrate your local data to server:

**Export from local:**
```bash
python manage.py dumpdata > backup.json
```

**Import on server:**
```bash
python manage.py loaddata backup.json
```

---

## Quick Setup Checklist

After deploying to server:

- [ ] Create/reset admin password
- [ ] Update SECRET_KEY in .env
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS
- [ ] Add CSRF_TRUSTED_ORIGINS
- [ ] Run migrations: `python manage.py migrate`
- [ ] Collect static files: `python manage.py collectstatic`
- [ ] Import data: `python manage.py loaddata backup.json`
- [ ] Setup Meta webhook (see META_WEBHOOK_SETUP.md)
- [ ] Test login at /admin/
- [ ] Test CRM dashboard at /

---

## Default Accounts Summary

| Account Type | Username | Login URL | Purpose |
|-------------|----------|-----------|---------|
| Django Admin | `admin` | `/admin/` | Full system access |
| Team Member | (custom) | `/team/login/` | Limited CRM access |

---

## Need to Create Fresh Database?

If you want to start fresh:

```bash
# Backup first!
python manage.py dumpdata > backup.json

# Delete database (SQLite)
rm db.sqlite3

# Or drop PostgreSQL database
# dropdb crm_db
# createdb crm_db

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Import data (optional)
python manage.py loaddata backup.json
```

---

## Contact & Support

For password reset or access issues:
1. SSH into your server
2. Run: `python manage.py changepassword admin`
3. Or create new superuser: `python manage.py createsuperuser`

**Remember:** Never commit passwords or credentials to Git!
