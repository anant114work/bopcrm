// Google Apps Script for receiving lead data
// Deploy this as a web app in Google Apps Script

function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    
    if (data.action === 'add_lead') {
      return addLeadToSheet(data.data);
    }
    
    return ContentService.createTextOutput(JSON.stringify({success: false, error: 'Unknown action'}));
  } catch (error) {
    return ContentService.createTextOutput(JSON.stringify({success: false, error: error.toString()}));
  }
}

function addLeadToSheet(leadData) {
  try {
    // Open the spreadsheet
    const spreadsheet = SpreadsheetApp.openById('1l2kVvwhafObJ1FObVjLfL3L6DkBx8_oTsWT1z705_a0');
    const sheet = spreadsheet.getActiveSheet();
    
    // Check if headers exist, if not add them
    if (sheet.getLastRow() === 0) {
      const headers = [
        'Lead ID', 'Full Name', 'Email', 'Phone', 'City', 
        'Budget', 'Configuration', 'Preferred Time', 'Form Name', 'Created Time'
      ];
      sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
    }
    
    // Add the lead data
    sheet.appendRow(leadData);
    
    return ContentService.createTextOutput(JSON.stringify({success: true}));
  } catch (error) {
    return ContentService.createTextOutput(JSON.stringify({success: false, error: error.toString()}));
  }
}

// Test function
function testAddLead() {
  const testData = [
    'TEST123', 'Test User', 'test@example.com', '+1234567890', 
    'Test City', '50L', '3BHK', 'Morning', 'Test Form', '2025-01-01 10:00:00'
  ];
  
  addLeadToSheet(testData);
}