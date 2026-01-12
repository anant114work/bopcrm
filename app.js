const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const axios = require('axios');
const path = require('path');

const app = express();
app.use(express.json());
app.use(express.static('.'));

// Configuration
const ACCESS_TOKEN = 'EAAgVjAbsIWoBQG62BB2cOAwa0KTl6A9GKAf2UcIJwfVOqZAyV5fVw9SCBE87XQk05CkW5gMZC60aBheUfUB2S9mFhu3HxXWxEwRxwZCFuyzuT3NBqGZCSW8lKCnmnBDCOlubQCws2QgSZAHigxB8YRlXByVlQP7eQvpSUmtoQCJq34YfyI73iPZA0BdGqYKpFQVILCunWs';
const PAGE_ID = '296508423701621'; // BOP Realty

// Google Ads Configuration
const GOOGLE_ADS_CONFIG = {
  DEVELOPER_TOKEN: 'Qqs06KvnUON1MNgyVWI0hw',
  ACCESS_TOKEN: null, // Set after OAuth
  MANAGER_CUSTOMER_ID: null, // Manager account ID
  CLIENT_CUSTOMER_ID: null   // Client account with ads
};

// Auto-sync configuration
let autoSyncInterval = null;
let isAutoSyncRunning = false;
const SYNC_INTERVAL = 5 * 60 * 1000; // 5 minutes

// Auto-sync status
let syncStats = {
  lastSync: null,
  totalSynced: 0,
  errors: 0,
  isRunning: false
};

// Initialize SQLite database
const db = new sqlite3.Database('leads.db');

// Create leads table with enhanced fields
db.serialize(() => {
  db.run(`CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id TEXT UNIQUE,
    created_time TEXT,
    email TEXT,
    full_name TEXT,
    phone_number TEXT,
    form_name TEXT,
    campaign_name TEXT,
    ad_name TEXT,
    ad_id TEXT,
    adset_id TEXT,
    campaign_id TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  )`);
});

// Fetch leads from Meta using Graph API
async function fetchLeads() {
  try {
    console.log(`[${new Date().toISOString()}] Starting lead sync...`);
    
    // Get all forms
    const formsResponse = await axios.get(`https://graph.facebook.com/v23.0/${PAGE_ID}/leadgen_forms`, {
      params: {
        access_token: ACCESS_TOKEN,
        fields: 'id,name,status,leads_count'
      }
    });
    
    const forms = formsResponse.data.data || [];
    let totalSynced = 0;
    
    for (const form of forms) {
      const formId = form.id;
      const formName = form.name;
      
      // Get leads from each form
      let nextUrl = `https://graph.facebook.com/v23.0/${formId}/leads`;
      
      while (nextUrl) {
        const leadsResponse = await axios.get(nextUrl, {
          params: {
            access_token: ACCESS_TOKEN,
            limit: 100,
            fields: 'id,created_time,field_data,ad_id,adset_id,campaign_id'
          }
        });
        
        const leadsData = leadsResponse.data;
        const leads = leadsData.data || [];
        
        for (const lead of leads) {
          const saved = await saveLead(lead, formName);
          if (saved) totalSynced++;
        }
        
        // Check for next page
        nextUrl = leadsData.paging?.next || null;
      }
    }
    
    syncStats.lastSync = new Date().toISOString();
    syncStats.totalSynced += totalSynced;
    
    console.log(`[${new Date().toISOString()}] Synced ${totalSynced} new leads`);
    return totalSynced;
  } catch (error) {
    console.error('Error fetching leads:', error);
    syncStats.errors++;
    throw error;
  }
}

