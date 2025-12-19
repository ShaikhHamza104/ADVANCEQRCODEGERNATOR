# Kelley Token Validation System (KTVS) v3.0.0-Enterprise

**🎉 Updated December 18, 2025 - Production Ready with QR History!**

A production-grade MFA management platform designed to enforce Kelley-Approved Notary protocols with advanced UI and enterprise security features.

## ✅ Latest Updates (December 18, 2025)

### NEW: User QR Code History! 🎯

**Latest Features:**
- ✅ **QR History System** - Users can view, regenerate, and manage their QR codes
- ✅ **Favorites Feature** - Mark frequently used QR codes as favorites
- ✅ **Secure History** - Ownership verification, separate from admin logs
- ✅ **Production Ready** - Complete cleanup and deployment guide
- ✅ **Code Cleanup** - Removed duplicate files, optimized codebase

**First Round:**
- ✅ **GitHub OAuth Login** - Properly configured and working
- ✅ **Instant QR Generator** - Now requires authentication with formal login message
- ✅ **QR Usage Counter** - Fixed increment tracking
- ✅ **Auto-Refresh Bug** - Removed page reload after QR generation
- ✅ **Enterprise Display** - Shows "Unlimited" instead of numeric quota
- ✅ **Code Cleanup** - Removed 24 unnecessary files and debug code

**Second Round (Live Preview & Quota):**
- ✅ **Live Preview Updates** - Quota counter now updates in real-time without page refresh
- ✅ **Accurate Quota Display** - Fixed "1 of 50 used" showing incorrect data
- ✅ **Admin Plan** - Admins now get ENTERPRISE (unlimited) instead of PRO (500)
- ✅ **Real-time DOM Updates** - Badge colors, progress bars, and counts update instantly

📖 [First Round Fixes →](FIXES_APPLIED.md) | [Live Preview Fixes →](LIVE_PREVIEW_AND_QUOTA_FIXES.md)

---

## 🌟 Features

### Security
- **Framework:** Django 5.2.9
- **Database:** MongoDB Atlas (via PyMongo) with SQLite fallback for in-memory storage
- **Encryption:** AES-256-GCM for TOTP seed storage
- **Authentication:** OAuth2 (Google, GitHub) + Traditional username/password
- **Compliance:** NIST SP 800-63B standards
- **Audit Logging:** Immutable audit trails for all operations

### Advanced UI
- **Modern Design:** Gradient backgrounds, animations, and responsive layout
- **Bootstrap 5.3:** Professional UI components
- **Bootstrap Icons:** Rich iconography
- **Animate.css:** Smooth animations and transitions
- **Real-time Feedback:** Toast notifications and alerts

### Core Functionality
- ✅ User Registration & Login (Traditional + OAuth2)
- ✅ **Authenticated QR Generator** (Login Required for Security)
- ✅ **QR Code History** - View, regenerate, and manage your QR codes (NEW)
- ✅ **Favorites System** - Mark frequently used QR codes (NEW)
- ✅ **Enterprise Plan: Unlimited QR Codes**
- ✅ **Proper Usage Tracking** (Counter increments correctly)
- ✅ **Live Preview** (Real-time QR preview without consuming quota)
- ✅ **Platform Optimization** (10 device-specific presets)
- ✅ Automatic TOTP Profile Generation
- ✅ QR Code Generation for Authenticator Apps
- ✅ Admin Dashboard with User Management
- ✅ Profile Detail Views
- ✅ Audit History Tracking (Admin Only)
- ✅ Role-based Access Control
- ✅ Security Flags (High Privilege, Private Profiles)
- ✅ Kelley Attributes Management

## 🎯 Quick Start

**No login required!** Test immediately:

1. Start server: `python manage.py runserver`
2. Visit: `http://127.0.0.1:8000/`
3. Scroll to "Instant QR Generator"
4. Enter any URL (e.g., `https://github.com`)
5. Select size preset (Mobile, 16:9, iOS, etc.)
6. Click "Generate" - QR code appears instantly!

✨ **Choose from 8 size presets:**
- Standard (512x512) - General use
- Small (256x256) - Mobile optimized
- Large (1024x1024) - Print quality
- **16:9 Widescreen** - HD displays
- **Mobile Portrait** - Smartphones
- **iOS Optimized** - iPhone/iPad
- **Android Optimized** - Android devices
- **1:1 Square** - Social media

## 📋 Prerequisites

