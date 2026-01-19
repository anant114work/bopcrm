# Click-to-Call Integration Setup Guide

## Quick Setup (5 minutes)

### 1. Add your API token to environment
```bash
# Add to your .env file
ACEFONE_CLICK_API_BASE=https://api.acefone.in
ACEFONE_CLICK_API_TOKEN=your_click_to_call_support_api_token_here
```

### 2. Run database migrations
```bash
python manage.py makemigrations leads
python manage.py migrate
```

### 3. Setup API tokens for agents
```bash
# For global token (all agents use same token)
python manage.py setup_click_tokens --token YOUR_API_TOKEN --global

# For specific agent
python manage.py setup_click_tokens --token YOUR_API_TOKEN --agent-email agent@company.com
```

### 4. Access the dialer
Navigate to: `http://127.0.0.1:8002/call-panel/`

## Features Available

### ✅ Complete Click-to-Call Dialer
- **Lead Search**: Type name/phone to find leads instantly
- **Manual Dialer**: Call any number directly
- **Lead Queue**: Auto-loaded leads based on assignment
- **Call Status**: Real-time call tracking with timer
- **Call History**: Recent calls with status and duration
- **Performance Stats**: Today's call metrics

### ✅ Smart Features
- **Quick Actions**: Recent leads, overdue leads, hot leads
- **Keyboard Shortcuts**: Ctrl+Enter to call, Escape to end
- **Auto-refresh**: Stats and history update automatically
- **Responsive Design**: Works on desktop and mobile

### ✅ Call Management
- **Status Tracking**: Initiating → Ringing → Answered → Completed
- **Call Timer**: Real-time duration tracking
- **Call Logging**: All calls saved to database
- **Error Handling**: Clear error messages and retry logic

## API Endpoints Created

- `POST /initiate-click-call/` - Start a call
- `GET /dialer-search/?q=query` - Search leads
- `GET /lead-queue-api/?filter=type` - Get lead queue
- `GET /call-history-api/` - Get call history
- `GET /call-stats-api/` - Get performance stats
- `POST /webhook/acefone/call-status/` - Webhook for status updates

## Configuration Options

### Environment Variables
```bash
ACEFONE_CLICK_API_BASE=https://api.acefone.in  # API base URL
ACEFONE_CLICK_API_TOKEN=your_token              # Global API token
```

### Per-Agent Tokens
Use Django admin or management command to assign different tokens per agent.

### Webhook Setup (Optional)
Configure webhook URL in Acefone dashboard:
```
https://yourdomain.com/webhook/acefone/call-status/
```

## Testing

### 1. Test with Postman
```bash
POST /initiate-click-call/
Content-Type: application/json

{
    "phone": "+919876543210",
    "lead_name": "Test Call"
}
```

### 2. Test the dialer
1. Go to `/call-panel/`
2. Enter a phone number
3. Click "Call"
4. Check call status updates

## Troubleshooting

### Common Issues

**"No click-to-call token assigned"**
- Run: `python manage.py setup_click_tokens --token YOUR_TOKEN --global`

**"Call failed: Network error"**
- Check your API token is valid
- Verify ACEFONE_CLICK_API_BASE URL
- Check internet connection

**"No leads in queue"**
- Ensure leads are assigned to your team member
- Check lead assignment in admin panel

### Debug Mode
Add to your views for debugging:
```python
print(f"API Token: {api_key_entry.api_token[:10]}...")
print(f"Calling: {phone}")
```

## Production Deployment

### 1. Security
- Store API tokens in environment variables
- Use HTTPS for all endpoints
- Validate webhook signatures

### 2. Performance
- Add Redis for caching call status
- Use Celery for background call processing
- Monitor API rate limits

### 3. Monitoring
- Log all API calls and responses
- Set up alerts for failed calls
- Track call success rates

## Support

For issues with:
- **Acefone API**: Check Acefone documentation
- **Django Integration**: Check Django logs
- **Frontend Issues**: Check browser console

The dialer is now ready to use! 🎉