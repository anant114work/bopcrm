# Auto AI Calling System - Quick Start

## What Was Created

A complete system that automatically triggers AI calls for new leads based on form-to-project mappings with duplicate prevention.

## Files Created

### Core System
1. **`leads/ai_agent_models.py`** - Database models for AI agents and call logs
2. **`leads/auto_ai_call_service.py`** - Service that handles call logic
3. **`leads/auto_ai_call_signal.py`** - Auto-trigger on new lead creation
4. **`leads/auto_ai_call_views.py`** - Web interface and API endpoints
5. **`leads/migrations/0047_ai_agent_models.py`** - Database migration

### Templates
6. **`leads/templates/leads/ai_agent_dashboard.html`** - Management dashboard

### Documentation
7. **`AUTO_AI_CALLING.md`** - Complete documentation
8. **`QUICK_START.md`** - This file
9. **`leads/management/commands/setup_auto_ai_calling.py`** - Setup command

## How It Works

```
New Lead → Find Project (Form Mapping) → Get AI Agent → Check if Called → Trigger Call → Log
```

## Quick Setup (5 minutes)

### Step 1: Run Migration
```bash
python manage.py migrate
```

### Step 2: Check Status
```bash
python manage.py setup_auto_ai_calling
```

### Step 3: Access Dashboard
Open browser: `http://your-domain/ai-agents/`

### Step 4: Add AI Agent
Click "Add Agent" button:
- Name: `Gaur Yamuna Agent`
- Agent ID: `6923ff797a5d5a94d5a5dfcf`
- Project: Select your project
- Click "Create Agent"

### Step 5: Add Form Mapping
Click "Add Mapping" button:
- Form Name: `Gaur Yamuna Expressway` (or your form name)
- Project: Select same project
- Click "Create Mapping"

### Step 6: Test
Create a new lead with the mapped form name - it will be automatically called!

## Key Features

✅ **Automatic Calling**: New leads are called immediately
✅ **Duplicate Prevention**: Each lead called only once
✅ **Call Logging**: Every call is tracked
✅ **Project Mapping**: Forms automatically mapped to projects
✅ **AI Agent Assignment**: Each project has its own AI agent
✅ **Analytics**: Track call success rates

## URLs

- **Dashboard**: `/ai-agents/`
- **Call Logs**: `/ai-call/logs/`
- **Analytics**: `/ai-call/analytics/`
- **Manual Trigger**: `/ai-call/trigger/<lead_id>/`
- **Batch Process**: `/ai-call/process-unmapped/`

## API Examples

### Create AI Agent
```bash
curl -X POST http://your-domain/ai-agents/create/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Gaur Yamuna Agent",
    "agent_id": "6923ff797a5d5a94d5a5dfcf",
    "project_id": 1,
    "is_active": true
  }'
```

### Create Form Mapping
```bash
curl -X POST http://your-domain/form-mappings/create-mapping/ \
  -H "Content-Type: application/json" \
  -d '{
    "form_name": "Gaur Yamuna Expressway",
    "project_id": 1
  }'
```

### Trigger Call for Lead
```bash
curl -X POST http://your-domain/ai-call/trigger/123/
```

### Process Unmapped Leads
```bash
curl -X POST http://your-domain/ai-call/process-unmapped/
```

## Database Tables

### AIAgent
Stores AI calling agents mapped to projects.

### AICallLog
Logs every call with status, timestamp, and prevents duplicates.

### FormSourceMapping
Maps lead form names to projects (already existed, now integrated).

## Monitoring

### Check Call Logs
```bash
# Via web
http://your-domain/ai-call/logs/

# Via Django shell
python manage.py shell
>>> from leads.ai_agent_models import AICallLog
>>> AICallLog.objects.filter(status='connected').count()
```

### View Analytics
```bash
http://your-domain/ai-call/analytics/
```

### Check Unmapped Leads
```bash
python manage.py setup_auto_ai_calling
```

## Troubleshooting

### Lead Not Called?
1. Check form mapping exists: `/ai-agents/`
2. Verify AI agent is active
3. Check call logs: `/ai-call/logs/`
4. Validate phone number format

### Call Failed?
1. Check Call Karo AI agent ID is correct
2. Verify API key in settings
3. Check phone number format (+91XXXXXXXXXX)
4. Review error in call logs

### Duplicate Calls?
System automatically prevents duplicates. Check:
```python
from leads.ai_agent_models import AICallLog
AICallLog.objects.filter(lead_id=123)
```

## Configuration

### Call Karo AI API Key
In `.env` or `settings.py`:
```python
CALLKARO_API_KEY = 'your-api-key-here'
```

Default: `bc422db39aa327234a911dd901accfcfa975623ee84c65c83aae9c4f844ffdb8`

## Example Agent IDs

From your existing system:
- **Gaur Yamuna**: `6923ff797a5d5a94d5a5dfcf`
- **AU Realty 1**: `692d5b6ad10e948b7bbfc2db`
- **AU Realty 2**: `69294d3d2cc1373b1f3a3972`

## Testing

### Test Form Mapping
```bash
curl -X POST http://your-domain/ai-call/test-mapping/ \
  -H "Content-Type: application/json" \
  -d '{"form_name": "Gaur Yamuna Expressway"}'
```

Response:
```json
{
  "success": true,
  "project": {"id": 1, "name": "Gaur Yamuna City"},
  "agent": {"id": 1, "name": "Gaur Yamuna Agent", "agent_id": "6923ff797a5d5a94d5a5dfcf"}
}
```

## Production Deployment

### 1. Run Migration
```bash
python manage.py migrate
```

### 2. Restart Server
```bash
sudo systemctl restart crm
```

### 3. Verify Signal Active
Check logs:
```bash
sudo journalctl -u crm -f
```

Look for: `✅ Auto AI call triggered for lead: ...`

## Support

- **Documentation**: `AUTO_AI_CALLING.md`
- **Dashboard**: `/ai-agents/`
- **Logs**: `sudo journalctl -u crm -f`

## Next Steps

1. ✅ Run migration
2. ✅ Add AI agents
3. ✅ Create form mappings
4. ✅ Test with new lead
5. ✅ Monitor call logs
6. ✅ Review analytics

## Success Indicators

- New leads show in call logs immediately
- Call status is "connected" or "initiated"
- Lead stage changes to "contacted"
- No duplicate calls in logs
- Analytics show increasing call count

---

**System is ready! Create a new lead to see it in action! 🚀**
