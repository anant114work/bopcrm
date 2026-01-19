# Campaign Variant System - Getting Started (5 Minutes)

## ✅ System Status: READY

All migrations have been applied. You can start using the system immediately.

## Quick Start (5 Steps)

### Step 1: Create the 10 SPJ Day Campaigns
```
1. Open browser: http://localhost:3000/drip-campaigns/create-spj-10day/
2. Check the confirmation checkbox
3. Click "Create SPJ 10-Day Campaigns"
4. Wait for success message
```

**Result**: 10 campaigns created (SPJ Day 1-10), all grouped together

### Step 2: Subscribe Leads to Active Campaign
```
1. Go to: http://localhost:3000/drip-campaigns/
2. Click on "SPJ Day 1" campaign
3. Click "Bulk Subscribe Leads"
4. Select leads to subscribe
5. Click "Subscribe"
```

**Result**: Leads subscribed to SPJ Day 1 (the active variant)

### Step 3: Switch to a Different Campaign
```
1. Go to: http://localhost:3000/drip-campaigns/
2. Scroll to "Campaign Variant Switcher"
3. Select "SPJ Day Campaigns (1-10)" from dropdown
4. Select "SPJ Day 5" radio button
5. Click "Switch to Selected Campaign"
```

**Result**: SPJ Day 5 is now active

### Step 4: Subscribe More Leads
```
1. Go to: http://localhost:3000/drip-campaigns/
2. Click on "SPJ Day 5" campaign
3. Click "Bulk Subscribe Leads"
4. Select new leads
5. Click "Subscribe"
```

**Result**: New leads subscribed to SPJ Day 5 (the new active variant)

### Step 5: Monitor Performance
```
1. Go to: http://localhost:3000/drip-campaigns/
2. Click on any campaign (e.g., "SPJ Day 1")
3. View:
   - Subscribers count
   - Messages sent
   - Delivery status
   - Failure rates
```

**Result**: See metrics for each variant

## What Happens Behind the Scenes

### When You Switch Variants
- ✅ Old variant becomes inactive
- ✅ New variant becomes active
- ✅ Existing subscribers keep their current campaign
- ✅ New subscribers get the active variant

### Example Flow
```
Day 1: Subscribe 100 leads to SPJ Day 1
       → 100 leads get Day 1 messages

Day 2: Switch to SPJ Day 5
       → Existing 100 leads still get Day 1 messages
       → New subscribers get Day 5 messages

Day 3: Subscribe 50 more leads
       → 50 new leads get Day 5 messages
       → Original 100 still get Day 1 messages
```

## API Endpoints (For Developers)

### Create Campaigns
```bash
POST /drip-campaigns/create-spj-10day/
```

### Get All Variants
```bash
GET /drip-campaigns/get-variants/?variant_group=spjday

Response:
{
  "success": true,
  "variants": [
    {"id": 1, "name": "SPJ Day 1", "is_active": true, "subscribers": 100},
    {"id": 2, "name": "SPJ Day 2", "is_active": false, "subscribers": 0},
    ...
  ],
  "active_campaign_id": 1,
  "active_campaign_name": "SPJ Day 1"
}
```

### Switch Variant
```bash
POST /drip-campaigns/switch-variant/

Body:
{
  "variant_group": "spjday",
  "active_campaign_id": 5
}

Response:
{
  "success": true,
  "message": "Switched to SPJ Day 5",
  "active_campaign": "SPJ Day 5"
}
```

## Troubleshooting

### Q: Where do I find the variant switcher?
A: Go to `/drip-campaigns/` and scroll down to "Campaign Variant Switcher"

### Q: Can I switch variants anytime?
A: Yes! Existing subscribers are unaffected

### Q: What happens to existing subscribers when I switch?
A: They keep their current campaign and continue receiving messages

### Q: How do I know which variant is active?
A: The active variant shows a green "Active" badge in the switcher

### Q: Can I create more variants?
A: Yes! Use the same `variant_group` when creating new campaigns

## Next Steps

1. ✅ Create the 10 SPJ campaigns (Step 1 above)
2. ✅ Subscribe your first batch of leads
3. ✅ Test switching between variants
4. ✅ Monitor performance metrics
5. ✅ Optimize based on results

## Documentation

- **Full Guide**: `CAMPAIGN_VARIANTS_GUIDE.md`
- **Implementation**: `CAMPAIGN_VARIANTS_IMPLEMENTATION.md`
- **Quick Start**: `CAMPAIGN_VARIANTS_QUICKSTART.md`
- **Status**: `CAMPAIGN_VARIANTS_READY.md`

---

**Ready to go!** 🚀

Start with Step 1 above and you'll have the system running in 5 minutes.
