# Admin User Management & Email Verification

## Overview
Complete admin control panel for managing users, switching subscription plans, verifying emails, and controlling user access.

## Features Implemented

### 1. Admin User Management Dashboard ✅

**Access:** Only available to superuser/admin accounts  
**URL:** `/admin/users/`

**Features:**
- View all registered users in a comprehensive table
- See user details: username, email, join date, current plan
- Email verification status for each user
- Active/Inactive account status
- Quick action buttons for each user

**User Information Displayed:**
- User ID
- Username (with ADMIN badge for superusers)
- Email address
- Email verification status (Verified/Not Verified)
- Current subscription plan (FREE/PRO/ENTERPRISE)
- Join date
- Account status (Active/Inactive)

### 2. Admin Plan Management ✅

**Change User Plans:**
Admins can switch any user between:
- **FREE Plan** - 50 QR codes, 100MB storage
- **PRO Plan** - 500 QR codes, 1GB storage  
- **ENTERPRISE Plan** - Unlimited everything

**How to Change Plans:**
1. Go to User Management (`/admin/users/`)
2. Click the "Plan" button next to the user
3. Select new plan from dropdown
4. Choose billing cycle (monthly/yearly)
5. Click "Change Plan"
6. Plan updates immediately with success message

**Features:**
- Instant plan switching
- All plan features update automatically
- User's QR quota adjusts immediately
- Billing cycle selection
- Current plan highlighted in modal

### 3. Email Verification System ✅

**Automatic Email Verification:**
- Verification email sent automatically on registration
- Secure token-based verification (24-hour expiration)
- SHA-256 hashed tokens stored in database
- One-time use tokens

**Manual Admin Verification:**
- Admins can manually verify any user's email
- Click "Verify" button in User Management
- Instant verification with confirmation
- Marked as "manually_verified" in database

**User Features:**
- Resend verification email from dashboard
- Email verification warning banner on dashboard
- Verified badge displayed when email is confirmed
- Links expire after 24 hours

**Email Verification Flow:**
```
1. User registers → Verification email sent
2. User clicks link in email → Token validated
3. Email marked as verified → User can login
4. Dashboard shows verified badge ✓
```

### 4. User Account Control ✅

**Enable/Disable Users:**
Admins can:
- Deactivate problematic accounts
- Temporarily suspend users
- Reactivate accounts
- Instant toggle with confirmation

**How it Works:**
1. Click "Disable" button in User Management
2. Confirm action in popup
3. User account becomes inactive
4. User cannot login until reactivated
5. Click "Enable" to restore access

### 5. Email Verification Pages

**Verification Success:**
- Beautiful success message
- Automatic redirect to login
- User-friendly confirmation

**Verification Failure:**
- Clear error messages
- Expired token notification
- Instructions to resend email

## Technical Implementation

### New Files Created:

1. **`core/email_verification.py`** (NEW)
   - EmailVerification class
   - Token generation and validation
   - Email sending functionality
   - Manual verification methods

2. **`core/templates/user_management.html`** (NEW)
   - Admin user management interface
   - Plan switching modals
   - Action buttons for each user

### Modified Files:

1. **`core/views.py`**
   - Added `user_management()` - Display all users
   - Added `admin_change_user_plan()` - Change user subscription
   - Added `admin_verify_email()` - Manual email verification
   - Added `admin_toggle_user_status()` - Enable/disable accounts
   - Added `verify_email()` - Process verification tokens
   - Added `resend_verification_email()` - Resend verification link
   - Updated `register()` - Send verification email on signup
   - Updated `dashboard()` - Show email verification status

2. **`core/urls.py`**
   - `/admin/users/` - User management page
   - `/admin/users/<id>/change-plan/` - Change plan endpoint
   - `/admin/verify-email/<id>/` - Manual verification
   - `/admin/toggle-user/<id>/` - Enable/disable user
   - `/verify-email/<token>/` - Email verification
   - `/resend-verification/` - Resend verification email

3. **`core/templates/dashboard.html`**
   - Email verification warning banner
   - Resend verification button
   - Verified badge next to username

4. **`core/templates/admin_dashboard.html`**
   - Added "Manage Users" button
   - Links to user management page

## Database Collections

### `email_verifications`
```javascript
{
  user_id: String,
  email: String,
  token_hash: String,          // SHA-256 hashed token
  created_at: DateTime,
  expires_at: DateTime,         // 24 hours from creation
  verified: Boolean,
  used: Boolean,
  verified_at: DateTime
}
```

### `user_profiles`
```javascript
{
  user_id: String,
  email_verified: Boolean,
  email_verified_at: DateTime,
  manually_verified: Boolean   // True if admin verified
}
```

## Usage Examples

### For Admins:

