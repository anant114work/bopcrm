# Automatic WhatsApp Campaign Setup

## Overview
Automatically send WhatsApp messages to new leads when they are added to your CRM. No manual intervention needed!

## How It Works

1. **Configure Auto Campaign**: Set up which WhatsApp template to send for each project
2. **Lead Added**: When a new lead is synced/added to the CRM
3. **Auto Detection**: System detects which project the lead belongs to (via form mapping)
4. **Auto Send**: WhatsApp message is sent automatically using the configured template
5. **Tracking**: Message delivery is logged in the system

## Setup Instructions

### Step 1: Run Migration
```bash
python manage.py migrate
```

### Step 2: Configure Auto Campaigns

1. Go to **Auto WhatsApp** page: `/auto-whatsapp/`
2. Click **"+ Create Auto Campaign"**
3. Select:
   - **Project**: Which project to apply this to
   - **WhatsApp Template**: Which template to send
   - **Delay**: How long to wait before sending (0 = immediate)
4. Click **"Create"**

### Step 3: Test It

1. Add a new lead (or sync from Meta)
2. Check the lead has a phone number
3. Check the lead's form name matches a project (via form mapping)
4. WhatsApp message will be sent automatically!

## Configuration Page

### Access
- URL: `/auto-whatsapp/`
- Menu: Add link to sidebar navigation

### Features
- ✅ Create auto campaigns
- ✅ View all configured campaigns
- ✅ Enable/Disable campaigns
- ✅ Delete campaigns
- ✅ Set delay before sending

## How Leads Are Matched to Projects

The system uses **Form Source Mapping** to determine which project a lead belongs to:

1. Lead has `form_name` field (e.g., "Gaur Yamuna City - Contact Form")
2. Form mapping links form names to projects
3. Auto campaign is triggered for that project's template

**Example:**
- Form: "Gaur Yamuna City - Contact Form"
- Mapped to: Project "Gaur Yamuna City"
- Auto Campaign: Send "Welcome Template" immediately
- Result: New lead gets WhatsApp automatically!

## Features

### Immediate Sending
- Set delay to **0 minutes**
- Message sent as soon as lead is created
- Perfect for welcome messages

### Delayed Sending
- Set delay to any number of minutes
- Example: Send follow-up after 30 minutes
- Useful for drip campaigns

### Smart Duplicate Prevention
- Won't send same template twice to same lead
- Checks message history before sending
- Prevents spam

### Automatic Phone Formatting
- Adds +91 prefix automatically
- Removes duplicate country codes
- Ensures proper delivery

### Project Image Attachment
- Randomly selects from project images
- Attaches to WhatsApp message
- Makes messages more engaging

## Technical Details

### New Files Created
1. **auto_whatsapp_models.py** - Database model
2. **auto_whatsapp_service.py** - Sending logic
3. **auto_whatsapp_views.py** - Web interface
4. **auto_whatsapp_config.html** - Configuration page
5. **migrations/0035_auto_whatsapp_campaign.py** - Database migration

### Modified Files
1. **signals.py** - Added trigger on lead creation
2. **models.py** - Imported new model
3. **urls.py** - Added new routes

### Database Schema
```python
AutoWhatsAppCampaign:
  - project (ForeignKey to Project)
  - template (ForeignKey to WhatsAppTemplate)
  - is_active (Boolean)
  - delay_minutes (Integer)
  - created_at (DateTime)
```

### Signal Flow
```
New Lead Created
    ↓
Signal: post_save (Lead)
    ↓
trigger_auto_campaigns_for_lead()
    ↓
Get project from form mapping
    ↓
Find active auto campaigns
    ↓
send_auto_whatsapp_to_lead()
    ↓
Check if already sent
    ↓
Build WhatsApp payload
    ↓
Send via AISensy API
    ↓
Log message in database
```

## API Endpoints

### Configuration Page
- `GET /auto-whatsapp/` - View all campaigns

### Campaign Management
- `POST /auto-whatsapp/create/` - Create new campaign
- `POST /auto-whatsapp/{id}/toggle/` - Enable/disable campaign
- `POST /auto-whatsapp/{id}/delete/` - Delete campaign

### Helper
- `GET /auto-whatsapp/project-templates/{project_id}/` - Get templates for project

## Example Configurations

### Welcome Message (Immediate)
```
Project: Gaur Yamuna City
Template: Welcome Message
Delay: 0 minutes
Status: Active
```
**Result**: New leads get welcome message instantly

### Follow-up (Delayed)
```
Project: Gaur Yamuna City
Template: Follow-up Reminder
Delay: 30 minutes
Status: Active
```
**Result**: New leads get follow-up after 30 minutes

### Multiple Campaigns
You can have multiple auto campaigns per project:
- Campaign 1: Welcome (0 min)
- Campaign 2: Project Details (5 min)
- Campaign 3: Pricing Info (30 min)

## Monitoring

### Check if Message Was Sent
1. Go to lead detail page
2. Check WhatsApp messages section
3. See delivery status (sent/failed)

### View All Auto Campaigns
1. Go to `/auto-whatsapp/`
2. See all configured campaigns
3. Check active/inactive status

### Logs
Check console output for:
```
Auto WhatsApp sent for NEW lead John Doe: 1 messages
```

## Troubleshooting

### Message Not Sent?
- ✅ Check lead has phone number
- ✅ Check form name is mapped to project
- ✅ Check auto campaign is active
- ✅ Check template exists for project
- ✅ Check AISensy API is configured

### Duplicate Messages?
- System prevents duplicates automatically
- Checks if template already sent to lead
- Won't send same template twice

### Wrong Project?
- Check form source mapping
- Ensure form name matches correctly
- Update mapping if needed

## Best Practices

1. **Start with One Campaign**
   - Test with one project first
   - Verify messages are sent correctly
   - Then expand to other projects

2. **Use Immediate for Welcome**
   - Set delay to 0 for welcome messages
   - Engage leads quickly

3. **Use Delays for Follow-ups**
   - Space out messages
   - Don't overwhelm leads

4. **Monitor Delivery**
   - Check message logs regularly
   - Fix failed deliveries

5. **Update Templates**
   - Keep messages fresh
   - Test before activating

## Benefits

✅ **Save Time**: No manual sending needed
✅ **Instant Engagement**: Welcome leads immediately  
✅ **Consistent**: Every lead gets same treatment
✅ **Scalable**: Works for 1 or 1000 leads per day
✅ **Trackable**: All messages logged
✅ **Flexible**: Configure per project
✅ **Smart**: Prevents duplicates automatically

## Next Steps

1. Run migration: `python manage.py migrate`
2. Go to `/auto-whatsapp/`
3. Create your first auto campaign
4. Test with a new lead
5. Monitor results
6. Expand to more projects!
