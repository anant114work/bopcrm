# WhatsApp Campaign Selector Update

## Changes Made

### 1. Updated WhatsApp Template (`leads/templates/leads/whatsapp.html`)
- Added campaign type selector buttons
- Two buttons to create campaigns:
  - "Create Gaur Yamuna Campaign" button
  - "Create SPJ 10-Day Campaign" button
- Added JavaScript function `createCampaign(type)` to handle campaign creation
- Updated radio button to trigger `updateButtons()` on change

### 2. Updated Drip Campaign Views (`leads/drip_campaign_views.py`)
- Modified `create_gaur_yamuna_campaign()` to return JSON for AJAX requests
- Modified `create_spj_10day_campaigns()` to return JSON for AJAX requests
- Added try-except blocks for error handling
- Both functions now support both regular form submission and AJAX calls

## Features

### Campaign Creation
Users can now:
1. Click "Create Gaur Yamuna Campaign" to create a 9-day Gaur Yamuna follow-up sequence
2. Click "Create SPJ 10-Day Campaign" to create 10 SPJ day campaigns with variant support
3. See confirmation dialogs before creating campaigns
4. Get success/error messages after campaign creation
5. Page automatically reloads to show the new campaigns

### Campaign Selection
After creation, users can:
1. See all available drip campaigns in the list
2. Select a campaign using radio buttons
3. Select leads from the table
4. Click "Start Drip Campaign" to subscribe selected leads

## How It Works

1. User clicks a "Create" button
2. JavaScript shows confirmation dialog
3. If confirmed, sends POST request to appropriate endpoint:
   - `/drip-campaigns/create-gaur-yamuna/` for Gaur Yamuna
   - `/drip-campaigns/create-spj-10day/` for SPJ
4. Backend creates the campaign and returns JSON response
5. Frontend shows success/error message
6. Page reloads to display the new campaign in the list

## Testing

To test:
1. Go to WhatsApp page: http://localhost:8000/whatsapp/
2. Click "Create Gaur Yamuna Campaign" - should create 9-day campaign
3. Click "Create SPJ 10-Day Campaign" - should create 10 day campaigns
4. Select a campaign from the list
5. Select leads from the table
6. Click "Start Drip Campaign" to subscribe leads

## URLs Used

- `/drip-campaigns/create-gaur-yamuna/` - Create Gaur Yamuna campaign
- `/drip-campaigns/create-spj-10day/` - Create SPJ 10-day campaigns
- `/drip-campaigns/bulk-subscribe/` - Subscribe leads to campaign
