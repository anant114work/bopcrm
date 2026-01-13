# Campaign Variant System - Implementation Summary

## What Was Added

### 1. Database Model Changes
**File**: `leads/drip_campaign_models.py`

Added two new fields to `DripCampaign` model:
- `variant_group`: Groups related campaign variants (e.g., 'spjday')
- `is_active_variant`: Boolean flag for the currently active variant

### 2. New Views/API Endpoints
**File**: `leads/drip_campaign_views.py`

Three new functions added:

#### `switch_campaign_variant(request)`
- Switches between campaign variants
- Deactivates all variants in a group, activates the selected one
- POST endpoint: `/drip-campaigns/switch-variant/`

#### `get_campaign_variants(request)`
- Retrieves all variants for a campaign group
- Shows which is active, subscriber count, messages sent
- GET endpoint: `/drip-campaigns/get-variants/`

#### `create_spj_10day_campaigns(request)`
- Creates 10 SPJ day campaign variants (Day 1-10)
- Each variant is independent but grouped
- POST endpoint: `/drip-campaigns/create-spj-10day/`

### 3. URL Routes
**File**: `leads/urls.py`

Added three new URL patterns:
```python
path('drip-campaigns/switch-variant/', drip_views.switch_campaign_variant, name='switch_campaign_variant'),
path('drip-campaigns/get-variants/', drip_views.get_campaign_variants, name='get_campaign_variants'),
path('drip-campaigns/create-spj-10day/', drip_views.create_spj_10day_campaigns, name='create_spj_10day_campaigns'),
```

### 4. Database Migration
**File**: `leads/migrations/0044_add_campaign_variants.py`

Migration to add the two new fields to DripCampaign table.

### 5. Frontend Templates

#### Campaign Variant Switcher
**File**: `leads/templates/leads/campaign_variant_switcher.html`

Interactive UI component featuring:
- Dropdown to select campaign group
- Radio buttons to select variant
- Shows active variant with badge
- Displays subscriber count and messages sent
- One-click switching with confirmation

#### SPJ Campaign Creation
**File**: `leads/templates/leads/create_spj_campaigns.html`

Setup page for creating 10-day campaigns:
- Explains the variant system
- Shows campaign configuration
- Confirmation checkbox
- Progress indicator

### 6. Documentation
**File**: `CAMPAIGN_VARIANTS_GUIDE.md`

Comprehensive guide covering:
- System overview and features
- Database changes
- API endpoints with examples
- Usage workflow
- Implementation details
- SPJ campaign structure
- Frontend integration
- Troubleshooting
- Best practices

## How It Works

### Campaign Variant System Flow

```
1. Create Campaigns
   └─ 10 variants created (SPJ Day 1-10)
   └─ All grouped under 'spjday'
   └─ Only Day 1 is active by default

2. Subscribe Leads
   └─ Leads get the ACTIVE variant
   └─ Currently: SPJ Day 1

3. Switch Variant
   └─ Select SPJ Day 5
   └─ Day 5 becomes active
   └─ Day 1 becomes inactive

4. New Subscribers
   └─ Get SPJ Day 5 (the new active variant)

5. Existing Subscribers
   └─ Keep SPJ Day 1 (unaffected)
   └─ Continue receiving their messages
```

## Key Features

✅ **Multiple Variants**: Create 10+ campaign versions
✅ **Easy Switching**: One-click variant switching
✅ **Existing Subscribers Protected**: Current subscribers unaffected
✅ **New Subscribers Use Active**: Automatic assignment to active variant
✅ **Independent Tracking**: Each variant has its own metrics
✅ **Same Logic**: All variants use existing drip message system

## Usage Steps

### Step 1: Run Migration
```bash
python manage.py migrate leads 0044_add_campaign_variants
```

### Step 2: Create Campaigns
Navigate to: `/drip-campaigns/create-spj-10day/`
Click: "Create SPJ 10-Day Campaigns"

### Step 3: Subscribe Leads
Leads are automatically subscribed to the active variant (Day 1)

### Step 4: Switch Variants
Use the Campaign Variant Switcher UI to switch between Day 1-10

### Step 5: Monitor
Each variant tracks its own:
- Subscriber count
- Messages sent
- Delivery status
- Failure rates

## SPJ 10-Day Campaign Details

**Campaign Structure**:
- 10 independent campaigns
- Grouped under `variant_group='spjday'`
- Each has one message template
- Destinations vary by day:
  - Days 1-7, 9-10: 919999929832
  - Day 8: 919169739813

**Active by Default**: Day 1

**Switching**: Use variant switcher to change active campaign

## API Examples

### Switch to Day 5
```bash
curl -X POST http://localhost:3000/drip-campaigns/switch-variant/ \
  -H "Content-Type: application/json" \
  -d '{
    "variant_group": "spjday",
    "active_campaign_id": 5
  }'
```

### Get All Variants
```bash
curl http://localhost:3000/drip-campaigns/get-variants/?variant_group=spjday
```

### Create Campaigns
```bash
curl -X POST http://localhost:3000/drip-campaigns/create-spj-10day/
```

## Files Modified/Created

### Modified Files
- `leads/drip_campaign_models.py` - Added variant fields
- `leads/drip_campaign_views.py` - Added 3 new views
- `leads/urls.py` - Added 3 new URL routes

### New Files
- `leads/migrations/0044_add_campaign_variants.py` - Database migration
- `leads/templates/leads/campaign_variant_switcher.html` - Switcher UI
- `leads/templates/leads/create_spj_campaigns.html` - Creation UI
- `CAMPAIGN_VARIANTS_GUIDE.md` - Comprehensive guide

## Integration with Existing System

The variant system integrates seamlessly with existing drip campaign logic:

1. **Subscriber Assignment**: Uses existing `DripSubscriber` model
2. **Message Sending**: Uses existing `send_drip_message()` function
3. **Auto-Sender**: Works with existing auto-sender
4. **Analytics**: Tracks metrics per variant
5. **Unsubscribe**: Works as before

## Next Steps

1. Run the migration
2. Create the SPJ 10-day campaigns
3. Add variant switcher to dashboard
4. Subscribe leads to active campaign
5. Test switching between variants
6. Monitor performance of each variant

## Support

For issues or questions, refer to:
- `CAMPAIGN_VARIANTS_GUIDE.md` - Detailed documentation
- API endpoints documentation in guide
- Troubleshooting section in guide
