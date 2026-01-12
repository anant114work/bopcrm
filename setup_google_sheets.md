# Google Sheets Integration Setup

## Step 1: Create Google Apps Script

1. Go to https://script.google.com/
2. Click "New Project"
3. Replace the default code with the content from `google_apps_script.js`
4. Save the project (name it "Lead Sync")

## Step 2: Deploy as Web App

1. Click "Deploy" > "New Deployment"
2. Choose "Web app" as type
3. Set "Execute as" to "Me"
4. Set "Who has access" to "Anyone"
5. Click "Deploy"
6. Copy the Web App URL

## Step 3: Update Django Code

1. Open `leads/google_sheets.py`
2. Replace `YOUR_SCRIPT_ID` with your Web App URL
3. Update the webhook_url variable

## Step 4: Test Integration

1. Run Django sync: Click "Sync New Leads"
2. Check your Google Sheet for new entries
3. Verify data is being added correctly

## Alternative: Direct API Integration

For production, consider using Google Sheets API with service account:

1. Create service account in Google Cloud Console
2. Download credentials JSON
3. Share spreadsheet with service account email
4. Use gspread library for direct API access

## Current Setup

- **Spreadsheet ID**: 1l2kVvwhafObJ1FObVjLfL3L6DkBx8_oTsWT1z705_a0
- **Sheet Name**: Sheet1
- **Integration**: Webhook via Google Apps Script

## Data Fields Synced

- Lead ID
- Full Name  
- Email
- Phone Number
- City
- Budget
- Configuration
- Preferred Time
- Form Name
- Created Time