# Local Server Webhook Setup with ngrok

## Step 1: Install ngrok
1. Download ngrok from https://ngrok.com/download
2. Extract to a folder (e.g., C:\ngrok\)
3. Sign up for free account at https://ngrok.com/
4. Get your authtoken from dashboard

## Step 2: Setup ngrok
1. Open Command Prompt as Administrator
2. Navigate to ngrok folder: `cd C:\ngrok\`
3. Add authtoken: `ngrok authtoken YOUR_AUTHTOKEN_HERE`

## Step 3: Expose Local Server
1. Start your Django server: `python manage.py runserver`
2. In another terminal, run: `ngrok http 8000`
3. Copy the HTTPS URL (e.g., https://abc123.ngrok.io)

## Step 4: Update Google Apps Script
Replace the CRM_WEBHOOK_URL in your Google Apps Script:
```javascript
CRM_WEBHOOK_URL: 'https://YOUR_NGROK_URL.ngrok.io/webhook/google-leads/'
```

## Step 5: Test Integration
1. Submit a test form
2. Check ngrok terminal for incoming requests
3. Verify lead appears in your CRM

## Alternative: Manual Sync
If ngrok doesn't work, use the "Import Google Leads" button on the Google Leads page to manually import existing leads.

## Production Setup
For production, deploy your CRM to a cloud service (Heroku, AWS, etc.) and use that URL instead of ngrok.