**Change User's Plan:**
```
1. Login as admin
2. Navigate to Admin Dashboard
3. Click "Manage Users"
4. Find the user in the table
5. Click "Plan" button
6. Select new plan (FREE/PRO/ENTERPRISE)
7. Choose billing cycle
8. Click "Change Plan"
✓ Success message appears
```

**Manually Verify User Email:**
```
1. Go to User Management
2. Find user with "Not Verified" badge
3. Click "Verify" button
4. Confirm in popup
✓ Email instantly verified
```

**Disable User Account:**
```
1. Go to User Management
2. Find the user
3. Click "Disable" button
4. Confirm action
✓ User account deactivated
```

### For Users:

**Verify Email After Registration:**
```
1. Register for account
2. Check email inbox
3. Click verification link
4. Email verified automatically
5. Login to account
```

**Resend Verification Email:**
```
1. Login to dashboard
2. See "Email Not Verified" warning
3. Click "Resend Email" button
4. Check inbox for new verification link
```

## Security Features

1. **Token Security:**
   - 32-byte URL-safe random tokens
   - SHA-256 hashing before storage
   - One-time use tokens
   - 24-hour expiration
   - Invalidated after use

2. **Admin Authorization:**
   - All admin endpoints check `is_superuser`
   - 403 Forbidden for non-admins
   - CSRF protection on all forms
   - JSON responses for AJAX calls

3. **Email Verification:**
   - Required before full access
   - Dashboard warnings for unverified users
   - Resend capability with rate limiting
   - Secure token transmission

## Email Configuration

**Development Mode:**
```python
# Verification URLs logged to console
DEBUG = True
# Check terminal for verification links
```

**Production Mode:**
```python
# Configure in settings.py:
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'KTVS Enterprise <noreply@ktvs-enterprise.com>'
```

## API Endpoints

### Admin Endpoints (Superuser Only)

**GET `/admin/users/`**
- Display user management interface
- Shows all users with their details
- Returns HTML page

**POST `/admin/users/<user_id>/change-plan/`**
- Change user's subscription plan
- Parameters: `new_plan`, `billing_cycle`
- Redirects to user management

**POST `/admin/verify-email/<user_id>/`**
- Manually verify user's email
- Returns JSON: `{success: true/false}`

**POST `/admin/toggle-user/<user_id>/`**
- Enable or disable user account
- Body: `{is_active: true/false}`
- Returns JSON: `{success: true/false}`

### User Endpoints

**GET `/verify-email/<token>/`**
- Verify email with token
- Redirects to login on success
- Shows error message on failure

**GET `/resend-verification/`**
- Resend verification email
- Requires login
- Returns to dashboard with message

## Testing

### Test Admin Features:
```bash
# 1. Create superuser
python manage.py createsuperuser

# 2. Start server
python manage.py runserver

# 3. Test admin access
http://localhost:8000/admin/users/

# 4. Test plan changing
- Select a user
- Click "Plan" button
- Change to PRO
- Verify subscription updated

# 5. Test email verification
- Click "Verify" on unverified user
- Check user profile for verified status
```

### Test Email Verification:
```bash
# 1. Register new account
# 2. Check console for verification URL
# 3. Visit verification URL
# 4. Check dashboard for verified badge
```

## User Interface

### Admin Dashboard Components:

**User Table Columns:**
- ID, Username, Email
- Email Verified Status (badge)
- Current Plan (colored badge)
- Join Date
- Account Status
- Action Buttons

**Action Buttons:**
- 🔼 **Plan** - Change subscription plan
- ✓ **Verify** - Manually verify email (disabled if already verified)
- ⚡ **Disable/Enable** - Toggle account status

**Color Coding:**
- 🟢 Green - Verified, Active, PRO plan
- 🟡 Yellow - Not Verified, Warning
- 🔴 Red - Admin, ENTERPRISE
- ⚫ Gray - FREE plan, Inactive

## Troubleshooting

**Email Not Sending:**
- Check DEBUG mode (development logs to console)
- Verify EMAIL_BACKEND settings
- Check SMTP credentials
- Review firewall/network settings

**Verification Link Not Working:**
- Check token expiration (24 hours)
- Verify token hasn't been used
- Check URL is complete
- Try resending verification email

**Admin Can't Access User Management:**
- Verify user has `is_superuser=True`
- Check user is logged in
- Clear browser cache
- Check URL is correct

**Plan Not Changing:**
- Verify admin permissions
- Check MongoDB connection
- Review console for errors
- Ensure subscription exists

## Future Enhancements

- Bulk user operations
- Export user data to CSV
- Email verification reminders
- Custom email templates
- User activity analytics
- Plan change history
- Automated plan expiration emails

---

**Last Updated:** December 14, 2025  
**Version:** 1.0.0  
**Module:** Admin User Management & Email Verification
