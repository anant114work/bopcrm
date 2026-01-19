# Form Source Mapping Guide

## Overview
The Form Source Mapping feature allows you to assign specific lead forms to projects, ensuring leads are automatically filtered and organized by project.

## Features

### 1. Map Forms to Projects
- Assign any lead form (from Meta/Facebook) to a specific project
- Leads from mapped forms will automatically be associated with the project
- Active/Inactive toggle for temporary disabling without deletion

### 2. Automatic Lead Filtering
- When viewing a project, only leads from mapped forms are shown
- Fallback to keyword matching if no exact mapping exists
- Works with all existing project features (WhatsApp, analytics, etc.)

### 3. Easy Management
- View all form mappings in one place
- See which forms are mapped to which projects
- Quick add/edit/delete functionality
- Auto-complete from existing form names

## How to Use

### Step 1: Access Form Mappings
1. Navigate to **Properties → Form Mappings** in the menu
2. You'll see a list of all current mappings

### Step 2: Create a New Mapping
1. Click **"+ Add Mapping"** button
2. Select or type the form name (auto-complete available)
3. Select the target project from dropdown
4. Click **"Save"**

### Step 3: Manage Mappings
- **Activate/Deactivate**: Toggle status without deleting
- **Delete**: Remove mapping permanently
- **View**: See all mappings in a table

## Example Use Cases

### Case 1: Multiple Projects
```
Form: "Gaur Yamuna City - Lead Form"  →  Project: Gaur Yamuna City
Form: "Chrysalis - Contact Form"     →  Project: Chrysalis
Form: "BOP Realty - Inquiry"         →  Project: BOP Realty
```

### Case 2: Multiple Forms per Project
```
Form: "Gaur YC - Facebook"    →  Project: Gaur Yamuna City
Form: "Gaur YC - Instagram"   →  Project: Gaur Yamuna City
Form: "Gaur YC - Website"     →  Project: Gaur Yamuna City
```

## Technical Details

### Database Migration
Run the migration to create the FormSourceMapping table:
```bash
python manage.py migrate
```

### How It Works
1. When syncing leads from Meta, the form name is captured
2. System checks for exact form name match in mappings
3. If found, lead is associated with that project
4. If not found, falls back to keyword matching (existing behavior)

### API Endpoints
- `GET /form-mappings/` - List all mappings
- `POST /form-mappings/create/` - Create new mapping
- `POST /form-mappings/<id>/toggle/` - Toggle active status
- `POST /form-mappings/<id>/delete/` - Delete mapping

## Benefits

1. **Precise Control**: Exact form-to-project mapping
2. **Easy Management**: Visual interface for all mappings
3. **Flexible**: Can activate/deactivate without deletion
4. **Backward Compatible**: Works with existing keyword system
5. **Auto-Complete**: Suggests existing form names

## Notes

- Form names are case-insensitive for matching
- One form can only be mapped to one project at a time
- Inactive mappings are ignored but preserved in database
- Changes take effect immediately for new leads
- Existing leads are not affected by new mappings
