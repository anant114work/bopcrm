// Updated Google Apps Script Code (Script.gs)
const CONFIG = {
  SPREADSHEET_ID: '1sWyNQnzxaMgaV51sAWsf6a9JXjNLXr68syakZuQxgGc',
  LEADS_SHEET: 'Sheet1',
  VISITORS_SHEET: 'Visitors',
  EMAIL_RECIPIENTS: 'boprealty37@gmail.com,kothiyalritesh@gmail.com',
  PROJECT_SUBJECT: 'AU Aspire Leisure Valley',
  CRM_WEBHOOK_URL: 'http://127.0.0.1:8000/google-sheets-webhook/' // UPDATE THIS WITH YOUR ACTUAL CRM URL
};

function doGet() {
  return ContentService.createTextOutput("OK").setMimeType(ContentService.MimeType.TEXT);
}

function doPost(e) {
  try {
    let data = parseIncomingData(e);
    if (!data || Object.keys(data).length === 0) {
      return ContentService.createTextOutput("ERROR: No data received").setMimeType(ContentService.MimeType.TEXT);
    }

    const action = data.action || 'form_submit';

    if (action === 'visitor' || action === 'visited') {
      handleVisitorTracking(data.ip, action);
    } else if (action === 'form_submit') {
      handleFormSubmission(data);
    }

    return ContentService.createTextOutput("SUCCESS").setMimeType(ContentService.MimeType.TEXT);

  } catch (err) {
    Logger.log("doPost error: " + err);
    return ContentService.createTextOutput("ERROR: " + err).setMimeType(ContentService.MimeType.TEXT);
  }
}

function parseIncomingData(e) {
  let data = {};
  if (e.parameter && Object.keys(e.parameter).length > 0) {
    data = Object.assign({}, e.parameter);
  } else if (e.postData && e.postData.contents) {
    try {
      data = JSON.parse(e.postData.contents);
    } catch (jsonErr) {
      if (e.postData.type === 'application/x-www-form-urlencoded') {
        const pairs = e.postData.contents.split('&');
        pairs.forEach(p => {
          const [k, v] = p.split('=');
          if (k) data[decodeURIComponent(k)] = v ? decodeURIComponent(v.replace(/\+/g, ' ')) : '';
        });
      }
    }
  }
  return data;
}

function handleVisitorTracking(ip, status) {
  const ss = SpreadsheetApp.openById(CONFIG.SPREADSHEET_ID);
  let sheet = ss.getSheetByName(CONFIG.VISITORS_SHEET);
  
  if (!sheet) {
    sheet = ss.insertSheet(CONFIG.VISITORS_SHEET);
    sheet.appendRow(["IP Address", "Status", "Visit Count", "Last Visit"]);
    sheet.getRange(1, 1, 1, 4).setFontWeight("bold");
  }

  const timestamp = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "dd/MM/yyyy HH:mm:ss");
  const data = sheet.getDataRange().getValues();
  let found = false;
  
  for (let i = 1; i < data.length; i++) {
    if (data[i][0] === ip) {
      found = true;
      const visitCount = (data[i][2] || 0) + 1;
      const rowNum = i + 1;
      
      sheet.getRange(rowNum, 2).setValue(status);
      sheet.getRange(rowNum, 3).setValue(visitCount);
      sheet.getRange(rowNum, 4).setValue(timestamp);
      
      if (visitCount >= 3) {
        sheet.getRange(rowNum, 1, 1, 4)
          .setBackground("#FF0000")
          .setFontColor("#FFFFFF");
      }
      break;
    }
  }
  
  if (!found) {
    sheet.appendRow([ip, status, 1, timestamp]);
  }
}

function handleFormSubmission(data) {
  const submitted_at = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "dd/MM/yyyy HH:mm:ss");

  data.name = (data.name || '').trim();
  data.phone = (data.phone || '');
  data.email = (data.email || '').trim();
  data.unit_size = (data.unit_size || '').trim();
  data.project_name = (data.project_name || CONFIG.PROJECT_SUBJECT).trim();
  data.timestamp = submitted_at;

  // Update visitor status
  if (data.ip) {
    handleVisitorTracking(data.ip, 'submitted_form');
  }

  // Save to spreadsheet
  storeInSpreadsheet(data);

  // Send email
  sendEmailNotification(data);

  // NEW: Send to CRM
  sendToCRM(data);
}

