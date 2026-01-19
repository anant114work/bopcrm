# Enhanced Meta Sync System

A high-performance Meta (Facebook) Lead Ads synchronization system designed to handle 2000+ forms with minute-by-minute syncing.

## Features

- **High Volume Support**: Efficiently processes 2000+ Meta forms
- **Minute-by-minute Syncing**: Automatic sync every 60 seconds
- **Batch Processing**: Processes forms in batches to avoid rate limits
- **Real-time Logging**: Clean console output showing only success messages and lead counts
- **Error Recovery**: Automatic retry and error handling
- **Dashboard Monitoring**: Web-based dashboard for monitoring and control

## Quick Start

### Method 1: Windows Batch File
```bash
# Double-click or run from command prompt
start_enhanced_sync.bat
```

### Method 2: Python Script
```bash
python start_enhanced_meta_sync.py
```

### Method 3: Django Management Command
```bash
python manage.py start_enhanced_sync
```

### Method 4: Web Dashboard
1. Navigate to: `http://localhost:8000/leads/enhanced-sync/dashboard/`
2. Click "Start Auto Sync"

## Configuration

Ensure these settings are configured in your `.env` file:

```env
META_ACCESS_TOKEN=your_meta_access_token_here
META_PAGE_ID=your_page_id_here
```

## Console Output

The system provides clean, minimal console output:

```
✓ Synced 45 leads from 1847 forms
✓ Synced 23 leads from 1847 forms  
✓ Synced 67 leads from 1847 forms
```

## Dashboard Features

- **Real-time Status**: Shows if sync is running or stopped
- **Live Statistics**: Today's leads, total forms, success rate
- **Recent Activity**: Last 20 sync runs with timestamps
- **Manual Controls**: Start/stop sync, trigger manual sync
- **Hourly Charts**: Visual breakdown of today's lead distribution

## API Endpoints

- `GET /leads/enhanced-sync/dashboard/` - Dashboard interface
- `POST /leads/enhanced-sync/start/` - Start auto sync
- `POST /leads/enhanced-sync/stop/` - Stop auto sync
- `GET /leads/enhanced-sync/status/` - Get sync status
- `POST /leads/enhanced-sync/manual/` - Trigger manual sync

## Performance Optimizations

1. **Batch Processing**: Forms processed in batches of 50
2. **Rate Limiting**: Small delays between batches to avoid API limits
3. **Recent Data Only**: Only syncs leads from last 24 hours to avoid duplicates
4. **Database Transactions**: Atomic operations for data integrity
5. **Efficient Queries**: Optimized database queries to check existing leads

## Monitoring

### Web Dashboard
Access the dashboard at `/leads/enhanced-sync/dashboard/` to monitor:
- Sync status (running/stopped)
- Real-time statistics
- Recent sync activity
- Manual controls

### Console Logs
The system outputs clean success messages:
- ✓ Success with lead count and form count
- ✗ Error messages with details

### Database Logs
All sync activities are logged to the `SyncLog` model for historical analysis.

## Troubleshooting

### Sync Not Starting
1. Check Meta API credentials in settings
2. Verify network connectivity
3. Check console for error messages

### No Leads Being Synced
1. Verify forms exist in Meta Business Manager
2. Check if forms have recent leads (last 24 hours)
3. Verify API permissions

### High Memory Usage
1. The system is optimized for 2000+ forms
2. Batch processing limits memory usage
3. Consider reducing batch size if needed

## Technical Details

### Architecture
- **Main Service**: `EnhancedMetaSync` class handles all sync operations
- **Threading**: Uses daemon threads for background processing
- **API Integration**: Facebook Graph API v18.0
- **Database**: Django ORM with atomic transactions

### Sync Process
1. Fetch all forms from Meta API (paginated)
2. Process forms in batches of 50
3. For each form, get leads from last 24 hours
4. Parse lead data and save to database
5. Log results and continue to next batch

### Error Handling
- Network timeouts: Automatic retry
- API rate limits: Batch delays and backoff
- Database errors: Transaction rollback
- Invalid data: Skip and continue

## Support

For issues or questions:
1. Check the dashboard for sync status
2. Review console logs for errors
3. Check database sync logs
4. Verify API credentials and permissions