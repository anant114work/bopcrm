# Google Ads API Integration Setup Guide

## Account Structure Analysis

Based on your information:

### **Manager Account (Has API Access)**
- **Email**: boprealtygod@gmail.com
- **Company**: Bop Realty
- **Developer Token**: `Qqs06KvnUON1MNgyVWI0hw` (Test Account Access)
- **Status**: Can access API but doesn't have ads

### **Client Account (Has Ads)**
- **Status**: Contains the actual campaigns and ads
- **Access**: Managed by the manager account above
- **Customer ID**: You need to find this

## Setup Steps

### 1. Get OAuth2 Access Token

You need to complete OAuth2 flow for `boprealtygod@gmail.com`:

```bash
# OAuth2 Scope needed
https://www.googleapis.com/auth/adwords

# OAuth2 URL (replace YOUR_CLIENT_ID)
https://accounts.google.com/o/oauth2/auth?client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI&scope=https://www.googleapis.com/auth/adwords&response_type=code&access_type=offline
```

### 2. Find Your Customer IDs

Use this API call to find accessible accounts:

```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     -H "developer-token: Qqs06KvnUON1MNgyVWI0hw" \
     "https://googleads.googleapis.com/v17/customers:listAccessibleCustomers"
```

### 3. Apply for Basic Access

Your developer token is currently **Test Account Access**. To access production accounts:

1. Go to Google Ads API Center
2. Click "Apply for Basic Access"
3. Fill out the application form
4. Wait for approval (usually 1-2 business days)

### 4. Configure the Integration

#### Django CRM:
```python
# In Django admin or shell
from leads.google_ads_models import GoogleAdsConfig

config = GoogleAdsConfig.objects.create(
    access_token="YOUR_OAUTH2_ACCESS_TOKEN",
    manager_customer_id="MANAGER_CUSTOMER_ID",  # Manager account
    client_customer_id="CLIENT_CUSTOMER_ID",    # Account with ads
    is_active=True
)
```

#### Node.js App:
```bash
# POST to configure
curl -X POST http://localhost:3000/google-ads/config \
  -H "Content-Type: application/json" \
  -d '{
    "accessToken": "YOUR_OAUTH2_ACCESS_TOKEN",
    "managerCustomerId": "MANAGER_CUSTOMER_ID",
    "clientCustomerId": "CLIENT_CUSTOMER_ID"
  }'
```

## Usage

### Django Commands:
```bash
# Sync all data
python manage.py sync_google_ads

# Sync only campaigns
python manage.py sync_google_ads --type campaigns

# Sync leads from last 30 days
python manage.py sync_google_ads --type leads --days 30
```

### Node.js Endpoints:
```bash
# Get campaigns
curl http://localhost:3000/google-ads/campaigns

# Get leads from last 7 days
curl http://localhost:3000/google-ads/leads?days=7

# Check configuration
curl http://localhost:3000/google-ads/config
```

## Important Notes

1. **Test vs Production**: Your token is currently for test accounts only
2. **Manager vs Client**: Manager account has API access, client account has ads
3. **OAuth2 Required**: You need to complete OAuth2 flow for the manager account
4. **Customer IDs**: Remove hyphens when using in API calls (123-456-7890 → 1234567890)

## Next Steps

1. **Complete OAuth2 flow** for boprealtygod@gmail.com
2. **Find your customer IDs** using listAccessibleCustomers
3. **Apply for Basic Access** to access production accounts
4. **Configure the integration** with the obtained tokens and IDs

## Troubleshooting

- **DEVELOPER_TOKEN_NOT_APPROVED**: Apply for Basic Access
- **CUSTOMER_NOT_FOUND**: Check customer ID format (no hyphens)
- **PERMISSION_DENIED**: Verify OAuth2 scope and account access
- **UNAUTHENTICATED**: Check access token validity