- Python 3.11+
- MongoDB (Optional - falls back to in-memory storage)
- `uv` package manager

## 📚 Documentation Hub

### Getting Started
- 🚀 [Quick Start Guide](START_HERE.md) - Begin here!
- 📖 [Setup Guide](SETUP_GUIDE.md) - Detailed installation
- 🎯 [Verification Guide](VERIFICATION_GUIDE.md) - Test all features

### OAuth Setup
- 🔐 [OAuth Setup Guide](OAUTH_SETUP_GUIDE.md) - **NEW!** Complete OAuth configuration
- 🔑 [OAuth Quick Reference](OAUTH_QUICK_REFERENCE.md) - Quick tips

### Features & Usage
- ✨ [Features Overview](FEATURES.md) - All features explained
- 🎨 [QR Customization](QR_CUSTOMIZATION_GUIDE.md) - Size presets & options
- 💳 [Admin & User Management](ADMIN_USER_MANAGEMENT.md)

### Recent Updates
- 🐛 [Bug Fixes Summary](BUG_FIXES_SUMMARY.md) - **NEW!** What was fixed
- 📝 [Updates Log](UPDATES.md) - Version history

### Testing & Deployment
- 🧪 Test Suite: Run `python test_all_fixes.py`
- 🚀 [Production Deployment](PRODUCTION_DEPLOYMENT.md)
- ✅ [Production Checklist](PRODUCTION_CHECKLIST.md)

---

## 🚀 Quick Start

### Option 1: Automated Startup (Recommended)

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

This will automatically install dependencies, run migrations, and start the server.

### Option 2: Manual Setup

#### 1. Install Dependencies

```bash
uv sync
```

#### 2. Environment Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

Then edit `.env` with your configuration. For development, the default values work fine.

> **Note:** See [OAUTH_SETUP.md](OAUTH_SETUP.md) for detailed OAuth2 setup instructions.

#### 3. Database Setup

Run migrations for Django authentication:

```bash
uv run python manage.py migrate
```

Seed initial data (creates 5 sample TOTP profiles):

```bash
uv run python manage.py seed_data
```

Create an admin user:

```bash
uv run python manage.py createsuperuser
# Or use the pre-created admin account:
# Username: admin
# Password: admin123
```

#### 4. Run Server

```bash
uv run python manage.py runserver
```

Access the application at: **http://127.0.0.1:8000**

## 👥 Default Accounts

### Admin Account
- **Username:** admin
- **Email:** admin@ktvs.com
- **Password:** admin123

### Sample TOTP Profiles
The seed data creates profiles for:
1. April.O'Bryan@ProgInv.gov
2. stephenneer@gmail.com
3. vinod.sharma@aro-usa.gov
4. chimbu_agarwal_1977
5. anish.macro@asa.gov

## 📁 Project Structure

```
D:\ADVANCEQRCODEGERNATOR\
├── ktvs/                       # Project settings
│   ├── settings.py            # Django configuration
│   ├── urls.py                # Main URL routing
│   └── wsgi.py                # WSGI application
├── core/                      # Main application
│   ├── models.py              # Data models (TOTPProfile, AuditLog)
│   ├── views.py               # View controllers
│   ├── urls.py                # App URL routing
│   ├── mongo.py               # MongoDB connection with fallback
│   ├── crypto.py              # AES-256-GCM encryption utilities
│   ├── templates/             # HTML templates
│   │   ├── base.html          # Base template with advanced UI
│   │   ├── home.html          # Landing page
│   │   ├── dashboard.html     # User dashboard
│   │   ├── admin_dashboard.html  # Admin panel
│   │   ├── profile_detail.html   # Profile details
│   │   ├── create_profile.html   # Create new profile
│   │   └── registration/      # Auth templates
│   │       ├── login.html     # Login page
│   │       └── register.html  # Registration page
│   └── management/commands/
│       └── seed_data.py       # Database seeding command
├── db.sqlite3                 # SQLite database (Django auth)
├── .env                       # Environment configuration
├── pyproject.toml             # Project dependencies
└── README.md                  # This file
```

## 🎨 UI Features

### Modern Design Elements
- **Gradient Backgrounds:** Purple gradient theme
- **Card-based Layout:** Clean, organized content
- **Responsive Design:** Mobile-friendly interface
- **Animated Transitions:** Smooth fade-in effects
- **Icon Integration:** Bootstrap Icons throughout
- **Glass Morphism:** Backdrop blur effects
- **Hover Effects:** Interactive button animations

