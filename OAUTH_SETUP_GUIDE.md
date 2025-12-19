# OAuth Setup Guide - Google & GitHub

This guide will help you configure OAuth authentication for your KTVS application.

## 🔐 OAuth Providers Supported

- **Google OAuth 2.0** - Sign in with Google
- **GitHub OAuth** - Sign in with GitHub

---

## 📋 Prerequisites

1. A Google Cloud Platform account (for Google OAuth)
2. A GitHub account (for GitHub OAuth)
3. Your application running locally or on a server
4. Access to the `.env` file in your project root

---

## 🌐 Callback URLs

Your OAuth redirect URIs (callback URLs) must be registered with each provider:

### Development (Local):
- Google: `http://127.0.0.1:8000/oauth/complete/google-oauth2/`
- GitHub: `http://127.0.0.1:8000/oauth/complete/github/`

### Production:
- Google: `https://yourdomain.com/oauth/complete/google-oauth2/`
- GitHub: `https://yourdomain.com/oauth/complete/github/`

---

## 🔵 Google OAuth Setup

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Select a project"** → **"New Project"**
3. Name your project (e.g., "KTVS Auth")
4. Click **"Create"**

### Step 2: Enable Google+ API

1. In your project, go to **"APIs & Services"** → **"Library"**
2. Search for **"Google+ API"**
3. Click **"Enable"**

### Step 3: Configure OAuth Consent Screen

1. Go to **"APIs & Services"** → **"OAuth consent screen"**
2. Select **"External"** (for testing) or **"Internal"** (for organization use)
3. Fill in the required information:
   - **App name**: KTVS Authentication
   - **User support email**: Your email
   - **Developer contact email**: Your email
4. Click **"Save and Continue"**
5. Skip "Scopes" → Click **"Save and Continue"**
6. Add test users (your email) if using External
7. Click **"Save and Continue"**

### Step 4: Create OAuth 2.0 Credentials

1. Go to **"APIs & Services"** → **"Credentials"**
2. Click **"Create Credentials"** → **"OAuth 2.0 Client ID"**
3. Select **"Web application"**
4. Name: "KTVS Web Client"
5. **Authorized JavaScript origins**:
   - `http://127.0.0.1:8000`
   - `http://localhost:8000`
6. **Authorized redirect URIs**:
   - `http://127.0.0.1:8000/oauth/complete/google-oauth2/`
   - `http://localhost:8000/oauth/complete/google-oauth2/`
7. Click **"Create"**
8. **Copy the Client ID and Client Secret** - you'll need these!

### Step 5: Update .env File

```env
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=your-client-id-here.apps.googleusercontent.com
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=your-client-secret-here
```

---

## 🐙 GitHub OAuth Setup

### Step 1: Register a New OAuth App

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click **"OAuth Apps"** → **"New OAuth App"**
3. Fill in the application details:
   - **Application name**: KTVS Authentication
   - **Homepage URL**: `http://127.0.0.1:8000` (for local development)
   - **Application description**: KTVS Token Validation System
   - **Authorization callback URL**: `http://127.0.0.1:8000/oauth/complete/github/`
4. Click **"Register application"**

### Step 2: Get Client Credentials

1. After registration, you'll see your **Client ID**
2. Click **"Generate a new client secret"**
3. **Copy both the Client ID and Client Secret** - you'll need these!

### Step 3: Update .env File

```env
SOCIAL_AUTH_GITHUB_KEY=your-github-client-id
SOCIAL_AUTH_GITHUB_SECRET=your-github-client-secret
```

---

## 🔧 Configuration Checklist

### Your `.env` file should contain:

```env
# ============ OAUTH2 - GOOGLE ============
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=725051651042-xxxxxxxxxxxxx.apps.googleusercontent.com
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=GOCSPX-xxxxxxxxxxxxx

# ============ OAUTH2 - GITHUB ============
SOCIAL_AUTH_GITHUB_KEY=Ov23lixxxxxxxxxxxx
SOCIAL_AUTH_GITHUB_SECRET=d5a29c9d0e8ae6215xxxxxxxxxxxxxxxxx

# Enable OAuth
ENABLE_OAUTH=True
```

---

## ✅ Testing OAuth

### 1. Restart your Django server
```bash
python manage.py runserver
```

### 2. Navigate to Login Page
```
http://127.0.0.1:8000/login/
```

### 3. Test OAuth Buttons
- Click **"Continue with Google"** - should redirect to Google login
- Click **"Continue with GitHub"** - should redirect to GitHub login

### 4. Verify Successful Login
After authentication, you should be redirected to `/dashboard/`

---

## 🚨 Common Issues & Solutions

### Issue: "redirect_uri_mismatch" error (Google)

**Solution**: 
- Make sure your redirect URI in Google Console exactly matches: `http://127.0.0.1:8000/oauth/complete/google-oauth2/`
- Check for trailing slashes - they matter!
- Use `127.0.0.1` not `localhost` (or add both)

### Issue: GitHub OAuth returns "Bad verification code"

**Solution**:
- Regenerate your client secret in GitHub
- Update `.env` with the new secret
- Restart Django server

### Issue: OAuth buttons don't work

**Solution**:
1. Check that `.env` file is loaded:
   ```python
   python manage.py shell
   >>> from django.conf import settings
   >>> print(settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY)
   ```
2. Verify `ENABLE_OAUTH=True` in `.env`
3. Check Django logs for error messages

### Issue: User created but no TOTP profile

**Solution**:
- Check `core/pipeline.py` - the `create_totp_profile` function should execute
- Check MongoDB connection
- Verify user exists in Django admin

---

## 🔒 Production Configuration

For production deployment:

1. **Update redirect URIs** in Google Cloud Console and GitHub:
   - Replace `http://127.0.0.1:8000` with `https://yourdomain.com`
   
2. **Update `.env` production settings**:
   ```env
   DEBUG=False
   SOCIAL_AUTH_REDIRECT_IS_HTTPS=True
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
   ```

3. **Enable HTTPS** on your server

4. **Update OAuth consent screen** (Google) to verified status

---

## 📞 Support

If you encounter issues:

1. Check Django logs: `python manage.py runserver` output
2. Check browser console for JavaScript errors
3. Verify MongoDB is running: `mongosh` or check Docker container
4. Review `OAUTH_IMPLEMENTATION.md` for architecture details

---

## 📚 Additional Resources

- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [GitHub OAuth Apps Documentation](https://docs.github.com/en/developers/apps/building-oauth-apps)
- [Django Social Auth Documentation](https://python-social-auth.readthedocs.io/)

---

**Last Updated**: December 2025
**Version**: 1.0
