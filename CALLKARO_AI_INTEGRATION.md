# Call Karo AI Integration

This document describes the integration of Call Karo AI into the Meta Leads CRM system.

## Overview

Call Karo AI has been integrated as an additional calling option alongside the existing Acefone functionality. Users can now choose between:

1. **Traditional Calling** (Acefone) - Direct human-to-human calls
2. **AI-Powered Calling** (Call Karo AI) - AI agents handle conversations automatically

## Features Implemented

### 1. Call Provider Selection
- Users can switch between Acefone and Call Karo AI in the call panel
- Dynamic UI updates based on selected provider
- Provider-specific configuration and information display

### 2. Call Karo AI Configuration
- **URL**: `/callkaro-config/`
- Configure API key and default agent ID
- Add and manage AI agents
- Assign agents to team members

### 3. AI Agent Management
- Create multiple AI agents with unique IDs
- Assign agents to specific team members
- Track agent usage and performance

### 4. Outbound Call API Integration
- **Endpoint**: `POST https://api.callkaro.ai/call/outbound`
- Support for immediate and scheduled calls
- Retry configuration and priority settings
- Lead metadata integration

### 5. Campaign Management
- **Endpoint**: `POST https://api.callkaro.ai/call/campaign`
- Create batch call campaigns
- Schedule multiple calls with AI agents
- Track campaign progress and completion rates

### 6. Call Logging and Tracking
- Comprehensive call logs for AI calls
- Status tracking (initiated, completed, failed, etc.)
- Duration and metadata storage
- Integration with existing CRM lead records

### 7. Dashboard and Analytics
- **URL**: `/callkaro-dashboard/`
- Real-time statistics for AI calls
- Recent call history
- Campaign performance metrics
- Agent utilization tracking

## API Endpoints

### Configuration
- `GET /callkaro-config/` - Configuration page
- `POST /save-callkaro-config/` - Save API configuration
- `POST /add-callkaro-agent/` - Add new AI agent

### Calling
- `POST /initiate-callkaro-call/` - Initiate AI call
- `POST /create-callkaro-campaign/` - Create campaign
- `POST /schedule-campaign-call/` - Schedule campaign call

### Data
- `GET /callkaro-agents-api/` - Get available agents
- `GET /callkaro-dashboard/` - Dashboard view
- `POST /callkaro-webhook/` - Webhook for status updates

## Database Models

### CallKaroConfig
- API key and default agent configuration
- System-wide settings for Call Karo AI

### CallKaroAgent
- AI agent definitions with IDs and names
- Team member assignments
- Agent descriptions and status

### CallKaroCampaign
- Batch call campaign management
- Agent assignments and statistics
- Campaign status tracking

### CallKaroCallLog
- Individual call records
- Lead associations and metadata
- Status tracking and duration logging
- Scheduling parameters

## Setup Instructions

### 1. Environment Variables
Add to your `.env` file:
```
CALLKARO_API_KEY=your_api_key_here
CALLKARO_DEFAULT_AGENT_ID=your_default_agent_id
```

### 2. Database Migration
```bash
python manage.py migrate
```

### 3. Configuration
1. Navigate to `/callkaro-config/`
2. Enter your Call Karo AI API key
3. Set default agent ID
4. Add your AI agents

### 4. Usage
1. Go to the call panel (`/call-panel/`)
2. Select "Call Karo AI (AI Agent)" as provider
3. Choose an AI agent
4. Make calls normally - AI will handle conversations

## Call Flow

### Traditional Acefone Call
1. User initiates call
2. Agent's phone rings first
3. Customer phone rings second
4. Human conversation

### Call Karo AI Call
1. User initiates call
2. AI agent calls customer directly
3. AI handles entire conversation
4. Results logged automatically

## Integration Points

### Lead Management
- AI calls are linked to CRM lead records
- Lead metadata passed to AI agents
- Call outcomes update lead status

### Team Management
- AI agents can be assigned to team members
- Call logs track which team member initiated calls
- Performance metrics per team member

### Analytics Integration
- AI call data included in CRM analytics
- Separate dashboard for AI-specific metrics
- Campaign performance tracking

## Webhook Support

Call Karo AI can send status updates to:
```
POST /callkaro-webhook/
```

Expected payload:
```json
{
  "call_id": "unique_call_id",
  "status": "completed|failed|missed",
  "duration": 120
}
```

## Error Handling

- API failures are logged and displayed to users
- Fallback to traditional calling if AI service unavailable
- Comprehensive error messages for troubleshooting

## Security Considerations

- API keys stored securely in database
- CSRF protection on all endpoints
- Team member authentication required
- Admin-only configuration access

## Future Enhancements

1. **Real-time Call Monitoring**
   - Live call status updates
   - Call recording integration
   - Real-time transcription

2. **Advanced Analytics**
   - AI conversation analysis
   - Lead scoring based on AI interactions
   - Performance comparisons between agents

3. **Workflow Integration**
   - Automatic follow-up scheduling
   - CRM status updates based on AI outcomes
   - Integration with WhatsApp messaging

4. **Campaign Automation**
   - Scheduled bulk campaigns
   - Lead filtering and segmentation
   - Automated retry logic

## Support

For issues or questions regarding the Call Karo AI integration:

1. Check the configuration at `/callkaro-config/`
2. Review call logs in `/callkaro-dashboard/`
3. Verify API key and agent settings
4. Check Django admin for detailed logs

## API Documentation Reference

The integration follows the official Call Karo AI API documentation:
- Outbound Call API
- Campaign API (v1 and v2)
- Webhook specifications

All API calls include proper error handling and logging for debugging purposes.