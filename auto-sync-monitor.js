const axios = require('axios');

const BASE_URL = 'http://localhost:3000';

async function checkSyncStatus() {
  try {
    const response = await axios.get(`${BASE_URL}/sync-status`);
    const status = response.data;
    
    console.log('\n=== Auto-Sync Status ===');
    console.log(`Running: ${status.isRunning ? '✅ YES' : '❌ NO'}`);
    console.log(`Interval: ${status.interval}`);
    console.log(`Last Sync: ${status.stats.lastSync || 'Never'}`);
    console.log(`Total Synced: ${status.stats.totalSynced}`);
    console.log(`Errors: ${status.stats.errors}`);
    console.log('========================\n');
    
    return status;
  } catch (error) {
    console.error('Error checking status:', error.message);
    return null;
  }
}

async function startAutoSync() {
  try {
    const response = await axios.post(`${BASE_URL}/start-auto-sync`);
    console.log('✅', response.data.message);
    return true;
  } catch (error) {
    console.error('❌ Error starting auto-sync:', error.message);
    return false;
  }
}

async function stopAutoSync() {
  try {
    const response = await axios.post(`${BASE_URL}/stop-auto-sync`);
    console.log('✅', response.data.message);
    return true;
  } catch (error) {
    console.error('❌ Error stopping auto-sync:', error.message);
    return false;
  }
}

async function manualSync() {
  try {
    console.log('🔄 Starting manual sync...');
    const response = await axios.post(`${BASE_URL}/sync-leads`);
    console.log('✅', response.data.message);
    console.log(`📊 Synced: ${response.data.synced} leads`);
    return true;
  } catch (error) {
    console.error('❌ Error during manual sync:', error.message);
    return false;
  }
}

async function getLeads() {
  try {
    const response = await axios.get(`${BASE_URL}/leads`);
    const leads = response.data;
    
    console.log(`\n📋 Total Leads: ${leads.length}`);
    if (leads.length > 0) {
      console.log('Recent leads:');
      leads.slice(0, 5).forEach((lead, index) => {
        console.log(`${index + 1}. ${lead.full_name || 'No name'} - ${lead.email || 'No email'} - ${lead.phone_number || 'No phone'}`);
      });
    }
    console.log('');
    
    return leads;
  } catch (error) {
    console.error('Error getting leads:', error.message);
    return [];
  }
}

// Command line interface
const command = process.argv[2];

async function main() {
  switch (command) {
    case 'status':
      await checkSyncStatus();
      break;
    case 'start':
      await startAutoSync();
      await checkSyncStatus();
      break;
    case 'stop':
      await stopAutoSync();
      await checkSyncStatus();
      break;
    case 'sync':
      await manualSync();
      break;
    case 'leads':
      await getLeads();
      break;
    case 'monitor':
      console.log('🔍 Monitoring auto-sync (press Ctrl+C to stop)...\n');
      setInterval(async () => {
        await checkSyncStatus();
      }, 30000); // Check every 30 seconds
      break;
    default:
      console.log('Meta Leads Auto-Sync Monitor');
      console.log('Usage: node auto-sync-monitor.js <command>');
      console.log('');
      console.log('Commands:');
      console.log('  status   - Check current sync status');
      console.log('  start    - Start auto-sync');
      console.log('  stop     - Stop auto-sync');
      console.log('  sync     - Run manual sync');
      console.log('  leads    - Show recent leads');
      console.log('  monitor  - Continuously monitor status');
      break;
  }
}

main().catch(console.error);