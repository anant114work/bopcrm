# 🚀 Server Deployment Fix - Quick Guide

## Your Current Issues

1. ❌ Projects and leads disappeared after deployment
2. ❌ New Meta leads not syncing in real-time
3. ❌ Need admin login credentials

---

## ✅ Solutions (Step by Step)

### 1. Fix Admin Login (5 minutes)

**SSH into your server and run:**

```bash
cd /path/to/your/crm
source venv/bin/activate  # or wherever your venv is

# Reset admin password
python manage.py changepassword admin
# Enter new password when prompted
```

**Login at:** `https://your-domain.com/admin/`
- Username: `admin`
- Password: (the one you just set)

---

### 2. Restore Missing Data (10 minutes)

Your data is still on your local machine! Let's transfer it:

**On your LOCAL machine:**

```bash
cd d:\AI-proto\CRM\drip

# Export all data
python manage.py dumpdata leads.Lead leads.Project leads.TeamMember leads.Property > data_backup.json

# Or export everything
python manage.py dumpdata > full_backup.json
```

**Transfer to server:**

```bash
# Using SCP (replace with your server details)
scp data_backup.json user@your-server:/path/to/crm/

# Or use FTP/SFTP client like FileZilla
```

**On SERVER:**

```bash
cd /path/to/your/crm
source venv/bin/activate

# Import data
python manage.py loaddata data_backup.json

# Restart server
sudo systemctl restart crm  # or your service name
```

**✅ Your projects and leads are back!**

---

### 3. Enable Real-Time Meta Sync (15 minutes)

#### A. Update Server .env File

**On SERVER, edit .env:**

```bash
nano .env  # or vim .env
```

**Add these lines:**

```env
# Meta Webhook Configuration
META_APP_SECRET=your_meta_app_secret_from_facebook
META_VERIFY_TOKEN=meta_webhook_verify_token_12345
```

**Get META_APP_SECRET:**
1. Go to https://developers.facebook.com/apps/
2. Select your app
3. Settings > Basic
4. Copy "App Secret"

**Save and restart:**

```bash
sudo systemctl restart crm
```

#### B. Configure Meta Webhook

1. Go to https://developers.facebook.com/apps/
2. Select your app
3. Click **Webhooks** in left menu
4. Click **Edit Subscription** for your Page
5. Enter:
   - **Callback URL:** `https://your-domain.com/webhook/meta/`
   - **Verify Token:** `meta_webhook_verify_token_12345`
6. Select **leadgen** field
7. Click **Verify and Save**

#### C. Test It

1. Submit a test lead through your Meta form
2. Check your CRM - lead should appear within 2 seconds!
3. No more manual sync needed! 🎉

---

### 4. Manual Sync (Backup Method)

If webhook isn't working yet, you can still sync manually:

**In your CRM dashboard:**
1. Click **"Sync Leads"** button
2. All Meta leads will be imported
3. This pulls ALL historical leads from Meta

---

## 🔧 Quick Troubleshooting

### Issue: "Can't login to admin"

```bash
# On server
python manage.py createsuperuser
# Create new admin account
```

### Issue: "Static files not loading"

```bash
python manage.py collectstatic --noinput
sudo systemctl restart nginx
```

### Issue: "CSRF verification failed"

**Update .env:**
```env
CSRF_TRUSTED_ORIGINS=https://your-domain.com
```

Restart server.

### Issue: "Webhook not receiving leads"

**Check webhook status:**
```bash
curl "https://your-domain.com/webhook/meta/?hub.mode=subscribe&hub.verify_token=meta_webhook_verify_token_12345&hub.challenge=test"
# Should return: test
```

**Check server logs:**
```bash
sudo journalctl -u crm -f
# or
tail -f /var/log/nginx/error.log
```

---

## 📋 Complete Deployment Checklist

### On Local Machine:
- [ ] Export data: `python manage.py dumpdata > backup.json`
- [ ] Transfer backup.json to server

### On Server:
- [ ] Update .env with META_APP_SECRET and META_VERIFY_TOKEN
- [ ] Import data: `python manage.py loaddata backup.json`
- [ ] Reset admin password: `python manage.py changepassword admin`
- [ ] Collect static files: `python manage.py collectstatic --noinput`
- [ ] Restart server: `sudo systemctl restart crm`

### In Meta Business Suite:
- [ ] Configure webhook URL: `https://your-domain.com/webhook/meta/`
- [ ] Set verify token: `meta_webhook_verify_token_12345`
- [ ] Subscribe to leadgen events
- [ ] Test with a lead submission

### Verify Everything Works:
- [ ] Login to admin panel: `https://your-domain.com/admin/`
- [ ] Check projects are visible
- [ ] Check leads are visible
- [ ] Submit test Meta lead - should appear instantly
- [ ] Click "Sync Leads" button - should pull historical leads

---

## 🎯 Summary

**Problem:** Data disappeared, leads not syncing in real-time

**Root Cause:** 
- Local SQLite database not transferred to server
- No webhook configured for real-time sync

**Solution:**
1. ✅ Export/import database from local to server
2. ✅ Configure Meta webhook for real-time sync
3. ✅ Reset admin password on server

**Result:**
- All your projects and leads restored
- New leads sync automatically in 1-2 seconds
- Manual sync button still works for historical data

---

## 📞 Need Help?

**Check these files for detailed guides:**
- `ADMIN_CREDENTIALS.md` - Admin login and password reset
- `META_WEBHOOK_SETUP.md` - Detailed webhook configuration
- `README.md` - Full project documentation

**Common Commands:**

```bash
# View logs
sudo journalctl -u crm -f

# Restart server
sudo systemctl restart crm

# Django shell
python manage.py shell

# Check database
python manage.py dbshell
```

---

## 🚀 You're All Set!

After following these steps:
- ✅ Admin access restored
- ✅ All data back in CRM
- ✅ Real-time lead sync working
- ✅ Manual sync as backup

**Test it:** Submit a Meta lead and watch it appear instantly! 🎉
