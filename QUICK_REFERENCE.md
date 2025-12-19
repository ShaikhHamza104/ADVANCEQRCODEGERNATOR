# KTVS Quick Reference Guide

## 🚀 Quick Start

```bash
# Start the application
./start.bat          # Windows
./start.sh           # Linux/Mac

# Access application
http://localhost:8000
```

## 👤 Default Credentials

```
Username: admin
Password: admin123
Email: admin@ktvs.com
```

## 📍 Important URLs

| Page | URL | Access |
|------|-----|--------|
| Homepage | `/` | Public |
| Login | `/login` | Public |
| Register | `/register` | Public |
| Dashboard | `/dashboard` | User |
| Pricing | `/pricing` | User |
| My Subscription | `/subscription` | User |
| Change Password | `/password/change` | User |
| Admin Dashboard | `/admin-dashboard` | Admin |
| Django Admin | `/admin` | Admin |

## 🎫 Pricing Plans

| Plan | QR Codes | Storage | API Calls | Price/Month |
|------|----------|---------|-----------|-------------|
| **Free** | 3 | 100MB | 100 | $0 |
| **Pro** | 50 | 1GB | 10,000 | $9.99 |
| **Enterprise** | ∞ | ∞ | ∞ | $49.99 |

## 🎟️ Sample Coupon Codes

Create coupons:
```bash
python create_coupons.py
```

Generated codes:
- `WELCOME50` - 50% off Pro (100 uses)
- `ENTERPRISE25` - 25% off Enterprise (50 uses)
- `PROMO2024` - 30% off Pro (999 uses)
- `TRIAL100` - 100% off Pro (10 uses)
- `UPGRADE15` - 15% off Pro (500 uses)

## 🔧 Common Commands

### Django Management
```bash
# Run server
python manage.py runserver

# Create superuser
python manage.py createsuperuser

# Run migrations
python manage.py migrate

# Create migrations
python manage.py makemigrations

# Collect static files
python manage.py collectstatic

# Django shell
python manage.py shell
```

### Database Operations
```bash
# Check database
python manage.py dbshell

# Flush database
python manage.py flush
```

## 🔑 User Actions

### Registration
1. Go to `/register`
2. Fill in username, email, password
3. Submit
4. Auto-created: TOTP profile + Free subscription

### Login
1. Go to `/login`
2. Enter credentials or use OAuth
3. Redirected to dashboard

### Upgrade Plan
1. Go to `/pricing`
2. Click "Upgrade" on desired plan
3. Select billing cycle
4. Submit (or apply coupon first)

### Apply Coupon
1. On pricing page
2. Enter coupon code
3. Select billing cycle
4. Click "Apply"

### Change Password
1. Click username dropdown
2. Select "Change Password"
3. Enter current password
4. Enter new password twice
5. Submit

### Logout
- Click username → "Logout"
- Or press Ctrl+L

## 🛠️ Admin Tasks

### Create Coupon (Python Shell)
```python
from core.subscription import CouponSystem

CouponSystem.create_coupon(
    code='SPECIAL50',
    discount_percent=50,
    plan_type='PRO',
    max_uses=100,
    expiry_days=30
)
```

### Upgrade User Subscription
```python
from core.subscription import SubscriptionManager

SubscriptionManager.upgrade_subscription(
    user_id='1',
    new_plan_type='PRO',
    billing_cycle='monthly'
)
```

### Reset User Password
```python
from django.contrib.auth.models import User

user = User.objects.get(username='username')
user.set_password('newpassword')
user.save()
```

### View All Subscriptions
```python
from core.mongo import db

subs = list(db.subscriptions.find())
for sub in subs:
    print(f"{sub['user_id']}: {sub['plan_type']}")
```

## 📊 Monitoring

### Check Subscription Stats
```python
from core.mongo import db

# Count by plan type
free_count = db.subscriptions.count_documents({'plan_type': 'FREE'})
pro_count = db.subscriptions.count_documents({'plan_type': 'PRO'})
enterprise_count = db.subscriptions.count_documents({'plan_type': 'ENTERPRISE'})

print(f"Free: {free_count}")
print(f"Pro: {pro_count}")
print(f"Enterprise: {enterprise_count}")
```

### Check Coupon Usage
```python
from core.mongo import db

coupons = list(db.coupons.find())
for coupon in coupons:
    print(f"{coupon['code']}: {coupon['current_uses']}/{coupon['max_uses']}")
```

## 🔐 Security Checklist

### Development
- [x] DEBUG=True
- [x] Default SECRET_KEY
- [x] HTTP (no SSL)
- [x] Default admin password

### Production
- [ ] DEBUG=False
- [ ] Strong SECRET_KEY (50+ chars)
- [ ] HTTPS enabled
- [ ] Change admin password
- [ ] Configure ALLOWED_HOSTS
- [ ] Set up MongoDB authentication
- [ ] Configure email backend
- [ ] Enable rate limiting
- [ ] Set up monitoring
- [ ] Configure backups

## 🐛 Troubleshooting

### MongoDB Not Connected
**Issue:** "MongoDB connection failed"  
**Solution:** App uses in-memory fallback. For production, configure MongoDB in `.env`

### Subscription Not Created
**Solution:**
```python
from core.subscription import SubscriptionManager
SubscriptionManager.create_subscription('USER_ID', 'FREE')
```

### Coupon Not Working
**Check:**
1. Coupon exists and is active
2. Not expired
3. Usage limit not reached
4. Correct plan type

### Static Files Not Loading
```bash
python manage.py collectstatic --noinput
```

## 📱 Testing Features

### Test Subscription Flow
1. Register new account → Gets Free plan
2. Go to pricing → See all plans
3. Apply coupon code → Get discount
4. Upgrade to Pro → Plan changes
5. View subscription → See usage stats
6. Create QR codes → Quota enforced

### Test Password Management
1. Login → Access account
2. Change password → Update credentials
3. Logout → Session cleared
4. Login with new password → Works

### Test Coupon System
1. Create coupon (admin shell)
2. Apply on pricing page
3. Check subscription upgraded
4. Verify discount applied
5. Check usage incremented

## 📚 Documentation Files

- `README.md` - Project overview
- `SETUP_GUIDE.md` - Complete setup instructions
- `PROJECT_SUMMARY.md` - Implementation details
- `FEATURES.md` - Feature documentation
- `SECURITY_AUDIT.md` - Security guidelines
- `START_HERE.md` - Getting started guide

## 🎯 Key Features

✅ Secure TOTP/QR code management  
✅ 3-tier subscription system  
✅ Coupon code promotions  
✅ OAuth integration (Google, GitHub)  
✅ Password management  
✅ Logout functionality  
✅ Admin dashboard  
✅ Audit logging  
✅ AES-256-GCM encryption  
✅ NIST SP 800-63B compliant  

## 📞 Support

- Documentation: See README.md
- Setup Help: See SETUP_GUIDE.md
- Feature List: See FEATURES.md
- Email: support@ktvs.example.com

---

**KTVS Enterprise v2.0.0**  
Quick Reference Guide
