# Login & User Management Implementation

## Summary

All pages now require login authentication. An admin user has been created with the specified credentials, and a user management page is available for creating and managing users.

## Changes Made

### 1. Login Required Middleware
- **File**: `leads/middleware.py`
- Added `LoginRequiredMiddleware` that enforces authentication on all pages
- Exempt URLs: `/team/login/`, `/webhook/`, `/health/`, `/admin/`, `/static/`, `/media/`
- Automatically redirects unauthenticated users to login page

### 2. Admin User Created
- **Username**: `admin`
- **Password**: `8882443789` (phone number)
- **Role**: Admin
- **Login URL**: `/team/login/`

### 3. User Management System
- **URL**: `/user-management/`
- **Access**: Admin only
- **Features**:
  - Create new users with name, email, phone, and role
  - Edit existing users
  - Toggle user active/inactive status
  - Delete users (except admin)
  - View all users in a table

### 4. New Files Created
- `leads/decorators.py` - Login and admin decorators
- `leads/user_management_views.py` - User management views
- `leads/templates/leads/user_management.html` - User management UI
- `create_admin_login.py` - Script to create/update admin user

### 5. Settings Updated
- Added `LoginRequiredMiddleware` to `MIDDLEWARE` in `crm/settings.py`

### 6. URLs Updated
- Added user management routes to `leads/urls.py`:
  - `/user-management/` - User management page
  - `/create-user/` - Create new user
  - `/update-user/` - Update user
  - `/toggle-user/` - Toggle user status
  - `/delete-user/` - Delete user

## How to Use

### Login as Admin
1. Navigate to `/team/login/`
2. Enter username: `admin`
3. Enter password: `8882443789`
4. Click Login

### Create New Users
1. Login as admin
2. Navigate to `/user-management/`
3. Click "Create New User" button
4. Fill in the form:
   - Name (required)
   - Email (optional)
   - Phone (required) - This will be the user's password
   - Role (select from dropdown)
5. Click "Create User"

### User Login
- Users login with their **first name** as username and **phone number** as password
- Example: If user is "John Doe" with phone "9876543210"
  - Username: `john`
  - Password: `9876543210`

### Manage Users
- **Edit**: Click edit icon to modify user details
- **Toggle Status**: Click toggle icon to activate/deactivate user
- **Delete**: Click delete icon to remove user (admin cannot be deleted)

## Security Features

1. **All pages require authentication** - Unauthenticated users are redirected to login
2. **Role-based access** - Admin-only pages check for admin role
3. **Session-based authentication** - Secure session management
4. **Webhook exemptions** - API webhooks remain accessible for integrations

## Available Roles

- Admin
- Sales Director - T1
- TEAM Head - T2
- Team leader - t3
- Sales Manager - T4
- Sales Executive - T5
- Telecaller - T6
- BROKER
- Commercial

## Notes

- Admin users have full access to all features including user management
- Non-admin users are redirected to their leads page after login
- Phone numbers must be unique across all users
- Email addresses must be unique if provided
- Users can be temporarily disabled without deletion using the toggle feature
