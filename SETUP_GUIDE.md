# KTVS Setup & Configuration Guide

## Table of Contents
1. [Quick Start](#quick-start)
2. [Subscription Plans](#subscription-plans)
3. [Creating Coupon Codes](#creating-coupon-codes)
4. [User Management](#user-management)
5. [Password Management](#password-management)
6. [MongoDB Setup](#mongodb-setup)
7. [OAuth Configuration](#oauth-configuration)
8. [Production Deployment](#production-deployment)

---

## Quick Start

### 1. Initial Setup

```bash
# Clone and navigate to project
cd ADVANCEQRCODEGERNATOR

# Run the start script (handles everything automatically)
./start.bat  # Windows
./start.sh   # Linux/Mac
```

### 2. Access the Application

- **Homepage:** http://localhost:8000
- **Login:** http://localhost:8000/login
- **Admin Dashboard:** http://localhost:8000/admin-dashboard
- **Pricing:** http://localhost:8000/pricing

### 3. Default Admin Account

```
Username: admin
Password: admin123
Email: admin@ktvs.com
```

**⚠️ Change this password immediately in production!**

---

## Subscription Plans

### Plan Overview

| Feature | Free | Pro | Enterprise |
|---------|------|-----|------------|
| QR Codes | 3 | 50 | Unlimited |
| Storage | 100MB | 1GB | Unlimited |
| API Calls/Day | 100 | 10,000 | Unlimited |
| Priority Support | ❌ | ✅ | ✅ |
| Custom Branding | ❌ | ✅ | ✅ |
| Advanced Analytics | ❌ | ❌ | ✅ |
| **Monthly Price** | **$0** | **$9.99** | **$49.99** |
| **Yearly Price** | **$0** | **$99.99** | **$499.99** |

### How Users Upgrade

1. Navigate to `/pricing`
2. Select desired plan
3. Choose billing cycle (monthly/yearly)
4. Click "Upgrade" button
5. (In production: Complete payment via Stripe)

---

## Creating Coupon Codes

### Using Django Shell

```bash
python manage.py shell
```

```python
from core.subscription import CouponSystem

# Create a 50% off coupon for Pro plan
CouponSystem.create_coupon(
    code='WELCOME50',
    discount_percent=50,
    plan_type='PRO',
    max_uses=100,
    expiry_days=30
)

# Create a 25% off coupon for Enterprise plan
CouponSystem.create_coupon(
    code='ENTERPRISE25',
    discount_percent=25,
    plan_type='ENTERPRISE',
    max_uses=50,
    expiry_days=60
)

# Create unlimited use promotional code
CouponSystem.create_coupon(
    code='PROMO2024',
    discount_percent=30,
    plan_type='PRO',
    max_uses=999999,
    expiry_days=365
)
```

### Coupon Parameters

- **code:** Unique coupon code (alphanumeric, uppercase)
- **discount_percent:** Discount percentage (0-100)
- **plan_type:** Target plan ('FREE', 'PRO', 'ENTERPRISE')
- **max_uses:** Maximum number of times code can be used
- **expiry_days:** Days until expiration from creation

### How Users Apply Coupons

1. Go to `/pricing`
2. Enter coupon code in the form
3. Select billing cycle
4. Click "Apply"
5. Subscription is upgraded with discount

---

## User Management

### Create Users via Admin

```bash
python manage.py createsuperuser
```

### Programmatic User Creation

```python
from django.contrib.auth.models import User
from core.subscription import SubscriptionManager
from core.totp import TOTPProfile
import secrets
import string

# Create user
user = User.objects.create_user(
    username='newuser',
    email='user@example.com',
    password='securepassword123'
)

# Create TOTP profile
alphabet = string.ascii_uppercase + '234567'
seed = ''.join(secrets.choice(alphabet) for _ in range(32))

TOTPProfile.create(
    user_id=str(user.id),
    seed=seed,
    metadata={
        "label": user.username,
        "issuer": "KTVS",
        "digits": 6,
        "period": 30,
        "algorithm": "SHA1"
    },
    kelley_attributes={
        "role": "User",
        "function": "Standard Access"
    },
    security_flags={
        "is_high_privilege": False,
        "is_private": False,
        "revocation_state": "Active"
    },
    actor={"user_id": "system", "ip_address": "127.0.0.1", "user_agent": "Script"}
)

# Create subscription (defaults to FREE)
SubscriptionManager.create_subscription(str(user.id), 'FREE')
```

### Upgrade User Manually

```python
from core.subscription import SubscriptionManager

# Upgrade user to Pro
SubscriptionManager.upgrade_subscription(
    user_id='1',  # User ID
    new_plan_type='PRO',
    billing_cycle='monthly'
)

# Upgrade to Enterprise with yearly billing
SubscriptionManager.upgrade_subscription(
    user_id='1',
    new_plan_type='ENTERPRISE',
    billing_cycle='yearly'
)
```

---

## Password Management

### User Password Change

Users can change their password:
1. Login to account
2. Click username dropdown
3. Select "Change Password"
4. Enter current password
5. Enter and confirm new password
6. Submit

### Admin Password Reset

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User

# Reset password for a user
user = User.objects.get(username='username')
user.set_password('newpassword123')
user.save()

print(f"Password reset for {user.username}")
```

### Forgot Password (Production)

In production, configure email settings in `.env`:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@ktvs.com
```

---

## MongoDB Setup

### Local MongoDB

```bash
# Install MongoDB
# Windows: Download from https://www.mongodb.com/try/download/community
# Linux: sudo apt-get install mongodb
# Mac: brew install mongodb-community

# Start MongoDB
mongod --dbpath /path/to/data
```

### MongoDB Atlas (Cloud)

1. Create account at https://www.mongodb.com/cloud/atlas
2. Create a free cluster
3. Get connection string
4. Update `.env`:

```env
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/ktvs?retryWrites=true&w=majority
```

### Verify Connection

```bash
python manage.py shell
```

```python
from core.mongo import db

# Test connection
print(db.list_collection_names())
# Should show: ['totp_profiles', 'audit_logs', 'subscriptions', 'coupons']
```

---

## OAuth Configuration

### Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URIs:
   - `http://localhost:8000/complete/google-oauth2/`
   - `http://127.0.0.1:8000/complete/google-oauth2/`
6. Update `.env`:

```env
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=your-client-id.apps.googleusercontent.com
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=your-client-secret
```

### GitHub OAuth

1. Go to [GitHub Settings](https://github.com/settings/developers)
2. Create new OAuth App
3. Set callback URL: `http://localhost:8000/complete/github/`
4. Update `.env`:

```env
SOCIAL_AUTH_GITHUB_KEY=your-github-client-id
SOCIAL_AUTH_GITHUB_SECRET=your-github-client-secret
```

---

## Production Deployment

### Environment Configuration

```env
# Security
SECRET_KEY=your-production-secret-key-minimum-50-characters-long
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Encryption
ENCRYPTION_KEY=your-32-character-encryption-key!!

# Database
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/ktvs_prod

# HTTPS Settings
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
```

### Deployment Checklist

- [ ] Set `DEBUG=False`
- [ ] Configure strong `SECRET_KEY` and `ENCRYPTION_KEY`
- [ ] Set proper `ALLOWED_HOSTS`
- [ ] Configure MongoDB with authentication
- [ ] Enable HTTPS/SSL
- [ ] Set up email backend for password resets
- [ ] Configure static files (`collectstatic`)
- [ ] Set up Gunicorn or uWSGI
- [ ] Configure Nginx/Apache reverse proxy
- [ ] Set up SSL certificates (Let's Encrypt)
- [ ] Configure firewall rules
- [ ] Set up monitoring and logging
- [ ] Enable rate limiting
- [ ] Configure backups

### Gunicorn Setup

```bash
# Install
pip install gunicorn

# Run
gunicorn ktvs.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location /static/ {
        alias /path/to/staticfiles/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Troubleshooting

### MongoDB Connection Issues

**Error:** "Warning: MongoDB connection failed"

**Solutions:**
1. Check MongoDB is running: `systemctl status mongod`
2. Verify connection string in `.env`
3. Check network connectivity
4. Application will fallback to in-memory storage

### OAuth Login Not Working

**Solutions:**
1. Verify OAuth credentials in `.env`
2. Check redirect URIs match exactly
3. Clear browser cache and cookies
4. Check OAuth app is not suspended

### Subscription Not Created

**Solutions:**
```python
# Manually create subscription
from core.subscription import SubscriptionManager

SubscriptionManager.create_subscription(
    user_id='USER_ID_HERE',
    plan_type='FREE'
)
```

### Static Files Not Loading

```bash
# Collect static files
python manage.py collectstatic --noinput
```

---

## Support & Resources

- **Documentation:** README.md
- **Issues:** GitHub Issues
- **Email:** support@ktvs.example.com

---

**KTVS Enterprise** - Secured with AES-256-GCM | NIST Compliant