function storeInSpreadsheet(data) {
  const ss = SpreadsheetApp.openById(CONFIG.SPREADSHEET_ID);
  let sheet = ss.getSheetByName(CONFIG.LEADS_SHEET);
  if (!sheet) {
    sheet = ss.insertSheet(CONFIG.LEADS_SHEET);
    sheet.appendRow(["Date & Time", "Name", "Phone", "Email", "Unit Size", "Project Name", "IP Address"]);
    sheet.getRange(1, 1, 1, 7).setFontWeight("bold");
  }

  const newRow = [
    data.timestamp,
    data.name,
    data.phone,
    data.email,
    data.unit_size,
    data.project_name,
    data.ip || 'N/A'
  ];

  sheet.appendRow(newRow);
}

function sendEmailNotification(data) {
  const subject = `Project Name: ${CONFIG.PROJECT_SUBJECT}`;

  const htmlBody = `
    <h2>New Lead - ${CONFIG.PROJECT_SUBJECT}</h2>
    <table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;font-family:Arial;font-size:14px;">
      <tr><td><b>Name</b></td><td>${data.name}</td></tr>
      <tr><td><b>Email</b></td><td>${data.email}</td></tr>
      <tr><td><b>Phone</b></td><td>${data.phone}</td></tr>
      <tr><td><b>Unit Size</b></td><td>${data.unit_size}</td></tr>
      <tr><td><b>Project</b></td><td>${data.project_name}</td></tr>
      <tr><td><b>IP Address</b></td><td>${data.ip || 'N/A'}</td></tr>
      <tr><td><b>Submitted At</b></td><td>${data.timestamp}</td></tr>
    </table>
  `;

  const altBody = `Name: ${data.name}
Email: ${data.email}
Phone: ${data.phone}
Unit Size: ${data.unit_size}
Project: ${data.project_name}
IP Address: ${data.ip || 'N/A'}
Submitted At: ${data.timestamp}`;

  const recipients = CONFIG.EMAIL_RECIPIENTS.split(",");
  recipients.forEach(r => {
    MailApp.sendEmail({
      to: r.trim(),
      subject: subject,
      htmlBody: htmlBody,
      body: altBody,
      name: CONFIG.PROJECT_SUBJECT
    });
  });
}

// NEW FUNCTION: Send leads to CRM
function sendToCRM(data) {
  try {
    const payload = {
      name: data.name,
      phone: data.phone,
      email: data.email,
      unit_size: data.unit_size,
      project_name: data.project_name,
      ip: data.ip,
      timestamp: data.timestamp
    };
    
    const response = UrlFetchApp.fetch(CONFIG.CRM_WEBHOOK_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      payload: JSON.stringify(payload)
    });
    
    console.log('CRM Response:', response.getContentText());
    
    if (response.getResponseCode() === 200) {
      console.log('✅ Lead sent to CRM successfully');
      return true;
    } else {
      console.error('❌ CRM Error:', response.getContentText());
      return false;
    }
  } catch (error) {
    console.error('❌ CRM Connection Error:', error);
    return false;
  }
}

// NEW FUNCTION: Sync existing leads to CRM
function syncExistingLeadsToCRM() {
  const ss = SpreadsheetApp.openById(CONFIG.SPREADSHEET_ID);
  const sheet = ss.getSheetByName(CONFIG.LEADS_SHEET);
  
  if (!sheet) {
    console.log('No leads sheet found');
    return;
  }
  
  const data = sheet.getDataRange().getValues();
  const headers = data[0];
  
  // Find column indices
  const nameCol = headers.indexOf('Name');
  const phoneCol = headers.indexOf('Phone');
  const emailCol = headers.indexOf('Email');
  const unitSizeCol = headers.indexOf('Unit Size');
  const projectCol = headers.indexOf('Project Name');
  const ipCol = headers.indexOf('IP Address');
  const timestampCol = headers.indexOf('Date & Time');
  
  let successCount = 0;
  let failCount = 0;
  
  // Process each row (skip header)
  for (let i = 1; i < data.length; i++) {
    const row = data[i];
    
    const leadData = {
      name: row[nameCol] || '',
      phone: row[phoneCol] || '',
      email: row[emailCol] || '',
      unit_size: row[unitSizeCol] || '',
      project_name: row[projectCol] || CONFIG.PROJECT_SUBJECT,
      ip: row[ipCol] || '',
      timestamp: row[timestampCol] || ''
    };
    
    // Skip if no phone number
    if (!leadData.phone) {
      continue;
    }
    
    if (sendToCRM(leadData)) {
      successCount++;
    } else {
      failCount++;
    }
    
    // Add delay to avoid overwhelming the server
    Utilities.sleep(1000); // 1 second delay
  }
  
  console.log(`Sync complete: ${successCount} success, ${failCount} failed`);
}