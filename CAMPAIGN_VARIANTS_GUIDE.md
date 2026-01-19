# Campaign Variant System - Implementation Guide

## Overview

The Campaign Variant System allows you to create multiple versions of a drip campaign and switch between them without affecting existing subscribers. This is perfect for A/B testing different messaging strategies or managing multiple campaign versions.

## Features

✅ **Multiple Variants**: Create 10+ campaign variants (e.g., SPJ Day 1-10)
✅ **Easy Switching**: Switch active variant with one click
✅ **Existing Subscribers Unaffected**: Current subscribers keep their campaign
✅ **New Subscribers Use Active**: New subscribers automatically get the active variant
✅ **Independent Tracking**: Each variant tracks its own metrics
✅ **Same Logic**: All variants use the same drip message logic

## Database Changes

### New Fields in DripCampaign Model

```python
variant_group = models.CharField(max_length=100, blank=True)
# Example: 'spjday', 'gaur_yamuna'

is_active_variant = models.BooleanField(default=True)
# Whether this variant is currently active for new subscribers
```

## API Endpoints

### 1. Switch Campaign Variant
**POST** `/drip-campaigns/switch-variant/`

```json
{
  "variant_group": "spjday",
  "active_campaign_id": 5
}
```

**Response:**
```json
{
  "success": true,
  "message": "Switched to SPJ Day 5",
  "active_campaign": "SPJ Day 5"
}
```

### 2. Get Campaign Variants
**GET** `/drip-campaigns/get-variants/?variant_group=spjday`

**Response:**
```json
{
  "success": true,
  "variants": [
    {
      "id": 1,
      "name": "SPJ Day 1",
      "is_active": true,
      "subscribers": 150,
      "messages_sent": 450
    },
    {
      "id": 2,
      "name": "SPJ Day 2",
      "is_active": false,
      "subscribers": 0,
      "messages_sent": 0
    }
  ],
  "active_campaign_id": 1,
  "active_campaign_name": "SPJ Day 1"
}
```

### 3. Create SPJ 10-Day Campaigns
**POST** `/drip-campaigns/create-spj-10day/`

Creates 10 campaign variants automatically:
- SPJ Day 1 through SPJ Day 10
- All grouped under `variant_group='spjday'`
- Only Day 1 is active by default
- Each has its own message template

## Usage Workflow

### Step 1: Create Campaign Variants

Navigate to: `/drip-campaigns/create-spj-10day/`

Click "Create SPJ 10-Day Campaigns" to generate all 10 variants.

### Step 2: Subscribe Leads to Active Campaign

When you subscribe leads, they automatically get the currently active variant:

```python
# Leads will be subscribed to the active variant
subscriber = DripSubscriber.objects.create(
    campaign=active_campaign,  # This is the active variant
    lead=lead,
    phone_number=lead.phone_number,
    first_name=lead.full_name,
    status='active'
)
```

### Step 3: Switch Between Variants

Use the Campaign Variant Switcher UI or API:

```javascript
// Switch to Day 5
fetch('/drip-campaigns/switch-variant/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({
        variant_group: 'spjday',
        active_campaign_id: 5
    })
})
```

### Step 4: Monitor Each Variant

Each variant tracks:
- Number of subscribers
- Messages sent
- Delivery status
- Failure rates

## Implementation Details

### How Variant Switching Works

1. **Deactivate All**: All variants in the group are set to `is_active_variant=False`
2. **Activate Selected**: The selected variant is set to `is_active_variant=True`
3. **New Subscribers**: Use the active variant
4. **Existing Subscribers**: Unaffected - continue with their current campaign

### Subscriber Assignment Logic

```python
# When subscribing a lead
active_campaign = DripCampaign.objects.filter(
    variant_group='spjday',
    is_active_variant=True
).first()

subscriber = DripSubscriber.objects.create(
    campaign=active_campaign,  # Gets the active variant
    lead=lead,
    ...
)
```

## SPJ 10-Day Campaign Structure

Each campaign variant contains:
- **Campaign Name**: SPJ Day 1-10
- **Variant Group**: spjday
- **Messages**: 1 message per variant (Day 1 message, Day 2 message, etc.)
- **Destinations**:
  - Days 1-7, 9-10: 919999929832
  - Day 8: 919169739813

## Frontend Integration

### Campaign Variant Switcher Component

Include in your dashboard:

```html
{% include 'leads/campaign_variant_switcher.html' %}
```

Features:
- Dropdown to select campaign group
- Radio buttons to select variant
- Shows active variant
- Shows subscriber count and messages sent
- One-click switching

## Example: SPJ Campaign Setup

### Create Campaigns
```bash
# Navigate to /drip-campaigns/create-spj-10day/
# Click "Create SPJ 10-Day Campaigns"
```

### Subscribe Leads
```python
# Leads are automatically subscribed to active variant (Day 1)
campaign = DripCampaign.objects.get(name='SPJ Day 1', is_active_variant=True)
subscriber = DripSubscriber.objects.create(
    campaign=campaign,
    lead=lead,
    phone_number=lead.phone_number,
    first_name=lead.full_name
)
```

### Switch to Day 5
```javascript
// Use the variant switcher UI or API
fetch('/drip-campaigns/switch-variant/', {
    method: 'POST',
    body: JSON.stringify({
        variant_group: 'spjday',
        active_campaign_id: 5  // SPJ Day 5
    })
})
```

### New Leads Get Day 5
```python
# New subscribers now get Day 5 campaign
campaign = DripCampaign.objects.get(name='SPJ Day 5', is_active_variant=True)
# New subscriber gets Day 5
```

## Migration Steps

1. **Run Migration**:
   ```bash
   python manage.py migrate leads 0044_add_campaign_variants
   ```

2. **Create Campaigns**:
   - Navigate to `/drip-campaigns/create-spj-10day/`
   - Click create button

3. **Update Dashboard**:
   - Add variant switcher component to drip campaigns dashboard
   - Include `campaign_variant_switcher.html` template

4. **Test**:
   - Subscribe test leads
   - Switch variants
   - Verify new subscribers get active variant

## Troubleshooting

### Issue: Variant switcher not showing
**Solution**: Ensure `campaign_variant_switcher.html` is included in your template

### Issue: New subscribers getting wrong campaign
**Solution**: Check that `is_active_variant=True` is set correctly on the active campaign

### Issue: Existing subscribers affected by switch
**Solution**: This shouldn't happen - verify that existing subscribers have their campaign_id set correctly

## Best Practices

1. **Test Before Switching**: Always test a variant before making it active
2. **Monitor Metrics**: Track performance of each variant
3. **Document Changes**: Keep notes on why you switched variants
4. **Gradual Rollout**: Consider subscribing small batches to new variants first
5. **Backup Data**: Export subscriber data before major changes

## Future Enhancements

- [ ] A/B testing analytics
- [ ] Automatic variant switching based on performance
- [ ] Variant cloning
- [ ] Scheduled variant switches
- [ ] Variant performance comparison dashboard
