# Team Management System - Enhanced CRM

## Overview
The CRM now includes a comprehensive team management system with automatic lead assignment, SLA tracking, and hierarchical team structure.

## New Features

### 1. Team Management
- **321 Team Members**: Complete organizational hierarchy imported
- **Role-based Structure**: 
  - Admin
  - Sales Director - T1
  - TEAM Head - T2  
  - Team leader - t3
  - Sales Manager - T4
  - Sales Executive - T5
  - Telecaller - T6
  - BROKER
  - Commercial

### 2. Automatic Lead Assignment
- **Round Robin Assignment**: New leads automatically assigned to available team members
- **30-minute SLA**: Leads must be attended within 30 minutes
- **Auto-reassignment**: Overdue leads automatically reassigned to next available person

### 3. Lead Stages & Tracking
- **Lead Stages**: New, Contacted, Interested, Not Interested, Site Visit, Hot, Warm, Cold, Dead, Converted
- **Stage Updates**: Team members can update lead stages
- **Notes System**: Add notes and follow-ups to leads

### 4. Enhanced Dashboard
- **Sidebar Navigation**: Fixed left sidebar with organized menu
- **Team Statistics**: Team member count, assigned leads, overdue leads
- **Stage Overview**: Visual breakdown of leads by stage
- **Assignment Status**: See who leads are assigned to

## New Pages

### Team Members (`/team/`)
- View all team members with hierarchy
- See roles and contact information
- Team overview statistics

### Lead Detail (Enhanced)
- **Assignment Section**: Assign leads to team members
- **Stage Management**: Update lead stages
- **Notes System**: Add and view notes/follow-ups
- **Assignment History**: See who lead is assigned to

### My Leads (`/my-leads/`)
- View leads assigned to current user
- Filter by stage and status

## Technical Implementation

### Models Added
- `TeamMember`: Team member information and hierarchy
- `LeadAssignment`: Lead assignment with SLA tracking
- `LeadNote`: Notes and follow-ups on leads
- `LeadStage`: Lead stage definitions

### Management Commands
- `import_team_members`: Import team member data
- `import_all_team`: Import complete team hierarchy
- `monitor_sla`: Check and reassign overdue leads

### SLA Monitoring
- **Automatic**: Run `python monitor_sla.py` every 5 minutes via cron
- **Manual**: Use management command `python manage.py monitor_sla`

## Setup Instructions

1. **Apply Migrations**:
   ```bash
   python manage.py migrate
   ```

2. **Import Team Members**:
   ```bash
   python manage.py import_all_team
   ```

3. **Setup SLA Monitoring** (Optional):
   ```bash
   # Add to crontab for automatic monitoring
   */5 * * * * cd /path/to/drip && python monitor_sla.py
   ```

## API Endpoints

### Team Management
- `POST /assign-lead/`: Assign lead to team member
- `POST /update-stage/`: Update lead stage
- `POST /add-note/`: Add note to lead
- `GET /team/`: View team members

### Lead Management
- `GET /my-leads/`: View assigned leads
- `GET /leads/<id>/`: Enhanced lead detail with assignment

## Usage

### Assigning Leads
1. Go to lead detail page
2. Select team member from dropdown
3. Click "Assign Lead"
4. Lead is assigned with 30-minute SLA

### Updating Stages
1. On lead detail page
2. Select new stage from dropdown
3. Click "Update Stage"
4. Stage is updated and lead marked as attended

### Adding Notes
1. On lead detail page
2. Enter note in text area
3. Click "Add Note"
4. Note is saved with timestamp and user

### Monitoring SLA
- Dashboard shows overdue leads count
- Overdue leads automatically reassigned every 5 minutes
- Manual reassignment available via management command

## Hierarchy Structure
```
Gaurav Mavi (Owner)
├── Sales Directors (T1)
│   ├── Team Heads (T2)
│   │   ├── Team Leaders (T3)
│   │   │   ├── Sales Managers (T4)
│   │   │   │   ├── Sales Executives (T5)
│   │   │   │   └── Telecallers (T6)
│   │   │   └── Brokers
│   │   └── Commercial Users
```

## Benefits
1. **Automated Workflow**: No manual lead assignment needed
2. **SLA Compliance**: Ensures timely lead follow-up
3. **Team Accountability**: Clear assignment and tracking
4. **Scalable Structure**: Supports large team hierarchy
5. **Better Conversion**: Systematic lead management process

## Future Enhancements
- Performance metrics per team member
- Lead scoring and priority assignment
- Automated follow-up reminders
- Team performance dashboards
- Integration with communication tools