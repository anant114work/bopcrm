# Acefone CRM Integration

## Overview
This integration adds call functionality to your CRM using Acefone APIs with complete number masking for security.

## Features
- **Click-to-Call**: Initiate calls directly from lead details
- **Number Masking**: All phone numbers are masked (***-***-1234)
- **Call Panel**: Dedicated dashboard for call management
- **Active Calls**: Real-time monitoring of ongoing calls
- **Call Records**: Track all call history and recordings
- **User Mapping**: Assign DID numbers to team members

## Setup Complete ✅
- Acefone configuration created with your token
- Sample DID numbers added
- Call panel accessible at `/call-panel/`
- Admin interface available for DID management

## Usage

### 1. Call Panel
Access the call panel from the sidebar navigation:
- Search leads by name
- View active calls in real-time
- Manual dialer for direct calls
- Call history and recordings

### 2. Lead Details
Each lead detail page now has:
- "Call via Acefone" button (replaces direct phone links)
- Masked phone numbers for security
- Call initiation through Acefone API

### 3. Number Management
Admin users can:
- Add/edit DID numbers via Django admin
- Assign numbers to team members
- Configure display names for numbers

## API Integration
- **Token**: Pre-configured with your provided token
- **Base URL**: https://api.acefone.in/v1
- **Endpoints Used**:
  - Click-to-call for outbound calls
  - Active calls monitoring
  - Call recordings retrieval
  - Call notes management

## Security Features
- All phone numbers are masked in UI
- Only authorized users can initiate calls
- Call records are logged for audit
- Admin-only access to raw numbers

## Next Steps
1. Assign DID numbers to team members in Django admin
2. Test call functionality from lead details
3. Monitor calls in the call panel
4. Configure webhooks for inbound call routing (optional)

## Files Added
- `leads/acefone_models.py` - Database models
- `leads/acefone_client.py` - API client
- `leads/call_views.py` - Call management views
- `leads/templates/leads/call_panel.html` - Call dashboard
- `leads/management/commands/setup_acefone.py` - Setup command

## Admin Access
Visit `/admin/` to manage:
- DID Numbers
- Call Records
- Acefone Configuration