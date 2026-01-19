# Auto AI Calling System

## Overview
Automatically triggers AI calls for new leads based on form-to-project mappings with call logging to prevent duplicates.

## Features
- ✅ Automatic form-to-project mapping
- ✅ AI agent assignment per project
- ✅ Auto-trigger calls on new lead creation
- ✅ Call logging to prevent duplicate calls
- ✅ Manual trigger for unmapped leads
- ✅ Analytics and reporting

## Components

### 1. Models (`ai_agent_models.py`)
- **AIAgent**: Maps AI calling agents to projects
  - `name`: Agent name
  - `agent_id`: Call Karo AI agent ID
  - `project`: Associated project
  - `is_active`: Enable/disable agent

- **AICallLog**: Tracks all AI calls
  - `lead`: Lead being called
  - `agent`: AI agent used
  - `phone_number`: Called number
  - `status`: initiated/connected/failed/no_answer
  - `call_id`: Call Karo AI call ID
  - `initiated_at`: Call timestamp

### 2. Service (`auto_ai_call_service.py`)
**AutoAICallService** handles:
- Finding project from form mapping
- Getting AI agent for project
- Triggering Call Karo AI calls
- Logging all calls
- Preventing duplicate calls

### 3. Signal (`auto_ai_call_signal.py`)
Automatically triggers AI call when new lead is created via Django signal.

### 4. Views (`auto_ai_call_views.py`)
- `ai_agent_dashboard`: Manage agents and mappings
- `create_ai_agent`: Add new AI agent
- `create_form_mapping`: Map form to project
- `trigger_auto_call_for_lead`: Manual call trigger
- `process_unmapped_leads`: Batch process leads
- `call_logs_view`: View all call logs
- `ai_call_analytics`: Call analytics

## Setup

### 1. Run Migration
```bash
python manage.py migrate
```

### 2. Create Projects
Go to `/projects/` and create your projects.

### 3. Add AI Agents
Go to `/ai-agents/` and add AI agents:
- Name: "Gaur Yamuna Agent"
- Agent ID: "6923ff797a5d5a94d5a5dfcf"
- Project: Select project
- Status: Active

### 4. Create Form Mappings
Map form names to projects:
- Form Name: "Gaur Yamuna Expressway"
- Project: Select project

### 5. Test
Create a new lead with the mapped form name - AI call will trigger automatically!

## Usage

### Automatic (Recommended)
New leads are automatically called when created. The system:
1. Detects new lead creation
2. Finds project from form mapping
3. Gets AI agent for project
4. Checks if already called
5. Triggers AI call
6. Logs the call

### Manual Trigger
For existing leads without calls:
```
POST /ai-call/trigger/<lead_id>/
```

### Batch Process
Process all unmapped leads:
```
POST /ai-call/process-unmapped/
```

## API Endpoints

### Management
- `GET /ai-agents/` - Dashboard
- `POST /ai-agents/create/` - Create agent
- `POST /ai-agents/<id>/delete/` - Delete agent
- `POST /form-mappings/create-mapping/` - Create mapping
- `POST /form-mappings/<id>/delete-mapping/` - Delete mapping

### Calling
- `POST /ai-call/trigger/<lead_id>/` - Trigger call for lead
- `POST /ai-call/process-unmapped/` - Process unmapped leads
- `POST /ai-call/test-mapping/` - Test form mapping

### Analytics
- `GET /ai-call/logs/` - View call logs
- `GET /ai-call/analytics/` - Call analytics

## Call Flow

```
New Lead Created
    ↓
Signal Triggered
    ↓
Find Project (Form Mapping)
    ↓
Get AI Agent (Project → Agent)
    ↓
Check Already Called? → Yes → Skip
    ↓ No
Validate Phone Number
    ↓
Trigger Call Karo AI
    ↓
Log Call (AICallLog)
    ↓
Update Lead Stage → "contacted"
```

## Call Logging

Every call is logged with:
- Lead information
- Agent used
- Phone number
- Status (initiated/connected/failed)
- Timestamp
- Call ID from Call Karo AI

**Duplicate Prevention**: System checks `AICallLog` before calling to ensure leads aren't called multiple times.

## Configuration

### Call Karo AI Settings
In `settings.py` or `.env`:
```python
CALLKARO_API_KEY = 'your-api-key'
```

Default API key is hardcoded in service but can be overridden.

## Monitoring

### Dashboard (`/ai-agents/`)
- Total agents
- Active agents
- Calls today
- Success rate
- Recent calls

### Call Logs (`/ai-call/logs/`)
Filter by:
- Status
- Project
- Date

### Analytics (`/ai-call/analytics/`)
- Daily call stats (7 days)
- Project-wise performance
- Agent performance

## Troubleshooting

### Lead not being called
1. Check form mapping exists
2. Verify AI agent is active
3. Check if already called in logs
4. Validate phone number format

### Call failed
1. Check Call Karo AI agent ID
2. Verify API key
3. Check phone number format (+91XXXXXXXXXX)
4. Review error in AICallLog

### Duplicate calls
System prevents duplicates automatically. If needed, check:
```python
AICallLog.objects.filter(lead=lead, status__in=['initiated', 'connected'])
```

## Example Agent IDs

From your system:
- Gaur Yamuna: `6923ff797a5d5a94d5a5dfcf`
- AU Realty 1: `692d5b6ad10e948b7bbfc2db`
- AU Realty 2: `69294d3d2cc1373b1f3a3972`

## Database Schema

### AIAgent
```sql
CREATE TABLE leads_aiagent (
    id BIGINT PRIMARY KEY,
    name VARCHAR(100),
    agent_id VARCHAR(100) UNIQUE,
    project_id BIGINT REFERENCES leads_project(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP
);
```

### AICallLog
```sql
CREATE TABLE leads_aicalllog (
    id BIGINT PRIMARY KEY,
    lead_id BIGINT REFERENCES leads_lead(id),
    agent_id BIGINT REFERENCES leads_aiagent(id),
    phone_number VARCHAR(20),
    status VARCHAR(20),
    call_id VARCHAR(100),
    initiated_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT
);

CREATE INDEX idx_lead_status ON leads_aicalllog(lead_id, status);
CREATE INDEX idx_phone_time ON leads_aicalllog(phone_number, initiated_at);
```

## Future Enhancements

- [ ] Retry failed calls
- [ ] Schedule calls for specific times
- [ ] Multiple agents per project (load balancing)
- [ ] Call recording integration
- [ ] SMS fallback for failed calls
- [ ] WhatsApp integration
- [ ] Custom call scripts per project
- [ ] A/B testing different agents

## Support

For issues or questions, check:
1. Call logs: `/ai-call/logs/`
2. Django logs: `journalctl -u crm -f`
3. Call Karo AI dashboard