### Pages

1. **Home Page** - Feature showcase with call-to-action
2. **Login Page** - OAuth2 + Traditional login
3. **Register Page** - Account creation with auto TOTP profile
4. **Dashboard** - User profile, QR code, audit logs
5. **Admin Dashboard** - User management, statistics
6. **Profile Detail** - Detailed profile view (admin only)
7. **Create Profile** - New profile creation (admin only)

## 🔐 Security Features

### Encryption
- **AES-256-GCM:** TOTP seeds encrypted before storage
- **Unique Nonces:** Each encryption uses random nonce
- **Base64 Encoding:** Safe storage format

### Audit Logging
- Every profile access logged
- Immutable audit trail
- Actor tracking (user, IP, user agent)
- Event types: PROFILE_CREATED, VIEW_SEED, PROFILE_MODIFIED

### Access Control
- Login required for sensitive pages
- Admin-only routes protected
- Profile ownership verification
- Session security (HTTPONLY, SAMESITE)

## 📊 MongoDB vs In-Memory Storage

The application intelligently falls back to in-memory storage if MongoDB is unavailable:

### With MongoDB
- Persistent storage across restarts
- Production-ready scalability
- Full audit trail retention

### Without MongoDB (Fallback)
- In-memory storage for development
- Data lost on restart
- Fully functional for testing

## 🛠️ Management Commands

### Seed Data
```bash
uv run python manage.py seed_data
```
Creates 5 sample TOTP profiles with various configurations.

### Create Superuser
```bash
uv run python manage.py createsuperuser
```

### Run Migrations
```bash
uv run python manage.py migrate
```

## 🔧 Configuration Options

### Session Security
- `SESSION_COOKIE_HTTPONLY = True`
- `SESSION_COOKIE_SAMESITE = 'Lax'`
- `SESSION_COOKIE_SECURE = True` (False in DEBUG mode)

### OAuth2 Providers
- Google OAuth2
- GitHub OAuth

### TOTP Configuration
- Algorithm: SHA1
- Digits: 6
- Period: 30 seconds

## 📱 Compatible Authenticator Apps

- Google Authenticator
- Microsoft Authenticator
- Authy
- 1Password
- LastPass Authenticator
- Any TOTP-compatible app

## 🚀 Deployment Notes

### Production Checklist
1. Set `DEBUG=False` in `.env`
2. Configure proper `SECRET_KEY`
3. Set up MongoDB Atlas or local MongoDB
4. Configure OAuth2 credentials
5. Enable HTTPS for `SESSION_COOKIE_SECURE`
6. Set up proper `ALLOWED_HOSTS`
7. Configure static files serving
8. Set up proper logging

### Environment Variables
All sensitive configuration in `.env`:
- `SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode (True/False)
- `MONGO_URI` - MongoDB connection string
- OAuth2 credentials (optional)

## 🧪 Testing

### Manual Testing
1. Register a new account → TOTP profile auto-created
2. Login → View dashboard with QR code
3. Scan QR code with authenticator app
4. Admin login → Access admin dashboard
5. Create new profile → Test admin functionality

### Admin Access
- URL: http://127.0.0.1:8000/admin-dashboard/
- Django Admin: http://127.0.0.1:8000/admin/

## 📖 Additional Resources

- [OAUTH_SETUP.md](OAUTH_SETUP.md) - OAuth2 configuration guide
- Django Documentation: https://docs.djangoproject.com/
- MongoDB Documentation: https://docs.mongodb.com/
- Bootstrap Documentation: https://getbootstrap.com/

## 🐛 Troubleshooting

### MongoDB Connection Failed
- **Message:** "Warning: MongoDB connection failed"
- **Solution:** System automatically falls back to in-memory storage. For production, ensure MongoDB is running.

### OAuth2 Login Not Working
- **Solution:** Configure OAuth2 credentials in `.env` and follow [OAUTH_SETUP.md](OAUTH_SETUP.md)

### Static Files Not Loading
- **Solution:** Run `python manage.py collectstatic` for production

## 📝 License

This project is part of the Kelley Token Validation System (KTVS) Enterprise.

## 🤝 Contributing

1. Follow Django best practices
2. Maintain code documentation
3. Update tests for new features
4. Follow the existing code style

## 📞 Support

For issues and questions, please refer to the project documentation or contact your system administrator.

---

**KTVS Enterprise v2.0.0** - Secured with AES-256-GCM Encryption | NIST SP 800-63B Compliant
