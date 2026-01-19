# Acefone AWS Signature V4 Setup

## Required Credentials

You need to get these from your Acefone account:

1. **Access Key** - Your Acefone access key
2. **Secret Key** - Your Acefone secret key

## Update Configuration

Edit `leads/acefone_client.py` and replace:

```python
self.access_key = "YOUR_ACCESS_KEY"  # Replace with actual key
self.secret_key = "YOUR_SECRET_KEY"  # Replace with actual key
```

With your actual Acefone credentials.

## Why This is Required

Acefone uses AWS Signature V4 authentication (same as AWS S3/API Gateway), not simple Bearer tokens. This requires:

- Canonical request creation
- HMAC-SHA256 signing
- Proper authorization header format

## Once Updated

The following will work:
- Fetch DID numbers from Acefone
- Click-to-call functionality
- Active calls monitoring
- Call recordings

## Current Status

❌ **Not Working**: Missing access key and secret key
✅ **Ready**: AWS Signature V4 implementation complete