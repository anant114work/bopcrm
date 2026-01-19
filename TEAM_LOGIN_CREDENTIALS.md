# Team Login Credentials

## Login Format
- **Username**: First name in lowercase (e.g., "gaurav", "amit", "ankush")
- **Password**: Phone number (e.g., "9910266552", "8130040959")

## Key Team Members Created

### Owner/Admin Level
- **Gaurav Mavi**: username: `gaurav`, password: `9910266552`
- **Admin**: username: `admin1`, password: `7290001154`
- **Atul Verma**: username: `atul`, password: `9999929832`
- **komal sharma**: username: `komal`, password: `7290001169`
- **JAGDISH**: username: `jagdish`, password: `8800932661`

### Team Heads (T2)
- **amit mavi**: username: `amit`, password: `8130040959`
- **Prince Mavi**: username: `prince`, password: `9999826429`
- **Sachin Mavi**: username: `sachin`, password: `7982507208`
- **SAURAV MAVI**: username: `saurav`, password: `8126084952`
- **RAGHU NANDAN**: username: `raghu`, password: `8920410474`
- **ankit mavi**: username: `ankit`, password: `9650633333`

### Sales Managers (T4)
- **Ankush Kadyan**: username: `ankush`, password: `9871627302`
- **gaurav gandhi**: username: `gaurav1`, password: `9873665696`
- **chirag jaitley**: username: `chirag`, password: `9667434500`
- **Romil Saxena**: username: `romil`, password: `9355876257`
- **manik anand**: username: `manik`, password: `9818888418`

### Sample Sales Executives & Others
- **Aarti sharma**: username: `aarti`, password: `7669275936`
- **ABHIMANYU MEHRA**: username: `abhimanyu`, password: `9582201434`
- **Abhishek gg**: username: `abhishek`, password: `9711344640`
- **Aditya Bhadana**: username: `aditya`, password: `9355876240`
- **AJAY PAL SINGH**: username: `ajay`, password: `8800134520`

## Features Available

### For All Users
1. **Dashboard**: View team statistics and lead overview
2. **My Leads**: View leads assigned to them
3. **Lead Management**: Update lead stages, add notes
4. **Team View**: See team hierarchy

### For Managers & Above
1. **Lead Assignment**: Assign leads to team members
2. **Team Management**: View all team members
3. **Lead Oversight**: View all leads and their status

### For Admins
1. **Full System Access**: All features
2. **Team Import**: Import new team members
3. **System Configuration**: WhatsApp, Zoho, etc.

## System Features

### Automatic Lead Assignment
- New leads automatically assigned via round-robin
- 30-minute SLA for lead response
- Auto-reassignment if SLA missed

### Lead Stages
- New, Contacted, Interested, Not Interested
- Site Visit, Hot, Warm, Cold, Dead, Converted

### Notes System
- Add notes to leads
- Track follow-up activities
- View note history

## Navigation
- **Fixed Sidebar**: Easy navigation between sections
- **Dashboard**: `/` - Main overview
- **All Leads**: `/leads/` - View all leads
- **My Leads**: `/my-leads/` - Personal assigned leads
- **Team**: `/team/` - Team member directory
- **WhatsApp**: `/whatsapp/` - Bulk messaging
- **Configuration**: Various setup pages

## Current Status
- **Total Team Members**: 67 (expandable to 321)
- **User Accounts**: 68 (including superuser)
- **Hierarchy**: 5 levels implemented
- **Auto-Assignment**: Active
- **SLA Monitoring**: Available

## Next Steps
1. Test login with any team member credentials
2. Create test leads to see assignment in action
3. Add remaining team members as needed
4. Configure WhatsApp templates
5. Set up SLA monitoring cron job

## Server Access
- **Development Server**: http://127.0.0.1:8001/
- **Login Page**: http://127.0.0.1:8001/admin/ (for Django admin)
- **Main App**: http://127.0.0.1:8001/ (main dashboard)

## Support
- All team members can login with their credentials
- Lead assignment happens automatically
- SLA tracking is active
- Notes and stages can be updated by assigned users