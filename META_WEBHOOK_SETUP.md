# Meta Real-Time Webhook Setup Guide

## Problem
Your CRM was only syncing leads manually. New leads from Meta weren't appearing automatically.

## Solution
I've added a real-time webhook endpoint that receives leads instantly from Meta.

---

## Step 1: Update Your Server .env File

Add these lines to your server's `.env` file:

```env
META_APP_SECRET=your_meta_app_secret_here
META_VERIFY_TOKEN=meta_webhook_verify_token_12345
```

**Where to find META_APP_SECRET:**
1. Go to https://developers.facebook.com/apps/
2. Select your app
3. Go to Settings > Basic
4. Copy the "App Secret"

---

## Step 2: Configure Meta Webhook

### A. Get Your Webhook URL
Your webhook URL is: `https://your-server-domain.com/webhook/meta/`

Example: `https://crm.yourdomain.com/webhook/meta/`

### B. Setup in Meta Business Suite

1. Go to https://developers.facebook.com/apps/
2. Select your app
3. Go to **Webhooks** in the left menu
4. Click **Edit Subscription** for your Page
5. Add webhook:
   - **Callback URL**: `https://your-server-domain.com/webhook/meta/`
   - **Verify Token**: `meta_webhook_verify_token_12345` (same as in .env)
   - **Fields**: Select `leadgen` (Lead Generation)
6. Click **Verify and Save**

### C. Subscribe to Page Events

1. In Webhooks section, find your Page
2. Click **Subscribe to this object**
3. Select **leadgen** field
4. Save

---

## Step 3: Test the Webhook

### Option 1: Test from Meta
1. Go to your Meta Business Suite
2. Submit a test lead through your lead form
3. Check your CRM - the lead should appear within seconds!

### Option 2: Manual Test
1. Click "Sync Leads" button in your CRM to pull existing leads
2. Submit a new test lead
3. It should appear automatically without clicking sync

---

## Step 4: Restart Your Server

After updating .env:

```bash
# If using systemd
sudo systemctl restart crm

# If using gunicorn directly
pkill gunicorn
gunicorn crm.wsgi:application --bind 0.0.0.0:8000 --daemon

# If using Docker
docker-compose restart
```

---

## How It Works

**Before (Manual Sync):**
- New lead submitted → Stored in Meta
- You click "Sync" button → CRM fetches leads
- Delay: Minutes to hours

**After (Real-Time Webhook):**
- New lead submitted → Meta sends webhook instantly
- CRM receives and saves lead automatically
- Delay: 1-2 seconds ⚡

---

## Troubleshooting

### Webhook Not Working?

1. **Check webhook is verified:**
   - Go to Meta Developers > Webhooks
   - Status should be "Active" with green checkmark

2. **Check server logs:**
   ```bash
   sudo journalctl -u crm -f
   # or
   tail -f /var/log/crm/error.log
   ```

3. **Test webhook manually:**
   ```bash
   curl -X POST https://your-domain.com/webhook/meta/ \
     -H "Content-Type: application/json" \
     -d '{"test": "data"}'
   ```

4. **Verify .env is loaded:**
   - Restart your server after updating .env
   - Check settings are loaded in Django shell:
   ```python
   python manage.py shell
   >>> from django.conf import settings
   >>> print(settings.META_VERIFY_TOKEN)
   ```

### Still No Leads?

1. **Manual sync still works:**
   - Click "Sync Leads" button to pull all existing leads
   - This fetches historical leads from Meta

2. **Check Meta Access Token:**
   - Token might be expired
   - Generate new token from Meta Business Suite
   - Update META_ACCESS_TOKEN in .env

3. **Check Form Permissions:**
   - Ensure your Meta app has permission to access lead forms
   - Go to Meta Business Suite > Settings > Lead Access

---

## Database Migration Issue

You mentioned projects and leads disappeared after deployment. This is because:

**Local Development:**
- Uses SQLite database (db.sqlite3 file)
- All data stored locally

**Server Deployment:**
- Needs PostgreSQL or MySQL
- Local SQLite data NOT automatically transferred

### Solution: Migrate Your Data

#### Option 1: Export/Import (Recommended)

**On Local Machine:**
```bash
python manage.py dumpdata leads.Lead leads.Project leads.TeamMember > backup.json
```

**On Server:**
```bash
# Upload backup.json to server
python manage.py loaddata backup.json
```

#### Option 2: Fresh Start + Sync

1. Create projects manually on server
2. Click "Sync Leads" to pull all Meta leads
3. Leads will be imported with all historical data

#### Option 3: Use PostgreSQL Everywhere

Update your local .env:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/crm_db
```

Then both local and server use same database type.

---

## Quick Commands

### Sync All Historical Leads
```bash
# Via Django shell
python manage.py shell
>>> from leads.views import sync_leads
>>> from django.http import HttpRequest
>>> request = HttpRequest()
>>> request.method = 'POST'
>>> sync_leads(request)
```

### Check Webhook Status
```bash
curl https://your-domain.com/webhook/meta/?hub.mode=subscribe&hub.verify_token=meta_webhook_verify_token_12345&hub.challenge=test123
# Should return: test123
```

### View Recent Leads
```bash
python manage.py shell
>>> from leads.models import Lead
>>> Lead.objects.order_by('-created_time')[:5]
```

---

## Summary

✅ **Real-time webhook created** - Leads sync automatically
✅ **Manual sync still works** - Click button to pull historical leads
✅ **Auto-assignment enabled** - New leads assigned to team members
✅ **Webhook verification** - Secure Meta integration

**Next Steps:**
1. Update .env with META_APP_SECRET
2. Configure webhook in Meta Business Suite
3. Test with a lead submission
4. Migrate your local data to server (if needed)

---

## Need Help?

- Check server logs for errors
- Test webhook with curl command
- Verify Meta app permissions
- Ensure .env is loaded (restart server)
