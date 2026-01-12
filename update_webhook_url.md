# Update Google Apps Script Webhook URL

## Step 1: Get your ngrok URL
1. Open a new terminal/command prompt
2. Run: `ngrok http 8000`
3. Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

## Step 2: Update Google Apps Script
1. Open your Google Apps Script project
2. Find this line in the code:
   ```javascript
   CRM_WEBHOOK_URL: 'https://YOUR_NGROK_URL.ngrok.io/webhook/google-leads/',
   ```
3. Replace `YOUR_NGROK_URL` with your actual ngrok subdomain
4. Example:
   ```javascript
   CRM_WEBHOOK_URL: 'https://abc123.ngrok.io/webhook/google-leads/',
   ```
5. Save and redeploy the Google Apps Script

## Step 3: Test the Integration
1. Make sure your Django server is running: `python manage.py runserver`
2. Try the "Sync Google Sheet" button in your CRM
3. Submit a test form to verify new leads come through automatically

## Current Status
✅ Google Sheets reading is working (found 313 leads)
✅ Sync function updated to read actual data
⚠️ Need to update webhook URL in Google Apps Script