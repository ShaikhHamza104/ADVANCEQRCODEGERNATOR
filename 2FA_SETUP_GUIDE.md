# 🔐 2FA Authentication Setup Guide

**Version:** 3.1.0  
**Date:** December 18, 2025  
**Status:** ✅ 2FA ENABLED

---

## 🎯 What's New - Two-Factor Authentication

Your application now has **mandatory 2FA (Two-Factor Authentication)** for enhanced security!

### How It Works:

1. **Login with username & password** → Standard login
2. **Enter 6-digit code** → From your authenticator app
3. **Access granted** → Dashboard access

---

## 📱 Setting Up Your Authenticator

### Step 1: Download Authenticator App

Choose one of these apps (all free):
- **Google Authenticator** (iOS/Android)
- **Microsoft Authenticator** (iOS/Android)  
- **Authy** (iOS/Android/Desktop)

### Step 2: Scan QR Code

1. Login to your dashboard
2. Scroll down to "TOTP Authenticator QR Code" section
3. Open your authenticator app
4. Tap "Add" or "+" button
5. Scan the QR code displayed on screen
6. Your account will be added with 6-digit rotating codes

### Step 3: Login with 2FA

1. Go to login page
2. Enter username and password
3. Click "Sign In"
4. **NEW:** You'll be redirected to 2FA verification page
5. Open your authenticator app
6. Enter the current 6-digit code
7. Click "Verify & Continue"
8. ✓ You're in!

---

## 🆘 Lost Access to Authenticator?

### Account Recovery Process:

1. Go to login page
2. Click **"Lost access to authenticator?"**
3. Fill out recovery form:
   - Your username
   - Your registered email
   - Reason for recovery (optional)
4. Submit request
5. Admin will receive email at: **kmohdhamza10@gmail.com**
6. Admin will reset your 2FA
7. You'll receive email notification
8. Login and scan new QR code

---

## 👨‍💼 Admin Features

### Reset User 2FA

If a user loses access:

1. Login as admin
2. Go to **User Management**
3. Find the user
4. Click **"Reset 2FA"** button
5. Confirm action
6. New TOTP profile generated
7. User receives email notification
8. User can scan new QR code

### Recovery Email Notifications

All recovery requests are sent to: **kmohdhamza10@gmail.com**

Email includes:
- User details (username, email, ID)
- Reason for recovery
- IP address and timestamp
- Direct link to user management

---

## 🔒 Security Features

### What's Protected:

✅ **Login requires 2FA** - Mandatory for all users  
✅ **Codes rotate every 30 seconds** - Time-based security  
✅ **Encrypted TOTP seeds** - AES-256-GCM encryption  
✅ **Audit logging** - All 2FA events tracked  
✅ **Account recovery** - Admin-approved process  
✅ **Email notifications** - User informed of changes

### Audit Events Logged:

- `2FA_SUCCESS` - Successful verification
- `2FA_FAILED` - Invalid code attempt
- `ACCOUNT_RECOVERY_REQUEST` - User requests help
- `ADMIN_2FA_RESET` - Admin resets user 2FA

---

## 🧪 Testing 2FA

### For Development/Testing:

You can see the current code for testing purposes:

```python
from core.totp import TOTPProfile

# Get user's profile
profile = TOTPProfile.get_by_user_id("USER_ID")

# Generate current code (admin only)
current_code = profile.generate_current_code()
print(f"Current 2FA code: {current_code}")
```

**Note:** This is for testing only. In production, users must use their authenticator apps.

---

## 📋 Troubleshooting

### Code Not Working?

- ✓ Check time sync on your device
- ✓ Ensure code hasn't expired (30-second window)
- ✓ Codes are case-sensitive (numbers only)
- ✓ Make sure you're using the latest code

### Can't Scan QR Code?

- ✓ Download QR code image
- ✓ Use manual entry in authenticator app
- ✓ Contact admin for 2FA reset

### OAuth Login (Google)?

- Google OAuth users get 2FA automatically
- First Google login creates TOTP profile
- Subsequent logins require 2FA code
- Same process as regular users

---

## 🎯 Quick Reference

### URLs:

- **Login:** `/login/`
- **2FA Verification:** `/verify-2fa/`
- **Account Recovery:** `/account-recovery/`
- **Dashboard (QR Code):** `/dashboard/`
- **Admin Reset 2FA:** `/admin/reset-2fa/<user_id>/`

### Templates:

- `registration/login.html` - Login page
- `registration/verify_2fa.html` - 2FA verification
- `registration/account_recovery.html` - Recovery request
- `admin_reset_2fa.html` - Admin reset confirmation

### Models:

- `TOTPProfile.verify_totp(code)` - Verify 6-digit code
- `TOTPProfile.generate_current_code()` - Get current code
- `AuditLog` - Track all 2FA events

---

## 🚀 Production Checklist

### Before Going Live:

- [ ] Configure email settings (SMTP)
- [ ] Test account recovery flow
- [ ] Verify admin email (kmohdhamza10@gmail.com)
- [ ] Test 2FA with real authenticator apps
- [ ] Check audit logs are working
- [ ] Ensure email notifications sent
- [ ] Update documentation for users

### Email Configuration:

Add to `.env`:
```bash
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=KTVS <noreply@yourdomain.com>
```

---

## 📊 Statistics & Monitoring

### Track 2FA Usage:

```python
# Count 2FA events
from core.mongo import db

# Successful logins
db.audit_logs.count_documents({"event_type": "2FA_SUCCESS"})

# Failed attempts
db.audit_logs.count_documents({"event_type": "2FA_FAILED"})

# Recovery requests
db.audit_logs.count_documents({"event_type": "ACCOUNT_RECOVERY_REQUEST"})
```

---

## ✅ Benefits of 2FA

1. **Enhanced Security** - Two layers of protection
2. **Prevents Unauthorized Access** - Password alone isn't enough
3. **Industry Standard** - Meets compliance requirements
4. **User Control** - Own device = own security
5. **Audit Trail** - Complete logging of access
6. **Easy Recovery** - Admin can help lost users

---

## 📝 Update Log

**v3.1.0 (December 18, 2025)**
- ✅ Added mandatory 2FA for all logins
- ✅ Created 2FA verification page
- ✅ Account recovery system
- ✅ Admin 2FA reset functionality
- ✅ Email notifications to admin
- ✅ Audit logging for all 2FA events
- ✅ pyotp library integration
- ✅ TOTP code verification (30-second window)

---

**Need Help?** Contact admin at kmohdhamza10@gmail.com

**Documentation:** See [README.md](README.md) for full system documentation
