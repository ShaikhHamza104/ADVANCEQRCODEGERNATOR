# KTVS System Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         KTVS ENTERPRISE                         │
│              Advanced QR Code & MFA Management                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │   Home   │  │  Login   │  │ Register │  │ Pricing  │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │Dashboard │  │  Admin   │  │Subscript │  │ Password │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                       APPLICATION LAYER                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Django Views                          │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ • User Management    • Subscription Management          │  │
│  │ • TOTP Profiles      • Coupon System                    │  │
│  │ • QR Generation      • Password Management              │  │
│  │ • Admin Dashboard    • OAuth Integration                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  Business Logic                          │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ • SubscriptionManager  • CouponSystem                   │  │
│  │ • TOTPProfile          • KelleySealDetector             │  │
│  │ • CryptoManager        • AuditLog                       │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        DATA LAYER                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────┐       ┌──────────────────────┐       │
│  │   SQLite Database    │       │   MongoDB Database   │       │
│  ├──────────────────────┤       ├──────────────────────┤       │
│  │ • Users              │       │ • totp_profiles      │       │
│  │ • Sessions           │       │ • audit_logs         │       │
│  │ • OAuth Tokens       │       │ • subscriptions      │       │
│  │ • Admin Data         │       │ • coupons            │       │
│  │                      │       │ • coupon_usage       │       │
│  └──────────────────────┘       └──────────────────────┘       │
│         Django Auth              Business Data Storage         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      SECURITY LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ • AES-256-GCM Encryption (TOTP Seeds)                   │  │
│  │ • Argon2 Password Hashing (NIST Compliant)              │  │
│  │ • CSRF Protection (All Forms)                           │  │
│  │ • Session Security (HTTP-Only, SameSite)                │  │
│  │ • Role-Based Access Control                             │  │
│  │ • Immutable Audit Logging                               │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### User Registration Flow
```
User Registration
    ↓
Create Django User (SQLite)
    ↓
Generate TOTP Profile (MongoDB)
    ↓
Create Free Subscription (MongoDB)
    ↓
Log Creation (Audit Log)
    ↓
Redirect to Login
```

### Subscription Upgrade Flow
```
User Selects Plan
    ↓
Apply Coupon (Optional)
    ↓
Validate Coupon Code
    ↓
Calculate Discount
    ↓
Update Subscription (MongoDB)
    ↓
Log Upgrade Event
    ↓
Redirect to Dashboard
```

### QR Code Generation Flow
```
User Requests QR Code
    ↓
Check Subscription Quota
    ↓
Fetch TOTP Profile
    ↓
Decrypt Seed (AES-256-GCM)
    ↓
Generate OTP URI
    ↓
Create QR Code Image
    ↓
Log Access (Audit)
    ↓
Return QR Code
```

### Coupon Application Flow
```
User Enters Coupon
    ↓
Validate Code Exists
    ↓
Check Expiration Date
    ↓
Check Usage Limit
    ↓
Increment Usage Counter
    ↓
Upgrade Subscription
    ↓
Record Coupon Usage
    ↓
Display Success Message
```

## Component Relationships

```
┌─────────────────┐
│   User Model    │ (Django Auth)
│  - id           │
│  - username     │
│  - email        │
│  - password     │
└────────┬────────┘
         │
         │ 1:1
         ↓
┌─────────────────┐
│ Subscription    │ (MongoDB)
│  - user_id      │
│  - plan_type    │
│  - features     │
│  - usage        │
└────────┬────────┘
         │
         │ 1:many
         ↓
┌─────────────────┐
│ TOTP Profile    │ (MongoDB)
│  - user_id      │
│  - encrypted    │
│  - metadata     │
│  - security     │
└─────────────────┘

┌─────────────────┐
│   Coupon        │ (MongoDB)
│  - code         │
│  - discount     │
│  - expires_at   │
└────────┬────────┘
         │
         │ 1:many
         ↓
┌─────────────────┐
│ Coupon Usage    │ (MongoDB)
│  - user_id      │
│  - code         │
│  - applied_at   │
└─────────────────┘
```

## Subscription Plan Matrix

