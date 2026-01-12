const bizSdk = require('facebook-nodejs-business-sdk');

const ACCESS_TOKEN = 'EAAgVjAbsIWoBPmzUD4hZBAOXBu1ZCVs3K4ART8wXpJGEs6iUijYIPWH3iDpC2McbFc8v0r6J17n0qAquuvesg9eAo1A4fUUDGpyOhWZBVjYVH4XIk5f2SBCPrVn8cyKEVCECOl3j5wZBYqGLBs9WZCrLblhdszL93e8IafZA591fXZCAZADrOZAP7g1ZAMdNDYJGc4bqotsiOoBLZCnBZAT32fxh4ZBMIGIAnIAasDDU2u6ZCfw5sZD';
const PAGE_ID = '296508423701621';

const FacebookAdsApi = bizSdk.FacebookAdsApi.init(ACCESS_TOKEN);
const Page = bizSdk.Page;

async function testLeads() {
  try {
    const page = new Page(PAGE_ID);
    const forms = await page.getLeadgenForms();
    console.log('Lead forms found:', forms.length);
    
    for (const form of forms) {
      console.log('Form:', form.name);
      const leads = await form.getLeads(['id', 'created_time', 'field_data']);
      console.log('Leads in form:', leads.length);
      
      leads.forEach(lead => {
        console.log('Lead ID:', lead.id);
        console.log('Created:', lead.created_time);
        console.log('Fields:', lead.field_data);
      });
    }
  } catch (error) {
    console.error('Error:', error.message);
  }
}

testLeads();