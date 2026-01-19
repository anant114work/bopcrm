# Auto AI Calling System - Deployment Checklist

## Pre-Deployment

- [ ] Review all created files
- [ ] Check code for syntax errors
- [ ] Verify imports are correct
- [ ] Test locally if possible

## Deployment Steps

### 1. Backup Database
```bash
python manage.py dumpdata > backup_before_ai_calling.json
```

### 2. Pull Latest Code
```bash
cd /var/www/drip
git pull origin main
```

### 3. Activate Virtual Environment
```bash
source venv/bin/activate
```

### 4. Install Dependencies (if any new)
```bash
pip install -r requirements.txt
```

### 5. Run Migration
```bash
python manage.py migrate
```

Expected output:
```
Running migrations:
  Applying leads.0047_ai_agent_models... OK
```

### 6. Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### 7. Restart Server
```bash
sudo systemctl restart crm
```

### 8. Check Server Status
```bash
sudo systemctl status crm
```

Should show: `active (running)`

### 9. Check Logs
```bash
sudo journalctl -u crm -f
```

Look for:
- No errors
- Server started successfully
- Signal registered

## Post-Deployment Verification

### 1. Check Setup Status
```bash
python manage.py setup_auto_ai_calling
```

Should show:
- Projects found
- Current agents (0 initially)
- Current mappings (0 initially)
- Call statistics

### 2. Access Dashboard
Open browser: `http://your-domain/ai-agents/`

Should see:
- Dashboard loads
- Stats cards (all zeros initially)
- Empty tables for agents and mappings

### 3. Create Test AI Agent
In dashboard:
- Click "Add Agent"
- Name: "Test Agent"
- Agent ID: "6923ff797a5d5a94d5a5dfcf"
- Project: Select any project
- Click "Create Agent"

Should see:
- Success message
- Agent appears in table

### 4. Create Test Form Mapping
In dashboard:
- Click "Add Mapping"
- Form Name: "Test Form"
- Project: Same as agent
- Click "Create Mapping"

Should see:
- Success message
- Mapping appears in table

### 5. Test Manual Trigger
Create a test lead with:
- Form name: "Test Form"
- Valid phone number

Then trigger manually:
```bash
curl -X POST http://your-domain/ai-call/trigger/<lead_id>/
```

Should return:
```json
{
  "success": true,
  "call_id": "...",
  "lead_name": "...",
  "project": "..."
}
```

### 6. Check Call Logs
Visit: `http://your-domain/ai-call/logs/`

Should see:
- Test call in logs
- Status: "initiated" or "connected"
- Correct lead and agent info

### 7. Test Automatic Trigger
Create a new lead via:
- Meta sync
- Google Sheets
- Manual entry

With form name matching your mapping.

Check logs:
```bash
sudo journalctl -u crm -f
```

Should see:
```
✅ Auto AI call triggered for lead: [Lead Name]
```

### 8. Verify No Duplicates
Try to trigger call again for same lead:
```bash
curl -X POST http://your-domain/ai-call/trigger/<lead_id>/
```

Should return:
```json
{
  "skipped": true,
  "reason": "Already called"
}
```

## Production Setup

### 1. Add Real AI Agents
For each project:
- Go to `/ai-agents/`
- Click "Add Agent"
- Enter real Call Karo AI agent ID
- Select project
- Activate

### 2. Create Form Mappings
For each form:
- Identify form name from leads
- Map to correct project
- Verify agent exists for project

### 3. Process Existing Leads (Optional)
To call existing unmapped leads:
```bash
curl -X POST http://your-domain/ai-call/process-unmapped/
```

This will process up to 50 leads at a time.

## Monitoring

### Daily Checks

1. **Call Volume**
   - Visit `/ai-call/analytics/`
   - Check daily call count
   - Verify success rate

2. **Failed Calls**
   - Visit `/ai-call/logs/?status=failed`
   - Review error messages
   - Fix issues

3. **Unmapped Leads**
   ```bash
   python manage.py setup_auto_ai_calling
   ```
   - Check "Unmapped Leads" count
   - Create mappings if needed

### Weekly Checks

1. **Agent Performance**
   - Visit `/ai-call/analytics/`
   - Review agent stats
   - Optimize if needed

2. **Form Mappings**
   - Check for new form names
   - Add mappings as needed

3. **Database Cleanup**
   - Old call logs can be archived
   - Keep last 90 days active

## Troubleshooting

### Issue: Migration Fails
```bash
# Check migration status
python manage.py showmigrations leads

# If needed, fake the migration
python manage.py migrate leads 0047 --fake

# Then run again
python manage.py migrate
```

### Issue: Dashboard Not Loading
```bash
# Check URL configuration
python manage.py show_urls | grep ai-agents

# Check static files
python manage.py collectstatic --noinput

# Restart server
sudo systemctl restart crm
```

### Issue: Signal Not Triggering
```bash
# Check apps.py
cat leads/apps.py | grep auto_ai_call_signal

# Check logs
sudo journalctl -u crm -f

# Restart server
sudo systemctl restart crm
```

### Issue: Calls Not Working
```bash
# Test Call Karo AI directly
curl -X POST https://api.callkaro.ai/call/outbound \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: your-api-key" \
  -d '{
    "to_number": "+919876543210",
    "agent_id": "your-agent-id",
    "metadata": {"test": true},
    "priority": 1
  }'
```

## Rollback Plan

If issues occur:

### 1. Restore Database
```bash
python manage.py loaddata backup_before_ai_calling.json
```

### 2. Revert Migration
```bash
python manage.py migrate leads 0046
```

### 3. Remove New Files
```bash
rm leads/ai_agent_models.py
rm leads/auto_ai_call_service.py
rm leads/auto_ai_call_signal.py
rm leads/auto_ai_call_views.py
```

### 4. Restore Modified Files
```bash
git checkout leads/models.py
git checkout leads/apps.py
git checkout leads/urls.py
git checkout leads/admin.py
```

### 5. Restart Server
```bash
sudo systemctl restart crm
```

## Success Indicators

✅ Migration completed successfully
✅ Dashboard loads without errors
✅ Can create AI agents
✅ Can create form mappings
✅ Manual trigger works
✅ Automatic trigger works
✅ Call logs are accurate
✅ Duplicates are prevented
✅ Analytics show data
✅ No errors in logs

## Support Contacts

- System logs: `sudo journalctl -u crm -f`
- Dashboard: `/ai-agents/`
- Setup command: `python manage.py setup_auto_ai_calling`
- Documentation: `AUTO_AI_CALLING.md`

## Post-Deployment Tasks

- [ ] Document agent IDs used
- [ ] Document form mappings created
- [ ] Train team on dashboard
- [ ] Set up monitoring alerts
- [ ] Schedule weekly reviews
- [ ] Update runbook

---

**Deployment Complete! 🎉**

Monitor the system for 24 hours to ensure stability.
