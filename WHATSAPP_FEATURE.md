# WhatsApp Bulk Messaging Feature

## Overview
Send WhatsApp template messages to all leads of a particular project in bulk.

## How to Access

### Option 1: From Projects List Page
1. Go to **Projects** page (`/projects/`)
2. Find the project you want to send messages to
3. Click the green **"Send WhatsApp"** button on the project card

### Option 2: From Project Detail Page
1. Go to **Projects** page (`/projects/`)
2. Click **"View Details"** on any project
3. Click the **"📢 Bulk WhatsApp"** button in the top-right section

### Direct URL
- `/projects/{project_id}/bulk-whatsapp/`

## Features

### 1. Send to All Leads
- Automatically sends to all leads with valid phone numbers
- Shows total count before sending
- Real-time progress feedback

### 2. Send to Selected Leads
- Select specific leads using checkboxes
- "Select All" option available
- Send only to chosen leads

### 3. Template Selection
- Choose from available WhatsApp templates for the project
- Preview selected campaign
- Uses project-specific templates

### 4. Smart Features
- Only sends to leads with phone numbers
- Automatically formats phone numbers (adds +91 prefix)
- Randomly selects project images to attach
- Personalizes messages with lead names
- Tracks sent/failed messages
- Creates message records for tracking

## Statistics Shown
- Total leads in project
- Leads with phone numbers
- Available templates
- Success/failure counts after sending

## Message Details
Each message includes:
- Lead's name (personalized)
- Project image (random from uploaded images)
- Template content
- Source tracking (form name)

## API Response
After sending, you'll see:
- ✅ Success message with count
- Number of messages sent successfully
- Number of failed messages

## Requirements
- Project must have WhatsApp templates configured
- Leads must have valid phone numbers
- AISensy API configuration must be set up

## Example Workflow

1. **Navigate**: Go to Projects → Select Project → Click "Send WhatsApp"
2. **Select Campaign**: Choose a WhatsApp template from dropdown
3. **Choose Recipients**: 
   - Click "Send to All Leads" for everyone
   - OR select specific leads and click "Send to Selected Leads"
4. **Monitor**: Watch the progress and see results
5. **Verify**: Check success/failure counts

## Button Locations

### Projects List Page
Each project card has a green **"Send WhatsApp"** button with a paper plane icon.

### Project Detail Page
Top-right section has a **"📢 Bulk WhatsApp"** button (admin only).

## Technical Details

### Backend
- **View**: `project_bulk_whatsapp()` in `bulk_whatsapp_views.py`
- **Send Function**: `send_bulk_whatsapp()` in `bulk_whatsapp_views.py`
- **URL**: `/projects/<project_id>/bulk-whatsapp/`

### Features
- Team member filtering (only sees their assigned leads)
- Phone number validation
- Image attachment from project gallery
- Message logging in database
- Error handling for failed sends

### API Integration
- Uses AISensy API for WhatsApp delivery
- Configurable API key and campaign name
- Supports template parameters
- Media attachment support
