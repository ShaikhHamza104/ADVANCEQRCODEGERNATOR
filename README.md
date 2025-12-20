# Advanced QR Code Generator

A Django web application for creating, customizing, and managing QR codes with user authentication and subscription tiers.

## Features

- **QR Code Generation** - Create customizable QR codes with colors, logos, and size presets
- **User Authentication** - Login via username/password or OAuth (Google, GitHub)
- **Two-Factor Authentication (2FA)** - TOTP-based security for accounts
- **QR History** - Save, favorite, and manage generated QR codes
- **Subscription Tiers** - Free, Pro, and Enterprise plans with usage quotas
- **Admin Dashboard** - User management and audit logs

## Tech Stack

- **Backend:** Django 5.2
- **Database:** SQLite (dev) / MongoDB (prod)
- **Security:** AES-256-GCM encryption, Argon2 password hashing
- **UI:** Bootstrap 5

## Quick Start

```bash
# Install dependencies
uv sync

# Run migrations
uv run python manage.py migrate

# Create admin user
uv run python manage.py createsuperuser

# Start server
uv run python manage.py runserver
```

Visit: **http://127.0.0.1:8000**

## Environment Variables

Create a `.env` file:

```env
SECRET_KEY=your-secret-key
DEBUG=True
MONGO_URI=mongodb://localhost:27017/qrcode_db
```

## License

MIT License. See `LICENSE` file for details.

## Contributing
Contributions welcome! Please open issues and pull requests on GitHub.

## Contact
For questions or support, contact **kmohdhamza10@gmail.com**.
---