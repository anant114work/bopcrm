// FIXED Google Apps Script - Replace YOUR_CRM_URL with actual URL
function sendToCRM(data) {
  // CHANGE THIS URL to your actual CRM webhook URL
  const CRM_WEBHOOK_URL = 'https://your-actual-domain.com/google-sheets-webhook/';
  // OR if running locally: 'http://localhost:8000/google-sheets-webhook/'
  
  const payload = {
    name: data.name,
    phone: data.phone,
    email: data.email,
    unit_size: data.unit_size,
    project_name: data.project_name,
    ip: data.ip,
    timestamp: data.timestamp
  };
  
  try {
    const response = UrlFetchApp.fetch(CRM_WEBHOOK_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      payload: JSON.stringify(payload)
    });
    
    console.log('CRM Response:', response.getContentText());
    return response.getResponseCode() === 200;
  } catch (error) {
    console.error('CRM Error:', error);
    return false;
  }
}

// ALSO UPDATE handleFormSubmission to actually call sendToCRM
function handleFormSubmission(data) {
  const submitted_at = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "dd/MM/yyyy HH:mm:ss");

  data.name = (data.name || '').trim();
  data.phone = (data.phone || '');
  data.email = (data.email || '').trim();
  data.unit_size = (data.unit_size || '').trim();
  data.project_name = (data.project_name || CONFIG.PROJECT_SUBJECT).trim();
  data.timestamp = submitted_at;

  // Update visitor status to "submitted_form"
  if (data.ip) {
    handleVisitorTracking(data.ip, 'submitted_form');
  }

  // Save lead to Sheet1
  storeInSpreadsheet(data);

  // Send Email
  sendEmailNotification(data);
  
  // SEND TO CRM - This was missing the actual call!
  sendToCRM(data);
}