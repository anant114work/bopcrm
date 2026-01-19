# 🎯 QUICK START - Fix Your CRM Now!

## What Happened?

When you deployed to the server:
1. Your local database (SQLite) wasn't copied → **Projects & leads disappeared**
2. No webhook configured → **New Meta leads not syncing in real-time**
3. Admin password needs reset on server

---

## 🔥 3-Step Fix (30 minutes)

### STEP 1: Get Admin Access (5 min)

**SSH into your server:**

```bash
python manage.py changepassword admin
```

**Login:** `https://your-domain.com/admin/`
- Username: `admin`
- Password: (what you just set)

---

### STEP 2: Restore Your Data (10 min)

**On your LOCAL computer (Windows):**

```bash
cd d:\AI-proto\CRM\drip
python manage.py dumpdata > backup.json
```

**Upload backup.json to your server** (use FileZilla, WinSCP, or SCP)

**On SERVER:**

```bash
python manage.py loaddata backup.json
sudo systemctl restart crm
```

**✅ All your projects and leads are back!**

---

### STEP 3: Enable Real-Time Sync (15 min)

**A. Update server .env file:**

Add these 2 lines:
```env
META_APP_SECRET=get_from_facebook_app_settings
META_VERIFY_TOKEN=meta_webhook_verify_token_12345
```

**B. Configure Meta webhook:**

1. Go to https://developers.facebook.com/apps/
2. Your App → Webhooks → Edit Subscription
3. Callback URL: `https://your-domain.com/webhook/meta/`
4. Verify Token: `meta_webhook_verify_token_12345`
5. Subscribe to: `leadgen`
6. Save

**C. Restart server:**

```bash
sudo systemctl restart crm
```

**✅ Test:** Submit a Meta lead → Should appear in CRM within 2 seconds!

---

## 🎉 Done!

Your CRM is now:
- ✅ Fully restored with all data
- ✅ Syncing leads in real-time
- ✅ Admin access working

---

## 📚 Detailed Guides

- **DEPLOYMENT_FIX.md** - Complete step-by-step guide
- **ADMIN_CREDENTIALS.md** - Admin login & password reset
- **META_WEBHOOK_SETUP.md** - Webhook configuration details

---

## ⚡ Quick Commands

```bash
# Reset admin password
python manage.py changepassword admin

# Export data (local)
python manage.py dumpdata > backup.json

# Import data (server)
python manage.py loaddata backup.json

# Restart server
sudo systemctl restart crm

# View logs
sudo journalctl -u crm -f

# Manual sync (if webhook not working)
# Click "Sync Leads" button in CRM dashboard
```

---

## 🆘 Still Having Issues?

### Leads not syncing?
- Click "Sync Leads" button (manual sync)
- Check webhook is verified in Meta
- Check server logs: `sudo journalctl -u crm -f`

### Can't login?
- Create new superuser: `python manage.py createsuperuser`

### Data still missing?
- Re-run: `python manage.py loaddata backup.json`
- Check file was uploaded correctly

---

**Need more help?** Check the detailed guides in this folder!
