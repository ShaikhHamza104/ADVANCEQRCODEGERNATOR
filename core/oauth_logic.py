"""
OAuth Login Logic - Google & GitHub Authentication
Uses credentials from .env file
"""
import os
from django.shortcuts import redirect
from django.contrib.auth import login as auth_login
from django.contrib import messages
from django.conf import settings
from social_django.utils import psa

def oauth_login_handler(request, backend):
    """
    Custom OAuth login handler
    Supports: google-oauth2, github
    
    Credentials from .env:
    - SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
    - SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET
    - SOCIAL_AUTH_GITHUB_KEY
    - SOCIAL_AUTH_GITHUB_SECRET
    """
    
    # Validate backend
    supported_backends = ['google-oauth2', 'github']
    if backend not in supported_backends:
        messages.error(request, f'Unsupported OAuth provider: {backend}')
        return redirect('login')
    
    # Check if OAuth is enabled
    if not settings.ENABLE_OAUTH:
        messages.error(request, 'OAuth authentication is currently disabled.')
        return redirect('login')
    
    # Validate credentials are configured
    if backend == 'google-oauth2':
        if not settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY or not settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET:
            messages.error(request, 'Google OAuth is not configured. Please contact administrator.')
            return redirect('login')
    
    elif backend == 'github':
        if not settings.SOCIAL_AUTH_GITHUB_KEY or not settings.SOCIAL_AUTH_GITHUB_SECRET:
            messages.error(request, 'GitHub OAuth is not configured. Please contact administrator.')
            return redirect('login')
    
    # OAuth flow continues via social_django
    return None


@psa('social:complete')
def oauth_complete(request, backend):
    """
    OAuth completion handler
    Called after successful authentication with provider
    """
    
    # Get user from OAuth response
    user = request.user
    
    if user and user.is_authenticated:
        # Successful OAuth login
        messages.success(
            request,
            f'Successfully logged in with {backend.title()}! Welcome {user.get_full_name() or user.username}!'
        )
        
        # Log the OAuth login
        from core.models import AuditLog
        AuditLog.log_event(
            user=user,
            action=f'oauth_login_{backend}',
            details=f'User logged in via {backend}',
            ip_address=get_client_ip(request)
        )
        
        # Redirect to dashboard
        return redirect('dashboard')
    
    else:
        # OAuth failed
        messages.error(request, f'Failed to authenticate with {backend}. Please try again.')
        return redirect('login')


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def validate_oauth_config():
    """
    Validate OAuth configuration from .env
    Returns dict with status for each provider
    """
    config_status = {
        'google': {
            'enabled': False,
            'configured': False,
            'key_present': False,
            'secret_present': False,
            'error': None
        }
    }
    
    # Check Google OAuth
    google_key = getattr(settings, 'SOCIAL_AUTH_GOOGLE_OAUTH2_KEY', None)
    google_secret = getattr(settings, 'SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET', None)
    
    config_status['google']['key_present'] = bool(google_key)
    config_status['google']['secret_present'] = bool(google_secret)
    config_status['google']['configured'] = bool(google_key and google_secret)
    # Enabled only if configured and global OAuth feature flag is on
    config_status['google']['enabled'] = bool(
        config_status['google']['configured'] and getattr(settings, 'ENABLE_OAUTH', True)
    )
    
    if not google_key:
        config_status['google']['error'] = 'SOCIAL_AUTH_GOOGLE_OAUTH2_KEY not set in .env'
    elif not google_secret:
        config_status['google']['error'] = 'SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET not set in .env'
    
    return config_status


# OAuth URL generators
def get_google_login_url():
    """Generate Google OAuth login URL"""
    from django.urls import reverse
    return reverse('social:begin', kwargs={'backend': 'google-oauth2'})


def get_oauth_redirect_uris():
    """
    Get OAuth redirect URIs for configuration
    These must be registered in Google Cloud Console
    """
    base_url = 'http://127.0.0.1:8000'  # Development
    
    return {
        'google': [
            f'{base_url}/oauth/complete/google-oauth2/',
            'http://localhost:8000/oauth/complete/google-oauth2/',
        ]
    }


# Context processor for templates
def oauth_context(request):
    """
    Add OAuth configuration to template context
    Usage in templates: {{ oauth.google.enabled }}
    """
    config = validate_oauth_config()
    
    return {
        'oauth': {
            'google': {
                'enabled': config['google']['enabled'],
                'configured': config['google']['configured'],
                'login_url': get_google_login_url() if config['google']['enabled'] else None,
                'name': 'Google',
                'icon': 'bi-google',
                'button_class': 'btn-danger'
            }
        }
    }
