# Campaign Variant System - Quick Start

## 5-Minute Setup

### 1. Apply Database Migration
```bash
python manage.py migrate leads 0044_add_campaign_variants
```

### 2. Create SPJ 10-Day Campaigns
Navigate to: `http://localhost:3000/drip-campaigns/create-spj-10day/`

Click: **"Create SPJ 10-Day Campaigns"**

This creates:
- SPJ Day 1 (Active by default)
- SPJ Day 2
- SPJ Day 3
- ... through SPJ Day 10

### 3. Subscribe Leads
Leads are automatically subscribed to the **active variant** (currently Day 1)

### 4. Switch Between Campaigns
Use the Campaign Variant Switcher to change which day is active:

**Option A: UI**
- Go to Drip Campaigns Dashboard
- Use the variant switcher dropdown
- Select a different day
- Click "Switch to Selected Campaign"

**Option B: API**
```bash
curl -X POST http://localhost:3000/drip-campaigns/switch-variant/ \
  -H "Content-Type: application/json" \
  -d '{
    "variant_group": "spjday",
    "active_campaign_id": 5
  }'
```

### 5. New Subscribers Get Active Campaign
When you switch to Day 5, new subscribers will automatically get Day 5 messages.

Existing subscribers keep their current campaign and continue receiving messages.

## What Each Day Contains

| Day | Destination | Status |
|-----|-------------|--------|
| 1 | 919999929832 | Active (default) |
| 2 | 919999929832 | Inactive |
| 3 | 919999929832 | Inactive |
| 4 | 919999929832 | Inactive |
| 5 | 919999929832 | Inactive |
| 6 | 919999929832 | Inactive |
| 7 | 919999929832 | Inactive |
| 8 | 919169739813 | Inactive |
| 9 | 919999929832 | Inactive |
| 10 | 919999929832 | Inactive |

## Key Points

✅ **Only one variant is active** - New subscribers get the active one
✅ **Existing subscribers unaffected** - They keep their current campaign
✅ **Easy switching** - Change active variant anytime
✅ **Independent tracking** - Each variant tracks its own metrics
✅ **Same message logic** - All variants use the same drip system

## Common Tasks

### Switch to Day 5
1. Go to Drip Campaigns Dashboard
2. Select "SPJ Day Campaigns (1-10)" from dropdown
3. Select "SPJ Day 5" radio button
4. Click "Switch to Selected Campaign"
5. ✅ Done! New subscribers now get Day 5

### Check Active Campaign
```bash
curl http://localhost:3000/drip-campaigns/get-variants/?variant_group=spjday
```

Look for `"is_active": true` in the response.

### Subscribe Leads to Active Campaign
```python
# Leads are automatically subscribed to active variant
# No special code needed - existing subscribe logic works
```

### Monitor Variant Performance
Each variant shows:
- Number of subscribers
- Messages sent
- Delivery status
- Failure rates

## Troubleshooting

**Q: New subscribers getting wrong campaign?**
A: Check that the correct variant has `is_active_variant=True`

**Q: Existing subscribers affected?**
A: They shouldn't be - verify their campaign_id is set correctly

**Q: Can't see variant switcher?**
A: Make sure `campaign_variant_switcher.html` is included in your template

## Next Steps

1. ✅ Run migration
2. ✅ Create campaigns
3. ✅ Subscribe leads
4. ✅ Test switching
5. Monitor performance
6. Optimize based on metrics

## Support

- Full guide: `CAMPAIGN_VARIANTS_GUIDE.md`
- Implementation details: `CAMPAIGN_VARIANTS_IMPLEMENTATION.md`
- API docs: See guide for endpoint details

---

**That's it!** You now have a fully functional campaign variant system with 10 SPJ day campaigns that can be switched with one click.
