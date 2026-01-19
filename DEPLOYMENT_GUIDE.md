# Render Deployment Guide

## 🚀 Deploy to Render

### 1. Prepare Repository
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/drip-crm.git
git push -u origin main
```

### 2. Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Connect your repository

### 3. Deploy Web Service
1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: `drip-crm`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - **Start Command**: `gunicorn crm.wsgi:application`

### 4. Add Environment Variables
In Render dashboard, add these environment variables:

**Required:**
```
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=.onrender.com
META_ACCESS_TOKEN=EAAgVjAbsIWoBPuCGCzxXTPkuBov4q6gPhtvIUfXhJuQlX3SCqDZAiWEmK08RiPFEhG0kTZACrQnGLmZA24AfUbmS2aCb4T7MTb6Iov0LTeH9a5ExDmoaoWuOzbwiHZBV3IqGyqrpcZAStSNsZCfmMzF4DnVKsCbydZAKiv6ErW3vPjNZBftxRyhcgHrMsP6GdkHHr3MA
META_PAGE_ID=296508423701621
```

**Optional (for full functionality):**
```
WHATSAPP_TOKEN=your_whatsapp_token
WHATSAPP_PHONE_ID=your_whatsapp_phone_id
ZOHO_CLIENT_ID=1000.N86NWH8YA8XTVCQ2LPIUGV3V8L8LNA
ZOHO_CLIENT_SECRET=97e14674507d101d6b86e8a695c9cf097f7f38db8e
ZOHO_REDIRECT_URI=https://your-app.onrender.com/zoho-callback/
```

### 5. Create Database (Optional)
1. Click "New +" → "PostgreSQL"
2. Name: `drip-crm-db`
3. Copy the `DATABASE_URL` to your web service environment variables

### 6. Update Zoho Redirect URI
After deployment, update your Zoho app settings:
1. Go to Zoho Developer Console
2. Update redirect URI to: `https://your-app.onrender.com/zoho-callback/`

## 🔧 Local Development

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your values
# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver
```

### Environment Variables for Local Development
Create `.env.local`:
```
SECRET_KEY=django-insecure-local-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
META_ACCESS_TOKEN=your_token
META_PAGE_ID=your_page_id
ZOHO_REDIRECT_URI=http://127.0.0.1:8000/zoho-callback/
```

## 📋 Post-Deployment Checklist

- [ ] App deploys successfully
- [ ] Database migrations run
- [ ] Static files served correctly
- [ ] Meta leads sync works
- [ ] Zoho integration works (after updating redirect URI)
- [ ] WhatsApp integration works (if configured)
- [ ] Google Sheets integration works (if configured)

## 🔍 Troubleshooting

### Common Issues:

1. **Static files not loading**
   - Check `STATIC_ROOT` and `STATICFILES_DIRS` in settings
   - Ensure `collectstatic` runs in build command

2. **Database connection errors**
   - Verify `DATABASE_URL` environment variable
   - Check PostgreSQL service is running

3. **Zoho OAuth errors**
   - Update redirect URI in Zoho console
   - Check `ZOHO_REDIRECT_URI` environment variable

4. **Meta API errors**
   - Verify `META_ACCESS_TOKEN` is valid
   - Check `META_PAGE_ID` is correct

## 🚀 Production URLs

After deployment, your app will be available at:
- **Main App**: `https://your-app.onrender.com`
- **Admin**: `https://your-app.onrender.com/admin/`
- **Zoho Config**: `https://your-app.onrender.com/zoho-config/`

## 🔐 Security Notes

- Never commit `.env` files to git
- Use strong `SECRET_KEY` in production
- Enable HTTPS redirect in production
- Regularly rotate API tokens
- Monitor logs for security issues