// Save lead to database
function saveLead(lead, formName) {
  return new Promise((resolve, reject) => {
    // Check if lead already exists
    db.get('SELECT id FROM leads WHERE lead_id = ?', [lead.id], (err, row) => {
      if (err) {
        reject(err);
        return;
      }
      
      if (row) {
        resolve(false); // Lead already exists
        return;
      }
      
      // Extract field data
      const fieldData = lead.field_data || [];
      let email = '', fullName = '', phoneNumber = '';
      
      for (const field of fieldData) {
        const fieldName = field.name?.toLowerCase() || '';
        const fieldValue = field.values?.[0] || '';
        
        if (fieldName.includes('email')) {
          email = fieldValue;
        } else if (fieldName.includes('name')) {
          fullName = fieldValue;
        } else if (fieldName.includes('phone') || fieldName.includes('mobile')) {
          phoneNumber = fieldValue;
        }
      }
      
      db.run(
        `INSERT INTO leads 
         (lead_id, created_time, email, full_name, phone_number, form_name, campaign_name, ad_name) 
         VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
        [
          lead.id,
          lead.created_time,
          email,
          fullName,
          phoneNumber,
          formName,
          lead.campaign_id || '',
          lead.ad_id || ''
        ],
        function(err) {
          if (err) reject(err);
          else resolve(true); // New lead saved
        }
      );
    });
  });
}

// API Routes
app.get('/leads', (req, res) => {
  db.all('SELECT * FROM leads ORDER BY created_at DESC', (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
    } else {
      res.json(rows);
    }
  });
});

// Google Ads API functions
async function getGoogleAdsCampaigns() {
  if (!GOOGLE_ADS_CONFIG.ACCESS_TOKEN || !GOOGLE_ADS_CONFIG.CLIENT_CUSTOMER_ID) {
    throw new Error('Google Ads not configured');
  }
  
  const url = `https://googleads.googleapis.com/v17/customers/${GOOGLE_ADS_CONFIG.CLIENT_CUSTOMER_ID}/googleAds:search`;
  
  const query = `
    SELECT 
      campaign.id,
      campaign.name,
      campaign.status,
      metrics.impressions,
      metrics.clicks,
      metrics.cost_micros
    FROM campaign 
    WHERE campaign.status != 'REMOVED'
  `;
  
  try {
    const response = await axios.post(url, { query }, {
      headers: {
        'Authorization': `Bearer ${GOOGLE_ADS_CONFIG.ACCESS_TOKEN}`,
        'developer-token': GOOGLE_ADS_CONFIG.DEVELOPER_TOKEN,
        'login-customer-id': GOOGLE_ADS_CONFIG.MANAGER_CUSTOMER_ID,
        'Content-Type': 'application/json'
      }
    });
    
    return response.data.results || [];
  } catch (error) {
    console.error('Error fetching Google Ads campaigns:', error.response?.data || error.message);
    throw error;
  }
}

async function getGoogleAdsLeads(daysBack = 30) {
  if (!GOOGLE_ADS_CONFIG.ACCESS_TOKEN || !GOOGLE_ADS_CONFIG.CLIENT_CUSTOMER_ID) {
    throw new Error('Google Ads not configured');
  }
  
  const endDate = new Date();
  const startDate = new Date(endDate.getTime() - (daysBack * 24 * 60 * 60 * 1000));
  
  const url = `https://googleads.googleapis.com/v17/customers/${GOOGLE_ADS_CONFIG.CLIENT_CUSTOMER_ID}/googleAds:search`;
  
  const query = `
    SELECT 
      lead_form_submission_data.id,
      lead_form_submission_data.campaign_id,
      lead_form_submission_data.form_submission_date_time,
      lead_form_submission_data.custom_lead_form_submission_fields
    FROM lead_form_submission_data 
    WHERE segments.date >= '${startDate.toISOString().split('T')[0]}'
    AND segments.date <= '${endDate.toISOString().split('T')[0]}'
  `;
  
  try {
    const response = await axios.post(url, { query }, {
      headers: {
        'Authorization': `Bearer ${GOOGLE_ADS_CONFIG.ACCESS_TOKEN}`,
        'developer-token': GOOGLE_ADS_CONFIG.DEVELOPER_TOKEN,
        'login-customer-id': GOOGLE_ADS_CONFIG.MANAGER_CUSTOMER_ID,
        'Content-Type': 'application/json'
      }
    });
    
    return response.data.results || [];
  } catch (error) {
    console.error('Error fetching Google Ads leads:', error.response?.data || error.message);
    throw error;
  }
app.get('/google-ads/campaigns', async (req, res) => {
  try {
    const campaigns = await getGoogleAdsCampaigns();
    res.json(campaigns);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/google-ads/leads', async (req, res) => {
  try {
    const daysBack = parseInt(req.query.days) || 30;
    const leads = await getGoogleAdsLeads(daysBack);
    res.json(leads);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.post('/google-ads/config', (req, res) => {
  try {
    const { accessToken, managerCustomerId, clientCustomerId } = req.body;
    
    GOOGLE_ADS_CONFIG.ACCESS_TOKEN = accessToken;
    GOOGLE_ADS_CONFIG.MANAGER_CUSTOMER_ID = managerCustomerId?.replace(/-/g, '');
    GOOGLE_ADS_CONFIG.CLIENT_CUSTOMER_ID = clientCustomerId?.replace(/-/g, '');
    
    res.json({ 
      message: 'Google Ads configuration updated',
      config: {
        developerToken: GOOGLE_ADS_CONFIG.DEVELOPER_TOKEN,
        managerCustomerId: GOOGLE_ADS_CONFIG.MANAGER_CUSTOMER_ID,
        clientCustomerId: GOOGLE_ADS_CONFIG.CLIENT_CUSTOMER_ID,
        configured: !!GOOGLE_ADS_CONFIG.ACCESS_TOKEN
      }
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/google-ads/config', (req, res) => {
  res.json({
    developerToken: GOOGLE_ADS_CONFIG.DEVELOPER_TOKEN,
    managerCustomerId: GOOGLE_ADS_CONFIG.MANAGER_CUSTOMER_ID,
    clientCustomerId: GOOGLE_ADS_CONFIG.CLIENT_CUSTOMER_ID,
    configured: !!GOOGLE_ADS_CONFIG.ACCESS_TOKEN
  });
});

// Start auto-sync
function startAutoSync() {
    console.log('Auto-sync already running');
    return;
  }
  
  isAutoSyncRunning = true;
  syncStats.isRunning = true;
  
  console.log(`[${new Date().toISOString()}] Starting auto-sync every ${SYNC_INTERVAL/1000/60} minutes`);
  
  // Initial sync
  fetchLeads().catch(err => console.error('Initial sync error:', err));
  
  // Set up interval
  autoSyncInterval = setInterval(async () => {
    try {
      await fetchLeads();
    } catch (error) {
      console.error('Auto-sync error:', error);
    }
  }, SYNC_INTERVAL);
}

// Stop auto-sync
function stopAutoSync() {
  if (autoSyncInterval) {
    clearInterval(autoSyncInterval);
    autoSyncInterval = null;
  }
  isAutoSyncRunning = false;
  syncStats.isRunning = false;
  console.log(`[${new Date().toISOString()}] Auto-sync stopped`);
}

app.post('/sync-leads', async (req, res) => {
  try {
    const synced = await fetchLeads();
    res.json({ 
      message: 'Leads synced successfully',
      synced: synced,
      stats: syncStats
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.post('/start-auto-sync', (req, res) => {
  try {
    startAutoSync();
    res.json({ 
      message: 'Auto-sync started',
      interval: `${SYNC_INTERVAL/1000/60} minutes`,
      stats: syncStats
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.post('/stop-auto-sync', (req, res) => {
  try {
    stopAutoSync();
    res.json({ 
      message: 'Auto-sync stopped',
      stats: syncStats
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/sync-status', (req, res) => {
  res.json({
    isRunning: isAutoSyncRunning,
    interval: `${SYNC_INTERVAL/1000/60} minutes`,
    stats: syncStats
  });
});

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'dashboard.html'));
});

app.get('/leads/:id', (req, res) => {
  db.get('SELECT * FROM leads WHERE id = ?', [req.params.id], (err, row) => {
    if (err) {
      res.status(500).json({ error: err.message });
    } else if (row) {
      res.json(row);
    } else {
      res.status(404).json({ error: 'Lead not found' });
    }
  });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log('Available endpoints:');
  console.log('GET /leads - Get all leads');
  console.log('POST /sync-leads - Manual sync leads from Meta');
  console.log('POST /start-auto-sync - Start automatic sync');
  console.log('POST /stop-auto-sync - Stop automatic sync');
  console.log('GET /sync-status - Get sync status');
  console.log('GET /leads/:id - Get specific lead');
  
  // Auto-start sync on server start
  console.log('\nStarting auto-sync on server startup...');
  startAutoSync();
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\nShutting down gracefully...');
  stopAutoSync();
  db.close();
  process.exit(0);
});