# Meta Leads CRM Integration with Auto-Sync

A Node.js application that automatically retrieves leads from Facebook Business Center and stores them in a local CRM database with continuous synchronization.

## Features

- ✅ **Auto-Sync**: Automatically syncs leads every 5 minutes
- 📊 **Web Dashboard**: Monitor sync status and leads through web interface
- 🔄 **Manual Sync**: Trigger manual synchronization when needed
- 📱 **API Endpoints**: RESTful API for integration
- 💾 **SQLite Database**: Local storage with duplicate prevention
- 🎯 **Enhanced Lead Data**: Captures ad_id, campaign_id, adset_id

## Quick Start

1. **Install dependencies:**
```bash
npm install
```

2. **Start the server with auto-sync:**
```bash
npm start
# OR use the batch file on Windows:
start-auto-sync.bat
```

3. **Access the dashboard:**
Open http://localhost:3000 in your browser

## Access Token

The application uses the Meta access token:
```
EAAgVjAbsIWoBQG62BB2cOAwa0KTl6A9GKAf2UcIJwfVOqZAyV5fVw9SCBE87XQk05CkW5gMZC60aBheUfUB2S9mFhu3HxXWxEwRxwZCFuyzuT3NBqGZCSW8lKCnmnBDCOlubQCws2QgSZAHigxB8YRlXByVlQP7eQvpSUmtoQCJq34YfyI73iPZA0BdGqYKpFQVILCunWs
```

## API Endpoints

### Lead Management
- `GET /leads` - Retrieve all leads
- `GET /leads/:id` - Get specific lead by ID

### Sync Control
- `POST /sync-leads` - Manual sync leads from Meta
- `POST /start-auto-sync` - Start automatic synchronization
- `POST /stop-auto-sync` - Stop automatic synchronization
- `GET /sync-status` - Get current sync status and statistics

### Dashboard
- `GET /` - Web dashboard for monitoring and control

## Command Line Tools

### Auto-Sync Monitor
```bash
# Check sync status
node auto-sync-monitor.js status

# Start auto-sync
node auto-sync-monitor.js start

# Stop auto-sync
node auto-sync-monitor.js stop

# Manual sync
node auto-sync-monitor.js sync

# View recent leads
node auto-sync-monitor.js leads

# Monitor continuously
node auto-sync-monitor.js monitor
```

## Usage

### Automatic Synchronization
The server automatically starts syncing leads every 5 minutes when started. You can:

1. **Monitor via Web Dashboard**: Visit http://localhost:3000
2. **Control via API**: Use the sync control endpoints
3. **Command Line**: Use the auto-sync-monitor.js tool

### Manual Operations

1. **Manual sync via API**:
```bash
curl -X POST http://localhost:3000/sync-leads
```

2. **Check sync status**:
```bash
curl http://localhost:3000/sync-status
```

3. **View all leads**:
```bash
curl http://localhost:3000/leads
```

### Auto-Sync Features

- ✅ **Duplicate Prevention**: Prevents duplicate leads based on Meta lead ID
- 🔄 **Continuous Sync**: Runs every 5 minutes automatically
- 📊 **Statistics Tracking**: Tracks total synced, errors, last sync time
- 🚫 **Error Handling**: Continues running even if individual syncs fail
- 📱 **Real-time Monitoring**: Web dashboard updates every 30 seconds

## Database

Uses SQLite database (`leads.db`) to store lead information including:
- Lead ID (Meta lead ID)
- Contact information (email, name, phone)
- Form and campaign details
- Ad tracking (ad_id, adset_id, campaign_id)
- Creation timestamps
- Duplicate prevention

## Configuration

- **Sync Interval**: 5 minutes (configurable in app.js)
- **Page ID**: 296508423701621 (BOP Realty)
- **Access Token**: Pre-configured with provided token
- **Database**: SQLite (leads.db)
- **Port**: 3000 (configurable via PORT environment variable)

## Files Structure

```
├── app.js                    # Main server application
├── auto-sync-monitor.js      # Command line monitoring tool
├── dashboard.html            # Web dashboard interface
├── start-auto-sync.bat       # Windows startup script
├── package.json              # Dependencies and scripts
├── leads.db                  # SQLite database (auto-created)
└── README.md                 # This file
```