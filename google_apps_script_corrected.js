// CORRECTED GOOGLE APPS SCRIPT CODE
// Replace your existing sendToCRM function with this:

function sendToCRM(data) {
  // IMPORTANT: Use your actual CRM URL
  const CRM_WEBHOOK_URL = 'http://127.0.0.1:8000/google-sheets-webhook/';
  
  // Format data for CRM
  const payload = {
    name: data.name || '',
    phone: data.phone || '',
    email: data.email || '',
    unit_size: data.unit_size || '',
    project_name: data.project_name || 'AU Aspire Form',
    ip: data.ip || '',
    timestamp: data.timestamp || Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "dd/MM/yyyy HH:mm:ss")
  };
  
  console.log('Sending to CRM:', payload);
  
  try {
    const response = UrlFetchApp.fetch(CRM_WEBHOOK_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      payload: JSON.stringify(payload)
    });
    
    const responseText = response.getContentText();
    const statusCode = response.getResponseCode();
    
    console.log('CRM Response Status:', statusCode);
    console.log('CRM Response:', responseText);
    
    if (statusCode === 200) {
      const result = JSON.parse(responseText);
      if (result.duplicate) {
        console.log('Lead already exists in CRM');
      } else {
        console.log('Lead successfully added to CRM');
      }
      return true;
    } else {
      console.error('CRM Error:', responseText);
      return false;
    }
    
  } catch (error) {
    console.error('CRM Connection Error:', error);
    return false;
  }
}

// BULK SYNC FUNCTION - Run this once to sync all existing leads
function syncAllLeadsTooCRM() {
  const sheet = SpreadsheetApp.getActiveSheet();
  const data = sheet.getDataRange().getValues();
  
  // Skip header row
  for (let i = 1; i < data.length; i++) {
    const row = data[i];
    
    const leadData = {
      timestamp: row[0] ? Utilities.formatDate(new Date(row[0]), Session.getScriptTimeZone(), "dd/MM/yyyy HH:mm:ss") : '',
      name: row[1] || '',
      phone: row[2] || '',
      email: row[3] || '',
      unit_size: '2 BHK', // Default
      project_name: 'AU Aspire Form', // Your project name
      ip: '192.168.1.1' // Default IP
    };
    
    console.log(`Syncing lead ${i}: ${leadData.name}`);
    sendToCRM(leadData);
    
    // Add small delay to avoid overwhelming the server
    Utilities.sleep(100);
  }
  
  console.log('Bulk sync completed!');
}

// FORM SUBMISSION HANDLER - This should be called when new leads are added
function handleFormSubmission(data) {
  const submitted_at = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "dd/MM/yyyy HH:mm:ss");

  // Clean and prepare data
  data.name = (data.name || '').trim();
  data.phone = (data.phone || '').toString().trim();
  data.email = (data.email || '').trim();
  data.unit_size = (data.unit_size || '2 BHK').trim();
  data.project_name = (data.project_name || 'AU Aspire Form').trim();
  data.timestamp = submitted_at;

  // Update visitor status if needed
  if (data.ip) {
    // handleVisitorTracking(data.ip, 'submitted_form');
  }

  // Save to spreadsheet (your existing logic)
  // storeInSpreadsheet(data);

  // Send email notification (your existing logic)  
  // sendEmailNotification(data);

  // NEW: Send to CRM
  const success = sendToCRM(data);
  
  if (success) {
    console.log('Lead successfully sent to CRM');
  } else {
    console.error('Failed to send lead to CRM');
  }
}