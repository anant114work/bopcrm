# WhatsApp Drip Campaigns System

A comprehensive WhatsApp drip campaign system for the Gaur Yamuna project, integrated with AI Sensy API for automated message delivery.

## Features

- **Automated Message Sequences**: 5-day follow-up sequence for Gaur Yamuna leads
- **AI Sensy Integration**: Direct integration with AI Sensy WhatsApp API
- **Lead Subscription Management**: Easy lead subscription and unsubscription
- **Message Scheduling**: Automatic message scheduling with customizable delays
- **Analytics Dashboard**: Comprehensive analytics and reporting
- **Test Functionality**: Built-in testing for individual messages
- **Management Commands**: Automated processing via Django management commands

## Campaign Structure

### Gaur Yamuna 5-Day Sequence

1. **Day 1 - Welcome Message** (Immediate)
   - Template: `gauryaumana_final`
   - Message: Welcome and assistance offer
   - Delay: 0 hours (immediate)

2. **Day 2 - Location Benefits** (+24 hours)
   - Template: `gauryaumana_maybelater`
   - Message: Yamuna Expressway and airport benefits
   - Delay: 24 hours

3. **Day 3 - Payment Plan** (+24 hours)
   - Template: `gauryaumana_later_2`
   - Message: 20-20-20-20-20 Smart Payment Plan
   - Delay: 24 hours

4. **Day 4 - Pricing Advantage** (+24 hours)
   - Template: `gauryaumana_later_3`
   - Message: 30% price advantage
   - Delay: 24 hours

5. **Day 5 - Project Features** (+24 hours)
   - Template: `gauryaumana_maybelater4`
   - Message: Corner units and architectural highlights
   - Delay: 24 hours

## Setup Instructions

### 1. Database Migration

```bash
cd d:\AI-proto\CRM\drip
python manage.py makemigrations leads --name add_drip_campaigns
python manage.py migrate
```

### 2. Create Campaign

1. Access the drip campaigns dashboard: `http://localhost:8000/drip-campaigns/`
2. Click "Create Gaur Yamuna Campaign"
3. This will automatically create the 5-message sequence

### 3. Subscribe Leads

**Via Web Interface:**
1. Go to drip campaigns dashboard
2. Click "Subscribe Lead" on the campaign
3. Enter Lead ID

**Via API:**
```javascript
fetch('/drip-campaigns/subscribe-lead/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
    },
    body: JSON.stringify({
        lead_id: leadId,
        campaign_id: campaignId
    })
})
```

### 4. Process Messages

**Manual Processing:**
- Click "Process Pending Messages" in the dashboard

**Automated Processing:**
```bash
# One-time processing
python manage.py process_drip_messages

# Continuous processing (runs every 60 seconds)
python manage.py process_drip_messages --continuous
```

## API Configuration

The system uses AI Sensy API with the following configuration:

```python
AISENSY_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
AISENSY_API_URL = "https://backend.aisensy.com/campaign/t1/api/v2"
```

### Message Payload Structure

```json
{
    "apiKey": "your_api_key",
    "campaignName": "gauryaumana_final",
    "destination": "919999999999",
    "userName": "User Name",
    "templateParams": ["User Name"],
    "source": "drip-campaign",
    "media": {},
    "buttons": [],
    "carouselCards": [],
    "location": {},
    "attributes": {
        "drip_campaign": "Gaur Yamuna Follow-up Sequence",
        "day_number": 1
    },
    "paramsFallbackValue": {
        "FirstName": "user"
    }
}
```

## Database Models

### DripCampaign
- Campaign management and configuration
- Status tracking (active, paused, completed, draft)
- Analytics aggregation

### DripMessage
- Individual message templates
- Day sequencing and timing
- AI Sensy template mapping

### DripSubscriber
- Lead subscription management
- Progress tracking
- Status management

### DripMessageLog
- Message delivery tracking
- API response logging
- Error handling

## URL Endpoints

```python
# Dashboard
/drip-campaigns/

# Create Gaur Yamuna Campaign
/drip-campaigns/create-gaur-yamuna/

# Campaign Detail
/drip-campaigns/<campaign_id>/

# Subscribe Lead (API)
/drip-campaigns/subscribe-lead/

# Process Pending Messages (API)
/drip-campaigns/process-pending/

# Test Message (API)
/drip-campaigns/test-message/

# Analytics
/drip-campaigns/analytics/
```

## Testing

### Test Script
```bash
python test_drip_campaign.py
```

### Manual Testing
1. Create test leads with phone numbers: 919999999999, 918888888888
2. Subscribe leads to campaign
3. Test individual messages
4. Monitor message logs

### Test Message
```javascript
fetch('/drip-campaigns/test-message/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
    },
    body: JSON.stringify({
        message_id: messageId,
        test_phone: '919999999999',
        test_name: 'Test User'
    })
})
```

## Analytics & Monitoring

### Campaign Analytics
- Total subscribers
- Active vs completed subscribers
- Message delivery rates
- Success/failure rates

### Message Analytics
- Individual message performance
- Delivery timestamps
- Error tracking
- API response logging

### Dashboard Features
- Real-time status updates
- Subscriber management
- Message scheduling overview
- Performance metrics

## Automation

### Continuous Processing
Set up continuous message processing:

```bash
# Run in background
nohup python manage.py process_drip_messages --continuous &

# Or use supervisor/systemd for production
```

### Cron Job (Alternative)
```bash
# Add to crontab for every 5 minutes
*/5 * * * * cd /path/to/project && python manage.py process_drip_messages
```

## Error Handling

- API failures are logged with full error details
- Failed messages can be retried
- Subscriber status is updated based on delivery success
- Comprehensive error logging for debugging

## Security

- CSRF protection on all API endpoints
- Input validation and sanitization
- Phone number format validation
- API key security (stored in environment variables recommended)

## Production Considerations

1. **Environment Variables**: Move API keys to environment variables
2. **Background Tasks**: Use Celery for message processing in production
3. **Rate Limiting**: Implement rate limiting for API calls
4. **Monitoring**: Set up monitoring for message delivery rates
5. **Backup**: Regular backup of campaign data and logs

## Troubleshooting

### Common Issues

1. **Messages not sending**
   - Check AI Sensy API key validity
   - Verify phone number format (91xxxxxxxxxx)
   - Check campaign status (must be 'active')

2. **Subscribers not progressing**
   - Ensure `process_pending_messages` is running
   - Check `next_message_at` timestamps
   - Verify message scheduling logic

3. **API errors**
   - Check AI Sensy API status
   - Verify template names match exactly
   - Check parameter mapping

### Debug Commands

```bash
# Check pending messages
python manage.py shell
>>> from leads.drip_campaign_models import DripSubscriber
>>> DripSubscriber.objects.filter(status='active', next_message_at__lte=timezone.now())

# Check message logs
>>> from leads.drip_campaign_models import DripMessageLog
>>> DripMessageLog.objects.filter(status='failed').order_by('-created_at')[:5]
```

## Support

For issues or questions:
1. Check the Django admin interface for detailed logs
2. Review the `DripMessageLog` model for API responses
3. Test individual messages using the test functionality
4. Monitor the analytics dashboard for performance insights