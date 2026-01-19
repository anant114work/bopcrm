# Meta Leads CRM - Production Ready

A comprehensive Django-based CRM system for managing leads from Meta (Facebook), Google, and other sources with AI-powered features, WhatsApp integration, and automated calling.

## 🚀 Features

- **Lead Management**: Capture and manage leads from multiple sources
- **Meta Integration**: Automatic lead sync from Facebook Business Center
- **Google Leads**: Import and manage Google Ads leads
- **WhatsApp Campaigns**: Send bulk WhatsApp messages and drip campaigns
- **AI Assistant**: AI-powered lead analysis and recommendations
- **Call Integration**: Automated calling with Call Karo AI and Tata API
- **Team Management**: Hierarchical team structure with lead assignment
- **Analytics Dashboard**: Comprehensive analytics and reporting
- **Project Management**: Track leads by projects and properties
- **Auto-Sync**: Automatic lead synchronization every 30 minutes

## 📋 Requirements

- Python 3.8+
- PostgreSQL 12+
- Redis 6+ (optional, for caching and Celery)
- Nginx
- Ubuntu 20.04/22.04 (for production)

## 🛠️ Installation

### Local Development

1. **Clone the repository**
```bash
git clone <repository-url>
cd drip
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Run migrations**
```bash
python manage.py migrate
python manage.py createsuperuser
```

6. **Collect static files**
```bash
python manage.py collectstatic
```

7. **Run development server**
```bash
python manage.py runserver
```

Visit http://localhost:8000

### Production Deployment (Hostinger VPS)

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

**Quick deployment:**
```bash
chmod +x deploy.sh
./deploy.sh
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Django
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/crm_db

# Meta API
META_ACCESS_TOKEN=your-token
META_PAGE_ID=your-page-id

# WhatsApp
WHATSAPP_TOKEN=your-token
WHATSAPP_PHONE_ID=your-phone-id

# AI Services
OPENAI_API_KEY=your-key
CALLKARO_API_KEY=your-key
```

See `.env.example` for all available options.

## 📁 Project Structure

```
drip/
├── crm/                    # Django project settings
├── leads/                  # Main application
│   ├── models.py          # Database models
│   ├── views.py           # View functions
│   ├── templates/         # HTML templates
│   └── static/            # Static files (CSS, JS)
├── static/                # Global static files
├── staticfiles/           # Collected static files (production)
├── media/                 # User uploaded files
├── requirements.txt       # Python dependencies
├── deploy.sh             # Deployment script
├── restart.sh            # Quick restart script
└── DEPLOYMENT.md         # Deployment guide
```

## 🔐 Security

- HTTPS enforced in production
- CSRF protection enabled
- Secure session cookies
- SQL injection protection
- XSS protection
- Environment-based configuration

## 📊 API Integrations

- **Meta (Facebook)**: Lead ads integration
- **WhatsApp Business API**: Message sending
- **Call Karo AI**: Automated calling
- **Tata API**: IVR and calling
- **OpenAI**: AI-powered features
- **Zoho CRM**: CRM integration (optional)

## 🚀 Deployment

### Quick Commands

```bash
# Restart application
./restart.sh

# View logs
sudo journalctl -u crm -f

# Update application
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart crm
```

### SSL Setup

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

## 🐛 Troubleshooting

### Static files not loading
```bash
python manage.py collectstatic --noinput
sudo systemctl restart nginx
```

### Database connection error
Check PostgreSQL service and DATABASE_URL in .env

### Permission issues
```bash
sudo chown -R $USER:www-data /var/www/drip
sudo chmod -R 755 /var/www/drip
```

## 📝 License

Proprietary - All rights reserved

## 👥 Support

For support and questions, contact the development team.

## 🔄 Updates

To update the application:

1. Pull latest changes
2. Install new dependencies
3. Run migrations
4. Collect static files
5. Restart services

```bash
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart crm
```

## 📈 Performance

- Uses WhiteNoise for efficient static file serving
- Redis caching for improved performance
- Celery for background tasks
- Database query optimization
- Compressed static files in production

## 🎯 Key Features

### Lead Management
- Multi-source lead capture
- Automatic lead assignment
- Lead scoring and prioritization
- Custom fields and tags

### Communication
- WhatsApp bulk messaging
- Drip campaigns
- Automated calling
- Email integration

### Analytics
- Lead source analysis
- Conversion tracking
- Team performance metrics
- Custom reports

### Team Management
- Hierarchical structure
- Role-based access
- Lead assignment rules
- Performance tracking
