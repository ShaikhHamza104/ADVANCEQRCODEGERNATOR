# 🚀 How to Run KTVS Application

## Quick Start (Easiest Method)

### Windows Users

1. **Open Command Prompt or PowerShell** in the project folder
2. **Run the start script:**
   ```bash
   start.bat
   ```
3. **Wait for the server to start** (you'll see "Starting development server...")
4. **Open your browser** and go to: **http://localhost:8000**

That's it! The script automatically:
- Activates the virtual environment
- Installs dependencies
- Runs database migrations
- Starts the development server

### Linux/Mac Users

1. **Open Terminal** in the project folder
2. **Make the script executable (first time only):**
   ```bash
   chmod +x start.sh
   ```
3. **Run the start script:**
   ```bash
   ./start.sh
   ```
4. **Open your browser** and go to: **http://localhost:8000**

---

## Step-by-Step Manual Method

If the automatic script doesn't work, follow these steps:

### Step 1: Activate Virtual Environment

**Windows:**
```bash
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

You should see `(.venv)` appear in your command prompt.

### Step 2: Install Dependencies (First Time Only)

```bash
pip install -r requirements.txt
```

Or if you have `uv` installed:
```bash
uv sync
```

### Step 3: Run Database Migrations (First Time Only)

```bash
python manage.py migrate
```

### Step 4: Create Admin User (First Time Only)

```bash
python manage.py createsuperuser
```

Or use the default admin account:
- Username: `admin`
- Password: `admin123`
- Email: `admin@ktvs.com`

### Step 5: Start the Server

```bash
python manage.py runserver
```

### Step 6: Open Your Browser

Navigate to: **http://localhost:8000**

---

## Optional: Create Sample Coupons

After the server is running, open a **new terminal/command prompt** and run:

**Windows:**
```bash
.venv\Scripts\python.exe create_coupons.py
```

**Linux/Mac:**
```bash
.venv/bin/python create_coupons.py
```

This creates 5 sample coupon codes you can test with.

---

## Accessing the Application

### Main Pages

1. **Homepage**: http://localhost:8000
2. **Login**: http://localhost:8000/login
3. **Register**: http://localhost:8000/register
4. **Pricing**: http://localhost:8000/pricing
5. **Admin Dashboard**: http://localhost:8000/admin-dashboard (admin only)
6. **Django Admin**: http://localhost:8000/admin (admin only)

### Default Login Credentials

```
Username: admin
Password: admin123
Email: admin@ktvs.com
```

⚠️ **Change this password after first login!**

---

## Testing Features

### 1. Register a New User
1. Go to http://localhost:8000/register
2. Fill in username, email, password
3. Click "Register"
4. You'll get a Free subscription automatically

### 2. View Pricing Plans
1. Login to your account
2. Click "Pricing" in the navbar
3. See all 3 plans (Free, Pro, Enterprise)

### 3. Apply a Coupon Code
1. Go to Pricing page
2. Enter coupon code: `WELCOME50`
3. Select billing cycle
4. Click "Apply"
5. Your subscription will upgrade with 50% discount!

### 4. Change Password
1. Click on your username in navbar
2. Select "Change Password"
3. Enter current and new password
4. Submit

### 5. View Subscription
1. Click username dropdown
2. Select "My Subscription"
3. See your plan details and usage

### 6. Logout
1. Click username dropdown
2. Click "Logout" button
3. Or press **Ctrl+L**

---

## Troubleshooting

### Issue: "Module not found" error

**Solution:** Activate virtual environment and install dependencies
```bash
# Windows
.venv\Scripts\activate
pip install -r requirements.txt

# Linux/Mac
source .venv/bin/activate
pip install -r requirements.txt
```

### Issue: "Port 8000 already in use"

**Solution 1:** Use a different port
```bash
python manage.py runserver 8080
```
Then access: http://localhost:8080

**Solution 2:** Stop the other process
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### Issue: "MongoDB connection failed"

**Solution:** The app works without MongoDB (uses in-memory storage)

For production, install MongoDB:
- Windows: https://www.mongodb.com/try/download/community
- Linux: `sudo apt-get install mongodb`
- Mac: `brew install mongodb-community`

Then update `.env`:
```env
MONGO_URI=mongodb://localhost:27017/ktvs
```

### Issue: Virtual environment not found

**Solution:** Create virtual environment
```bash
python -m venv .venv
```
Then activate it and install dependencies.

### Issue: Django not found

**Solution:** Install Django
```bash
pip install django
```

---

## Stopping the Server

Press **Ctrl+C** in the terminal where the server is running.

---

## Complete Workflow Example

Here's a complete example of running the application:

```bash
# 1. Navigate to project folder
cd D:\ADVANCEQRCODEGERNATOR

# 2. Run the start script (EASIEST)
start.bat

# OR do it manually:

# 3. Activate virtual environment
.venv\Scripts\activate

# 4. Run server
python manage.py runserver

# 5. Open browser to http://localhost:8000

# 6. Login with admin/admin123

# 7. Test features!
```

---

## First-Time Setup Checklist

- [ ] Navigate to project folder
- [ ] Activate virtual environment
- [ ] Install dependencies (`pip install -r requirements.txt`)
- [ ] Run migrations (`python manage.py migrate`)
- [ ] Create admin user or use default (admin/admin123)
- [ ] Start server (`python manage.py runserver`)
- [ ] Open browser to http://localhost:8000
- [ ] Login and test!
- [ ] (Optional) Create sample coupons (`python create_coupons.py`)

---

## Development Mode vs Production

### Development (Current Setup)
- DEBUG=True
- Uses SQLite + in-memory MongoDB
- HTTP (no SSL)
- Default secret keys
- Runs on localhost:8000

### Production (When Ready)
- Set DEBUG=False in `.env`
- Configure real MongoDB
- Enable HTTPS
- Change all secret keys
- Use Gunicorn/uWSGI
- Set up Nginx/Apache

See **SETUP_GUIDE.md** for production deployment.

---

## Need Help?

1. **Installation issues?** Check [README.md](README.md)
2. **Setup questions?** See [SETUP_GUIDE.md](SETUP_GUIDE.md)
3. **Quick commands?** Use [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
4. **Errors?** Check [SETUP_GUIDE.md - Troubleshooting](SETUP_GUIDE.md#troubleshooting)

---

## Summary - TL;DR

**Windows:**
```bash
start.bat
# Then open: http://localhost:8000
# Login: admin / admin123
```

**Linux/Mac:**
```bash
./start.sh
# Then open: http://localhost:8000
# Login: admin / admin123
```

**That's it!** 🎉

---

**KTVS Enterprise v2.0.0**  
Application Startup Guide