```
┌──────────────┬──────────┬──────────┬──────────────┐
│   Feature    │   Free   │   Pro    │  Enterprise  │
├──────────────┼──────────┼──────────┼──────────────┤
│ QR Codes     │    3     │    50    │  Unlimited   │
│ Storage      │  100 MB  │   1 GB   │  Unlimited   │
│ API Calls    │   100    │  10,000  │  Unlimited   │
│ Support      │    ❌     │    ✅     │      ✅       │
│ Branding     │    ❌     │    ✅     │      ✅       │
│ Analytics    │    ❌     │    ❌     │      ✅       │
│ Price/Month  │   $0     │  $9.99   │   $49.99     │
│ Price/Year   │   $0     │ $99.99   │  $499.99     │
└──────────────┴──────────┴──────────┴──────────────┘
```

## Security Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   INPUT VALIDATION                      │
│  • Form Validation  • CSRF Tokens  • XSS Protection    │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│                   AUTHENTICATION                        │
│  • Django Auth  • OAuth2  • Session Management         │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│                   AUTHORIZATION                         │
│  • Login Required  • Admin Check  • Owner Verification │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│                   ENCRYPTION                            │
│  • AES-256-GCM  • Unique Nonces  • Secure Storage      │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│                   AUDIT LOGGING                         │
│  • All Actions Logged  • Immutable  • Timestamp        │
└─────────────────────────────────────────────────────────┘
```

## Technology Stack

```
Frontend:
  ├── Bootstrap 5.3 (UI Framework)
  ├── Bootstrap Icons (Iconography)
  ├── Animate.css (Animations)
  └── Custom CSS (Styling)

Backend:
  ├── Django 5.2.9 (Web Framework)
  ├── Python 3.10+ (Language)
  └── Social Auth (OAuth)

Databases:
  ├── SQLite (Django Auth)
  └── MongoDB (Business Data)

Security:
  ├── Cryptography (AES-256-GCM)
  ├── Argon2 (Password Hashing)
  └── CSRF Protection (Django)

Libraries:
  ├── qrcode (QR Generation)
  ├── PyMongo (MongoDB Driver)
  └── python-social-auth (OAuth)
```

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Load Balancer                        │
│                  (Nginx / Apache)                       │
└──────────────────────┬──────────────────────────────────┘
                       │
         ┌─────────────┴─────────────┐
         ↓                           ↓
┌─────────────────┐         ┌─────────────────┐
│  Django App 1   │         │  Django App 2   │
│   (Gunicorn)    │         │   (Gunicorn)    │
└────────┬────────┘         └────────┬────────┘
         │                           │
         └─────────────┬─────────────┘
                       ↓
         ┌─────────────────────────┐
         │   MongoDB Cluster       │
         │   (Replica Set)         │
         └─────────────────────────┘
```

## File Organization

```
ADVANCEQRCODEGERNATOR/
│
├── core/                        # Main Application
│   ├── templates/              # HTML Templates
│   ├── subscription.py         # Subscription Logic
│   ├── views.py                # View Controllers
│   ├── urls.py                 # URL Routing
│   ├── totp.py                 # TOTP Management
│   ├── crypto.py               # Encryption
│   └── mongo.py                # Database Connection
│
├── ktvs/                        # Project Settings
│   ├── settings.py             # Configuration
│   ├── urls.py                 # Main URLs
│   └── wsgi.py                 # WSGI Config
│
├── Output/                      # Generated Files
│   ├── .gitkeep
│   └── README.md
│
├── Documentation/
│   ├── README.md               # Overview
│   ├── SETUP_GUIDE.md          # Setup Instructions
│   ├── PROJECT_SUMMARY.md      # Implementation Details
│   ├── QUICK_REFERENCE.md      # Quick Commands
│   └── ARCHITECTURE.md         # This File
│
└── Configuration/
    ├── .env                     # Environment Variables
    ├── .gitignore              # Git Exclusions
    ├── pyproject.toml          # Dependencies
    └── manage.py               # Django CLI
```

---

**KTVS Enterprise v2.0.0**  
System Architecture Documentation
