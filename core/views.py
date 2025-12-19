from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout, update_session_auth_hash, authenticate
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden, JsonResponse
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, PasswordResetForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.middleware.csrf import get_token
from typing import Optional, Dict, Any
from .totp import TOTPProfile, AuditLog
from .mongo import db
from .coupon import CouponManager
from .subscription import SubscriptionManager, CouponSystem, PLANS
from .qr_history import QRHistory
from bson import ObjectId
from datetime import datetime, timedelta
import qrcode
import io
import secrets
import string
import os

def _get_actor(request: HttpRequest) -> Dict[str, Any]:
    """Creates an actor dictionary from the request."""
    return {
        "user_id": str(request.user.id),
        "ip_address": request.META.get('REMOTE_ADDR'),
        "user_agent": request.META.get('HTTP_USER_AGENT')
    }

def _get_profile_and_check_permission(request: HttpRequest, profile_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Fetches a profile and checks for user permission."""
    if profile_id:
        try:
            oid = ObjectId(profile_id)
        except Exception:
            return None
        profile = db.totp_profiles.find_one({"_id": oid})
    else:
        profile = db.totp_profiles.find_one({"user_id": str(request.user.id)})

    if not profile:
        return None
        
    # Check permissions
    if profile['user_id'] != str(request.user.id) and not request.user.is_superuser:
        return None
        
    return profile

def _paginate(request: HttpRequest, collection, per_page: int = 20) -> Dict[str, Any]:
    """Paginates a MongoDB collection."""
    try:
        page = int(request.GET.get('page', 1))
        if page < 1:
            page = 1
    except ValueError:
        page = 1

    skip = (page - 1) * per_page
    total_documents = collection.count_documents({})
    documents = list(collection.find().skip(skip).limit(per_page))

    for doc in documents:
        doc['id'] = str(doc['_id'])  # Rename _id to id for template compatibility

    total_pages = (total_documents + per_page - 1) // per_page
    has_next = page < total_pages
    has_previous = page > 1

    return {
        'documents': documents,
        'page': page,
        'total_pages': total_pages,
        'has_next': has_next,
        'has_previous': has_previous,
    }

def home(request: HttpRequest) -> HttpResponse:
    return render(request, 'home.html')


def custom_login(request: HttpRequest) -> HttpResponse:
    """Custom login view with 2FA redirect"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Check if user has 2FA enabled
            profile = TOTPProfile.get_by_user_id(str(user.id))
            
            if profile:
                # Check is_2fa_enabled - default to True for legacy profiles without this field
                is_2fa_enabled = getattr(profile, 'is_2fa_enabled', True)
                
                if is_2fa_enabled:
                    # Redirect to 2FA verification
                    from datetime import datetime
                    request.session['pending_2fa_user_id'] = str(user.id)
                    request.session['pending_2fa_timestamp'] = datetime.utcnow().isoformat()
                    request.session['failed_2fa_attempts'] = 0  # Reset failed attempts
                    return redirect('verify_2fa')
            
            # No 2FA profile or 2FA disabled - direct login
            from django.contrib.auth import login
            login(request, user)
            messages.success(request, f'✓ Welcome back, {user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, '❌ Invalid username or password')
    
    return render(request, 'registration/login.html')


def register(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        
        # Check if terms and privacy policy are accepted
        agree_terms = request.POST.get('agree_terms')
        agree_privacy = request.POST.get('agree_privacy')
        
        if not agree_terms or not agree_privacy:
            messages.error(request, '⚠️ You must accept both the Terms of Service and Privacy Policy to register.')
            return render(request, 'registration/register.html', {'form': form})
        
        if form.is_valid():
            user = form.save(commit=False)
            # Get email from form data
            email = request.POST.get('email', '').strip()
            full_name = request.POST.get('full_name', '').strip()
            
            if email:
                user.email = email
            if full_name:
                # Split full name into first and last name
                name_parts = full_name.split(' ', 1)
                user.first_name = name_parts[0]
                if len(name_parts) > 1:
                    user.last_name = name_parts[1]
            
            user.save()
            
            # Automatically create a TOTP profile for new users
            user_id = str(user.id)
            actor = {
                "user_id": "system_registration",
                "ip_address": request.META.get('REMOTE_ADDR'),
                "user_agent": request.META.get('HTTP_USER_AGENT')
            }
            
            # Generate random seed
            alphabet = string.ascii_uppercase + '234567'
            seed = ''.join(secrets.choice(alphabet) for _ in range(32))
            
            TOTPProfile.create(
                user_id=user_id,
                seed=seed,
                metadata={
                    "label": user.username,
                    "issuer": settings.KTVS_SETTINGS['ISSUER'],
                    "digits": settings.KTVS_SETTINGS['TOTP_DIGITS'],
                    "period": settings.KTVS_SETTINGS['TOTP_PERIOD'],
                    "algorithm": settings.KTVS_SETTINGS['TOTP_ALGORITHM']
                },
                kelley_attributes={
                    "role": settings.KTVS_SETTINGS['DEFAULT_KELLEY_ROLE'],
                    "function": settings.KTVS_SETTINGS['DEFAULT_KELLEY_FUNCTION']
                },
                security_flags={
                    "is_high_privilege": False,
                    "is_private": False,
                    "revocation_state": "Active"
                },
                actor=actor
            )
            
            # Create Free subscription
            SubscriptionManager.create_subscription(user_id, 'FREE')
            
            # Send welcome email
            from .emails import EmailService
            EmailService.send_welcome_email(user.email, user.username)
            
            # Send email verification
            from .email_verification import EmailVerification
            EmailVerification.send_verification_email(
                user_id, 
                user.email, 
                user.username, 
                request
            )
            
            messages.success(request, '✅ Account created successfully! Please check your email to verify your account before logging in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    user_id = str(request.user.id)
    profile = _get_profile_and_check_permission(request)
    
    # Add id key for template compatibility
    if profile:
        profile['id'] = str(profile['_id'])
    
    # Get 2FA status
    totp_profile = TOTPProfile.get_by_user_id(user_id)
    is_2fa_enabled = totp_profile.is_2fa_enabled if totp_profile else False
    
    # Get subscription info
    subscription = SubscriptionManager.get_user_subscription(user_id)
    
    # Check plan expiration for non-admin users
    if not request.user.is_superuser and subscription.get('plan_type') != 'FREE':
        current_period_end = subscription.get('current_period_end')
        if current_period_end and current_period_end < datetime.utcnow():
            # Plan expired, downgrade to FREE
            SubscriptionManager.upgrade_subscription(user_id, 'FREE')
            subscription = SubscriptionManager.get_user_subscription(user_id)
            messages.warning(request, '⚠️ Your subscription has expired and has been automatically downgraded to the Free plan.')
    
    # Admin users always have ENTERPRISE plan (unlimited, no expiration)
    if request.user.is_superuser and subscription.get('plan_type') != 'ENTERPRISE':
        SubscriptionManager.upgrade_subscription(user_id, 'ENTERPRISE')
        subscription = SubscriptionManager.get_user_subscription(user_id)
        # Make admin plan never expire
        db.subscriptions.update_one(
            {'user_id': user_id},
            {'$set': {'current_period_end': datetime.utcnow() + timedelta(days=36500)}}  # 100 years
        )
        subscription = SubscriptionManager.get_user_subscription(user_id)
    
    # Initialize QR count on first dashboard load if not set
    # This combines TOTP profiles + custom URL QR codes
    if subscription.get('usage', {}).get('qr_count') is None:
        actual_qr_count = db.totp_profiles.count_documents({'user_id': user_id})
        db.subscriptions.update_one(
            {'user_id': user_id},
            {'$set': {'usage.qr_count': actual_qr_count}}
        )
        # Re-fetch subscription to get updated count
        subscription = SubscriptionManager.get_user_subscription(user_id)
    
    can_create, quota_info = SubscriptionManager.check_qr_quota(user_id)
    
    # Get recent audit logs for this user
    audit_logs = []
    if profile:
        logs = db.audit_logs.find({"target_profile_id": ObjectId(profile['_id'])}).sort("timestamp", -1).limit(10)
        audit_logs = list(logs)
    
    context = {
        'profile': profile,
        'audit_logs': audit_logs,
        'user': request.user,
        'subscription': subscription,
        'quota_info': quota_info,
        'can_create_more': can_create,
        'is_2fa_enabled': is_2fa_enabled
    }
    return render(request, 'dashboard.html', context)

@login_required
def qr_code_view(request: HttpRequest, profile_id: str) -> HttpResponse:
    profile = _get_profile_and_check_permission(request, profile_id)
    if not profile:
        return HttpResponseForbidden("Access Denied")

    actor = _get_actor(request)
    
    profile_obj = TOTPProfile(**profile)
    seed = profile_obj.get_decrypted_seed(actor)
    
    # Get customization parameters
    bg_color = request.GET.get('bg', 'white')
    fg_color = request.GET.get('fg', 'black')
    box_size = int(request.GET.get('box_size', '10'))
    border = int(request.GET.get('border', '4'))
    
    # Generate OTP Auth URL
    otp_uri = f"otpauth://totp/{profile['metadata']['issuer']}:{profile['metadata']['label']}?secret={seed}&issuer={profile['metadata']['issuer']}&algorithm={profile['metadata']['algorithm']}&digits={profile['metadata']['digits']}&period={profile['metadata']['period']}"
    
    # Create QR code with customization
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=box_size,
        border=border,
    )
    qr.add_data(otp_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color=fg_color, back_color=bg_color)
    buf = io.BytesIO()
    img.save(buf)
    buf.seek(0)
    
    return HttpResponse(buf, content_type="image/png")

@login_required
def admin_dashboard(request: HttpRequest) -> HttpResponse:
    if not request.user.is_superuser:
        return HttpResponseForbidden("Admins Only")
    
    pagination_data = _paginate(request, db.totp_profiles)
    
    # Ensure all profiles have 'id' field
    for profile in pagination_data['documents']:
        if 'id' not in profile and '_id' in profile:
            profile['id'] = str(profile['_id'])
    
    # Get total audit logs count
    total_logs = db.audit_logs.count_documents({})
    total_users = User.objects.count()
    
    # Get all users for admin management
    all_users = User.objects.all()
    
    context = {
        'profiles': pagination_data['documents'],
        'total_logs': total_logs,
        'total_users': total_users,
        'all_users': all_users,
        'page': pagination_data['page'],
        'total_pages': pagination_data['total_pages'],
        'has_next': pagination_data['has_next'],
        'has_previous': pagination_data['has_previous'],
    }
    return render(request, 'admin_dashboard.html', context)

@login_required
def profile_detail(request: HttpRequest, profile_id: str) -> HttpResponse:
    profile_data = _get_profile_and_check_permission(request, profile_id)
    if not profile_data:
        messages.error(request, "Profile not found or access denied.")
        return redirect('admin_dashboard')
    
    # Convert _id to string and add id key for template compatibility
    profile_data['id'] = str(profile_data['_id'])
    
    # Get audit logs for this profile
    logs = db.audit_logs.find({"target_profile_id": ObjectId(profile_id)}).sort("timestamp", -1).limit(20)
    audit_logs = list(logs)
    
    context = {
        'profile': profile_data,
        'audit_logs': audit_logs
    }
    return render(request, 'profile_detail.html', context)

@login_required
def create_profile(request: HttpRequest) -> HttpResponse:
    if not request.user.is_superuser:
        return HttpResponseForbidden("Admins Only")
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        label = request.POST.get('label')
        issuer = request.POST.get('issuer', 'KTVS')
        
        actor = _get_actor(request)
        
        # Generate random seed
        alphabet = string.ascii_uppercase + '234567'
        seed = ''.join(secrets.choice(alphabet) for _ in range(32))
        
        profile = TOTPProfile.create(
            user_id=user_id,
            seed=seed,
            metadata={
                "label": label,
                "issuer": issuer,
                "digits": settings.KTVS_SETTINGS['TOTP_DIGITS'],
                "period": settings.KTVS_SETTINGS['TOTP_PERIOD'],
                "algorithm": settings.KTVS_SETTINGS['TOTP_ALGORITHM']
            },
            kelley_attributes={
                "role": request.POST.get('role', settings.KTVS_SETTINGS['DEFAULT_KELLEY_ROLE']),
                "function": request.POST.get('function', settings.KTVS_SETTINGS['DEFAULT_KELLEY_FUNCTION'])
            },
            security_flags={
                "is_high_privilege": request.POST.get('is_high_privilege') == 'on',
                "is_private": request.POST.get('is_private') == 'on',
                "revocation_state": "Active"
            },
            actor=actor
        )
        
        messages.success(request, f'Profile created for {user_id}')
        return redirect('admin_dashboard')
    
    return render(request, 'create_profile.html')

@login_required
def download_qr(request: HttpRequest, profile_id: str) -> HttpResponse:
    """Download QR code as PNG file with customization options"""
    profile = _get_profile_and_check_permission(request, profile_id)
    if not profile:
        return HttpResponseForbidden("Access Denied")

    actor = _get_actor(request)
    
    profile_obj = TOTPProfile(**profile)
    seed = profile_obj.get_decrypted_seed(actor)
    
    # Get customization parameters
    bg_color = request.GET.get('bg', 'white')
    fg_color = request.GET.get('fg', 'black')
    size_preset = request.GET.get('size', 'medium')
    
    # Size presets (box_size, border, pixel dimensions)
    size_presets = {
        'small': (8, 3, 256),      # Small 256x256
        'medium': (10, 4, 512),     # Medium 512x512
        'large': (12, 5, 1024),     # Large 1024x1024
        '16:9': (10, 4, 1920),      # 16:9 HD
        '4:3': (10, 4, 1024),       # 4:3 Standard
        '1:1': (10, 4, 800),        # Square 1:1
    }
    
    box_size, border, _ = size_presets.get(size_preset, size_presets['medium'])
    
    # Allow custom override
    if request.GET.get('box_size'):
        box_size = int(request.GET.get('box_size'))
    if request.GET.get('border'):
        border = int(request.GET.get('border'))
    
    otp_uri = f"otpauth://totp/{profile['metadata']['issuer']}:{profile['metadata']['label']}?secret={seed}&issuer={profile['metadata']['issuer']}&algorithm={profile['metadata']['algorithm']}&digits={profile['metadata']['digits']}&period={profile['metadata']['period']}"
    
    # Create QR code with customization
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=box_size,
        border=border,
    )
    qr.add_data(otp_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color=fg_color, back_color=bg_color)
    buf = io.BytesIO()
    img.save(buf)
    buf.seek(0)
    
    response = HttpResponse(buf, content_type="image/png")
    response['Content-Disposition'] = f'attachment; filename="{profile["metadata"]["label"]}_qr.png"'
    return response

@login_required
def export_seed(request: HttpRequest, profile_id: str) -> JsonResponse:
    """Export TOTP seed (admin only or profile owner)"""
    profile_data = _get_profile_and_check_permission(request, profile_id)
    if not profile_data:
        return JsonResponse({"error": "Profile not found or access denied"}, status=403)
    
    profile_data['_id'] = str(profile_data['_id'])
    profile = TOTPProfile(**profile_data)
    
    actor = _get_actor(request)
    
    seed = profile.get_decrypted_seed(actor)
    
    return JsonResponse({
        "seed": seed,
        "label": profile.metadata['label'],
        "issuer": profile.metadata['issuer'],
        "otp_uri": f"otpauth://totp/{profile.metadata['issuer']}:{profile.metadata['label']}?secret={seed}&issuer={profile.metadata['issuer']}&algorithm={profile.metadata['algorithm']}&digits={profile.metadata['digits']}&period={profile.metadata['period']}"
    })

@login_required
@require_POST
def delete_profile(request: HttpRequest, profile_id: str) -> HttpResponse:
    """Delete a TOTP profile (admin only)"""
    profile = _get_profile_and_check_permission(request, profile_id)
    if not profile:
        messages.error(request, "Profile not found or access denied.")
        return redirect('admin_dashboard')

    result = db.totp_profiles.delete_one({"_id": ObjectId(profile_id)})
    
    if result.deleted_count > 0:
        # Log deletion
        actor = _get_actor(request)
        AuditLog(
            event_type="PROFILE_DELETED",
            actor=actor,
            target_profile_id=profile_id,
            payload={"deleted": True}
        ).save()
        
        messages.success(request, "Profile deleted successfully")
    else:
        messages.error(request, "Profile not found")
    
    return redirect('admin_dashboard')

@login_required
def update_profile(request: HttpRequest, profile_id: str) -> HttpResponse:
    """Update profile attributes (admin only)"""
    profile_data = _get_profile_and_check_permission(request, profile_id)
    if not profile_data:
        messages.error(request, "Profile not found or access denied.")
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        actor = _get_actor(request)
        
        updates = {}
        if request.POST.get('role'):
            updates['kelley_attributes.role'] = request.POST.get('role')
        if request.POST.get('function'):
            updates['kelley_attributes.function'] = request.POST.get('function')
        if 'is_high_privilege' in request.POST:
            updates['security_flags.is_high_privilege'] = request.POST.get('is_high_privilege') == 'on'
        if 'is_private' in request.POST:
            updates['security_flags.is_private'] = request.POST.get('is_private') == 'on'
        if request.POST.get('revocation_state'):
            updates['security_flags.revocation_state'] = request.POST.get('revocation_state')
        
        profile_data['_id'] = str(profile_data['_id'])
        profile = TOTPProfile(**profile_data)
        profile.update(updates, actor)
        
        messages.success(request, "Profile updated successfully")
        return redirect('profile_detail', profile_id=profile_id)
    
    # Add id key for template compatibility
    profile_data['id'] = str(profile_data['_id'])
    return render(request, 'update_profile.html', {'profile': profile_data})

@login_required
def audit_logs_view(request: HttpRequest) -> HttpResponse:
    """View all audit logs (admin only)"""
    if not request.user.is_superuser:
        return HttpResponseForbidden("Admins Only")
    
    logs = db.audit_logs.find().sort("timestamp", -1).limit(100)
    audit_logs = list(logs)
    
    return render(request, 'audit_logs.html', {'audit_logs': audit_logs})

@login_required
@require_POST
def delete_own_account(request: HttpRequest) -> HttpResponse:
    """Allow user to delete their own account"""
    user = request.user
    
    # Delete MongoDB profile
    profile = _get_profile_and_check_permission(request)
    if profile:
        db.totp_profiles.delete_one({"_id": ObjectId(profile['_id'])})
        
        # Log deletion (preserving log even if user is gone)
        actor = _get_actor(request)
        AuditLog(
            event_type="PROFILE_DELETED",
            actor=actor,
            target_profile_id=str(profile['_id']),
            payload={"deleted_by_owner": True}
        ).save()
    
    # Delete Django user
    user.delete()
    
    # Logout
    auth_logout(request)
    
    messages.success(request, "Your account has been successfully deleted.")
    return redirect('home')

def logout_view(request: HttpRequest) -> HttpResponse:
    """Custom logout view with session clearing, plan expiration check, and redirect"""
    if request.user.is_authenticated:
        user_id = str(request.user.id)
        
        # Check plan expiration before logout (unless admin)
        if not request.user.is_superuser:
            subscription = SubscriptionManager.get_user_subscription(user_id)
            
            # Check if plan has expired
            if subscription.get('plan_type') != 'FREE':
                current_period_end = subscription.get('current_period_end')
                if current_period_end and current_period_end < datetime.utcnow():
                    # Plan expired, downgrade to FREE
                    SubscriptionManager.upgrade_subscription(user_id, 'FREE')
                    messages.warning(request, '⚠️ Your subscription has expired and has been downgraded to the Free plan.')
        
        auth_logout(request)
        messages.success(request, '✅ You have been successfully logged out.')
    return redirect('home')

@require_POST
def generate_qr_from_url(request: HttpRequest) -> HttpResponse:
    """Generate customizable QR code from URL provided in POST data - Public for instant generator"""
    import json
    
    try:
        data = json.loads(request.body)
        url = data.get('url')
        
        if not url:
            return JsonResponse({'error': 'No URL provided'}, status=400)
        
        # Check quota FIRST (before generating) if not a preview
        is_preview = data.get('preview', False)
        if request.user.is_authenticated and not is_preview:
            user_id = str(request.user.id)
            can_create, quota_info = SubscriptionManager.check_qr_quota(user_id)
            if not can_create:
                return JsonResponse({
                    'error': f'QR code limit reached! You have used {quota_info["used"]}/{quota_info["limit"]} QR codes. Please upgrade your plan.'
                }, status=403)
        
        # Get customization parameters with responsive size support
        fg_color = data.get('fg', '000000').replace('#', '')
        bg_color = data.get('bg', 'ffffff').replace('#', '')
        size_preset = data.get('size', 'medium')
        
        # Size presets for different devices and aspect ratios
        size_presets = {
            'small': (8, 3),           # Small for mobile
            'medium': (10, 4),          # Medium general use
            'large': (12, 5),           # Large desktop
            'mobile': (10, 3),          # Optimized for mobile screens
            '16:9': (10, 4),            # 16:9 aspect ratio (widescreen)
            '4:3': (10, 4),             # 4:3 aspect ratio (standard)
            '1:1': (10, 4),             # 1:1 square
            'ios': (10, 4),             # iOS optimized
            'android': (10, 4),         # Android optimized
        }
        
        box_size, border = size_presets.get(size_preset, size_presets['medium'])
        
        # Allow custom override
        if data.get('box_size'):
            box_size = int(data.get('box_size'))
        if data.get('border'):
            border = int(data.get('border'))
        
        # Create QR code with customization
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=box_size,
            border=border,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        # Generate image with custom colors
        img = qr.make_image(fill_color=f'#{fg_color}', back_color=f'#{bg_color}')
        
        # Convert to bytes
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        
        # Track usage after successful generation
        if request.user.is_authenticated and not is_preview:
            user_id = str(request.user.id)
            try:
                SubscriptionManager.increment_qr_count(user_id)
                
                # Save to user history
                QRHistory.add_to_history(user_id, {
                    'qr_type': 'url',
                    'content': url,
                    'fg_color': fg_color,
                    'bg_color': bg_color,
                    'platform': size_preset if 'size' in data else 'custom',
                    'box_size': box_size,
                    'border': border
                })
            except:
                pass  # Don't fail if tracking fails
        
        return HttpResponse(buf, content_type="image/png")
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ============= COUPON SYSTEM VIEWS =============

@login_required
def coupon_entry(request: HttpRequest) -> HttpResponse:
    """Entry page for coupon code application"""
    user_id = str(request.user.id)
    
    # Initialize coupon manager
    hmac_secret = settings.KTVS_SETTINGS['COUPON_HMAC_SECRET']
    CouponManager.set_hmac_secret(hmac_secret)
    
    # Check current coupon status
    current_coupon = CouponManager.get_user_coupon(user_id)
    
    context = {
        'current_coupon': current_coupon,
        'csrf_token': get_token(request)
    }
    
    return render(request, 'coupon_entry.html', context)


@login_required
@require_POST
def apply_coupon(request: HttpRequest) -> HttpResponse:
    """Apply a coupon code to user account"""
    user_id = str(request.user.id)
    coupon_code = request.POST.get('coupon_code', '').strip()
    
    if not coupon_code:
        messages.error(request, 'Please enter a coupon code.')
        return redirect('coupon_entry')
    
    # Initialize coupon manager
    hmac_secret = settings.KTVS_SETTINGS['COUPON_HMAC_SECRET']
    CouponManager.set_hmac_secret(hmac_secret)
    
    # Validate coupon
    is_valid, coupon_data = CouponManager.validate_code(coupon_code, user_id)
    
    if not is_valid:
        messages.error(request, coupon_data.get('error', 'Invalid coupon code.'))
        return redirect('coupon_entry')
    
    # Send email for other coupon types
    from .emails import EmailService
    
    # Format benefits based on coupon type
    if coupon_data['type'] == 'QR_QUOTA_BOOST':
        benefits = f"<strong>📊 QR Code Quota Increased</strong><br>Additional QR codes: {coupon_data.get('quota_boost', 0)}<br>Your total limit has been increased!"
    elif coupon_data['type'] == 'STORAGE_BOOST':
        benefits = f"<strong>💾 Storage Increased</strong><br>Additional storage: {coupon_data.get('storage_boost', 0)} MB"
    else:
        benefits = f"<strong>🎁 Coupon Benefits Applied</strong><br>Type: {coupon_data['type']}"
    
    EmailService.send_coupon_notification(
        request.user.email, 
        request.user.username, 
        coupon_code,
        coupon_data['type'],
        benefits
    )
    
    messages.success(request, f'✅ Coupon applied: {coupon_data["type"]}')
    
    return redirect('dashboard')


@login_required
def check_qr_quota(request: HttpRequest) -> JsonResponse:
    """Check if user can create more QR codes (AJAX)"""
    user_id = str(request.user.id)
    
    # DO NOT sync with TOTP profiles - this resets custom URL QR count
    # Custom URL QR codes should count toward quota
    # Only TOTP profiles count is synced on dashboard load for initial accuracy
    
    # Get current quota info without resetting
    can_create, quota_info = SubscriptionManager.check_qr_quota(user_id)
    
    return JsonResponse({
        'can_create': can_create,
        'quota_info': quota_info
    })


# ============= SUBSCRIPTION & PRICING VIEWS =============

@login_required
def pricing_view(request: HttpRequest) -> HttpResponse:
    """Display pricing plans"""
    user_id = str(request.user.id)
    subscription = SubscriptionManager.get_user_subscription(user_id)
    
    context = {
        'plans': PLANS,
        'current_plan': subscription.get('plan_type', 'FREE'),
        'subscription': subscription
    }
    
    return render(request, 'pricing.html', context)


@login_required
def payment_confirmation(request: HttpRequest) -> HttpResponse:
    """Show payment confirmation page before upgrade"""
    plan_type = request.GET.get('plan', 'PRO')
    billing_cycle = request.GET.get('cycle', 'monthly')
    
    if plan_type not in PLANS:
        messages.error(request, 'Invalid plan selected.')
        return redirect('pricing')
    
    plan = PLANS[plan_type]
    price = plan.price_yearly if billing_cycle == 'yearly' else plan.price_monthly
    
    context = {
        'plan_type': plan_type,
        'plan_name': plan.name,
        'billing_cycle': billing_cycle,
        'price': price,
    }
    
    return render(request, 'payment_confirmation.html', context)


@login_required
@require_POST
def upgrade_plan(request: HttpRequest) -> HttpResponse:
    """Upgrade user's subscription plan"""
    user_id = str(request.user.id)
    plan_type = request.POST.get('plan_type', 'PRO')
    billing_cycle = request.POST.get('billing_cycle', 'monthly')
    
    if plan_type not in PLANS:
        messages.error(request, 'Invalid plan selected.')
        return redirect('pricing')
    
    # Get plan details
    plan = PLANS[plan_type]
    price = plan.price_yearly if billing_cycle == 'yearly' else plan.price_monthly
    
    # In production, integrate payment gateway here (Stripe, PayPal, etc.)
    # For now, simulate successful payment
    
    # Upgrade subscription
    SubscriptionManager.upgrade_subscription(user_id, plan_type, billing_cycle)
    
    # Create success message with pricing details
    period_text = 'year' if billing_cycle == 'yearly' else 'month'
    messages.success(
        request, 
        f'🎉 Successfully upgraded to {plan_type} plan! '
        f'${price}/{period_text} ({billing_cycle} billing). '
        f'Your new features are now active!'
    )
    
    # Log the upgrade
    actor = _get_actor(request)
    AuditLog(
        event_type="SUBSCRIPTION_UPGRADED",
        actor=actor,
        target_profile_id=None,
        payload={
            'plan_type': plan_type,
            'billing_cycle': billing_cycle,
            'price': price
        }
    ).save()
    
    return redirect('dashboard')


@login_required
def subscription_details(request: HttpRequest) -> HttpResponse:
    """View subscription details and usage"""
    user_id = str(request.user.id)
    subscription = SubscriptionManager.get_user_subscription(user_id)
    
    # Check plan expiration for non-admin users
    if not request.user.is_superuser and subscription.get('plan_type') != 'FREE':
        current_period_end = subscription.get('current_period_end')
        if current_period_end and current_period_end < datetime.utcnow():
            # Plan expired, downgrade to FREE
            SubscriptionManager.upgrade_subscription(user_id, 'FREE')
            subscription = SubscriptionManager.get_user_subscription(user_id)
            messages.warning(request, '⚠️ Your subscription has expired and has been automatically downgraded to the Free plan.')
    
    # Admin users always have PRO plan (no expiration)
    if request.user.is_superuser and subscription.get('plan_type') != 'PRO':
        SubscriptionManager.upgrade_subscription(user_id, 'PRO')
        subscription = SubscriptionManager.get_user_subscription(user_id)
        # Make admin plan never expire
        db.subscriptions.update_one(
            {'user_id': user_id},
            {'$set': {'current_period_end': datetime.utcnow() + timedelta(days=36500)}}  # 100 years
        )
        subscription = SubscriptionManager.get_user_subscription(user_id)

    # Get QR quota info
    can_create, quota_info = SubscriptionManager.check_qr_quota(user_id)

    context = {
        'subscription': subscription,
        'quota_info': quota_info,
        'plans': PLANS
    }

    return render(request, 'subscription_details.html', context)


@login_required
@require_POST
def cancel_subscription(request: HttpRequest) -> HttpResponse:
    """Cancel user's subscription"""
    user_id = str(request.user.id)
    immediate = request.POST.get('immediate') == 'true'
    
    SubscriptionManager.cancel_subscription(user_id, immediate)
    
    if immediate:
        messages.success(request, 'Subscription cancelled and downgraded to Free plan.')
    else:
        messages.success(request, 'Subscription will be cancelled at the end of the billing period.')
    
    return redirect('subscription_details')


@login_required
@require_POST
def apply_coupon_code(request: HttpRequest) -> HttpResponse:
    """Apply coupon code for plan upgrade"""
    user_id = str(request.user.id)
    coupon_code = request.POST.get('coupon_code', '').strip()
    billing_cycle = request.POST.get('billing_cycle', 'monthly')
    
    if not coupon_code:
        messages.error(request, 'Please enter a coupon code.')
        return redirect('pricing')
    
    success, result = CouponSystem.apply_coupon(user_id, coupon_code, billing_cycle)
    
    if success:
        discount = result['discount']
        plan = result['plan']
        messages.success(request, f'🎉 Coupon applied! {discount}% discount on {plan} plan!')
    else:
        messages.error(request, result.get('error', 'Invalid coupon code.'))
    
    return redirect('pricing')


# ============= PASSWORD RESET VIEWS =============

@login_required
def change_password(request: HttpRequest) -> HttpResponse:
    """Change user password"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep user logged in
            messages.success(request, '✅ Password changed successfully!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'change_password.html', {'form': form})


def password_reset_request(request: HttpRequest) -> HttpResponse:
    """Request password reset (for logged out users)"""
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            # This will send email in production
            # For now, just show success message
            messages.success(request, 'Password reset link has been sent to your email.')
            return redirect('login')
    else:
        form = PasswordResetForm()
    
    return render(request, 'password_reset.html', {'form': form})



# ============= LEGAL PAGES =============

def terms_of_service(request: HttpRequest) -> HttpResponse:
    """Display Terms of Service page"""
    return render(request, 'terms_of_service.html')


def privacy_policy(request: HttpRequest) -> HttpResponse:
    """Display Privacy Policy page"""
    return render(request, 'privacy_policy.html')


# ============= ADMIN USER MANAGEMENT =============

@login_required
def user_management(request: HttpRequest) -> HttpResponse:
    """Admin view for managing all users"""
    if not request.user.is_superuser:
        return HttpResponseForbidden("Admins Only")
    
    from django.contrib.auth.models import User
    from .email_verification import EmailVerification
    
    # Get all users
    users = User.objects.all().order_by('-date_joined')
    
    # Get user data with subscriptions
    user_data = []
    for user in users:
        user_id = str(user.id)
        subscription = SubscriptionManager.get_user_subscription(user_id)
        
        user_data.append({
            'user': user,
            'subscription': subscription
        })
    
    context = {
        'users': user_data
    }
    
    return render(request, 'user_management.html', context)


@login_required
def admin_change_user_plan(request: HttpRequest, user_id: int) -> HttpResponse:
    """Admin endpoint to change user's subscription plan"""
    if not request.user.is_superuser:
        return HttpResponseForbidden("Admins Only")
    
    if request.method != 'POST':
        return redirect('user_management')
    
    new_plan = request.POST.get('new_plan')
    billing_cycle = request.POST.get('billing_cycle', 'monthly')
    
    if new_plan not in ['FREE', 'PRO', 'ENTERPRISE']:
        messages.error(request, 'Invalid plan selected.')
        return redirect('user_management')
    
    try:
        # Update user's subscription
        SubscriptionManager.upgrade_subscription(str(user_id), new_plan, billing_cycle)
        
        from django.contrib.auth.models import User
        user = User.objects.get(id=user_id)
        
        messages.success(request, f'Successfully changed {user.username}\'s plan to {new_plan}!')
    except Exception as e:
        messages.error(request, f'Error changing plan: {str(e)}')
    
    return redirect('user_management')


@login_required
@require_POST
def admin_verify_email(request: HttpRequest, user_id: int) -> JsonResponse:
    """Admin endpoint to manually verify user's email"""
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    from .email_verification import EmailVerification
    
    success = EmailVerification.manual_verify_email(str(user_id))
    
    if success:
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'error': 'Failed to verify email'})


@login_required
@require_POST
def admin_toggle_user_status(request: HttpRequest, user_id: int) -> JsonResponse:
    """Admin endpoint to enable/disable user accounts"""
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    import json
    data = json.loads(request.body)
    is_active = data.get('is_active', True)
    
    try:
        from django.contrib.auth.models import User
        user = User.objects.get(id=user_id)
        user.is_active = is_active
        user.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# ============= EMAIL VERIFICATION =============

def verify_email(request: HttpRequest, token: str) -> HttpResponse:
    """Verify user's email with token"""
    from .email_verification import EmailVerification
    
    success, result = EmailVerification.verify_token(token)
    
    if success:
        messages.success(request, 'Email verified successfully! You can now log in.')
        return redirect('login')
    else:
        messages.error(request, result.get('error', 'Invalid verification token'))
        return redirect('home')


@login_required
def resend_verification_email(request: HttpRequest) -> HttpResponse:
    """Resend verification email to user"""
    from .email_verification import EmailVerification
    
    user_id = str(request.user.id)
    
    # Check if already verified
    if EmailVerification.is_email_verified(user_id):
        messages.info(request, 'Your email is already verified!')
        return redirect('dashboard')
    
    # Send verification email
    success = EmailVerification.resend_verification_email(
        user_id, 
        request.user.email, 
        request.user.username, 
        request
    )
    
    if success:
        messages.success(request, 'Verification email sent! Please check your inbox.')
    else:
        messages.error(request, 'Failed to send verification email. Please try again later.')
    
    return redirect('dashboard')


# ============= QR CODE HISTORY VIEWS =============

@login_required
def qr_history(request: HttpRequest) -> HttpResponse:
    """Display user's QR code generation history"""
    user_id = str(request.user.id)
    
    # Get pagination parameters
    page = int(request.GET.get('page', 1))
    per_page = 20
    skip = (page - 1) * per_page
    
    # Get history
    history = QRHistory.get_user_history(user_id, limit=per_page, skip=skip)
    total_count = QRHistory.get_history_count(user_id)
    total_pages = (total_count + per_page - 1) // per_page
    
    # Get favorites
    favorites = QRHistory.get_favorites(user_id)
    
    context = {
        'history': history,
        'favorites': favorites,
        'page': page,
        'total_pages': total_pages,
        'total_count': total_count,
        'has_prev': page > 1,
        'has_next': page < total_pages
    }
    
    return render(request, 'qr_history.html', context)


@login_required
@require_POST
def regenerate_from_history(request: HttpRequest, history_id: str) -> HttpResponse:
    """Regenerate a QR code from history"""
    import json
    
    user_id = str(request.user.id)
    
    # Get history entry with ownership verification
    entry = QRHistory.get_history_entry(history_id, user_id)
    
    if not entry:
        return JsonResponse({'error': 'History entry not found'}, status=404)
    
    # Regenerate QR code with same settings
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=entry.get('box_size', 10),
        border=entry.get('border', 4),
    )
    qr.add_data(entry['content'])
    qr.make(fit=True)
    
    # Generate image with stored colors
    fg_color = entry.get('fg_color', '000000')
    bg_color = entry.get('bg_color', 'ffffff')
    img = qr.make_image(fill_color=f'#{fg_color}', back_color=f'#{bg_color}')
    
    # Convert to bytes
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    
    return HttpResponse(buf, content_type="image/png")


@login_required
@require_POST
def toggle_history_favorite(request: HttpRequest, history_id: str) -> JsonResponse:
    """Toggle favorite status of a history entry"""
    user_id = str(request.user.id)
    
    new_status = QRHistory.toggle_favorite(history_id, user_id)
    
    if new_status is False and QRHistory.get_history_entry(history_id, user_id) is None:
        return JsonResponse({'error': 'History entry not found'}, status=404)
    
    return JsonResponse({'is_favorite': new_status})


@login_required
@require_POST
def delete_history_entry(request: HttpRequest, history_id: str) -> JsonResponse:
    """Delete a history entry"""
    user_id = str(request.user.id)
    
    deleted = QRHistory.delete_history_entry(history_id, user_id)
    
    if not deleted:
        return JsonResponse({'error': 'History entry not found or already deleted'}, status=404)
    
    return JsonResponse({'success': True})


@login_required
@require_POST
def clear_qr_history(request: HttpRequest) -> HttpResponse:
    """Clear all QR history for user"""
    user_id = str(request.user.id)
    
    count = QRHistory.clear_user_history(user_id)
    
    messages.success(request, f'✓ Cleared {count} history entries')
    return redirect('qr_history')


def verify_2fa(request: HttpRequest) -> HttpResponse:
    """2FA verification step after username/password login"""
    from datetime import datetime, timedelta
    
    # Check if user is in session but not fully authenticated
    pending_user_id = request.session.get('pending_2fa_user_id')
    pending_2fa_timestamp = request.session.get('pending_2fa_timestamp')
    
    if not pending_user_id:
        messages.error(request, 'Invalid 2FA session')
        return redirect('login')
    
    # Session timeout check (5 minutes)
    if pending_2fa_timestamp:
        session_start = datetime.fromisoformat(pending_2fa_timestamp)
        if datetime.utcnow() - session_start > timedelta(minutes=5):
            # Session expired
            del request.session['pending_2fa_user_id']
            del request.session['pending_2fa_timestamp']
            if 'failed_2fa_attempts' in request.session:
                del request.session['failed_2fa_attempts']
            messages.error(request, '⏱️ Your 2FA session has expired. Please log in again.')
            return redirect('login')
    
    # Rate limiting - check failed attempts
    failed_attempts = request.session.get('failed_2fa_attempts', 0)
    lockout_until = request.session.get('2fa_lockout_until')
    
    if lockout_until:
        lockout_time = datetime.fromisoformat(lockout_until)
        if datetime.utcnow() < lockout_time:
            remaining = (lockout_time - datetime.utcnow()).seconds
            messages.error(request, f'🔒 Too many failed attempts. Please wait {remaining} seconds before trying again.')
            return render(request, 'registration/verify_2fa.html', {'locked': True, 'lockout_remaining': remaining})
        else:
            # Lockout expired, reset
            del request.session['2fa_lockout_until']
            request.session['failed_2fa_attempts'] = 0
            failed_attempts = 0
    
    if request.method == 'POST':
        code = request.POST.get('totp_code', '').strip()
        
        if not code:
            messages.error(request, 'Please enter the 6-digit code from your authenticator app')
            return render(request, 'registration/verify_2fa.html')
        
        # Validate code format (must be exactly 6 digits)
        if not code.isdigit() or len(code) != 6:
            messages.error(request, '❌ Code must be exactly 6 digits')
            return render(request, 'registration/verify_2fa.html')
        
        # Get TOTP profile
        profile = TOTPProfile.get_by_user_id(pending_user_id)
        
        if not profile:
            messages.error(request, 'No 2FA profile found. Please contact administrator.')
            return render(request, 'registration/verify_2fa.html')
        
        # Verify the TOTP code
        if profile.verify_totp(code):
            # Code is valid - complete login
            from django.contrib.auth import login
            from django.contrib.auth.models import User
            
            user = User.objects.get(id=pending_user_id)
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            
            # Clear pending session data
            del request.session['pending_2fa_user_id']
            if 'pending_2fa_timestamp' in request.session:
                del request.session['pending_2fa_timestamp']
            if 'failed_2fa_attempts' in request.session:
                del request.session['failed_2fa_attempts']
            if '2fa_lockout_until' in request.session:
                del request.session['2fa_lockout_until']
            
            # Log successful 2FA
            AuditLog(
                event_type="2FA_SUCCESS",
                actor=_get_actor(request),
                target_profile_id=profile._id,
                payload={"message": "2FA verification successful"}
            ).save()
            
            messages.success(request, f'✓ Welcome back, {user.username}!')
            return redirect('dashboard')
        else:
            # Invalid code - increment failed attempts
            failed_attempts += 1
            request.session['failed_2fa_attempts'] = failed_attempts
            
            # Lockout after 5 failed attempts (30 second lockout)
            if failed_attempts >= 5:
                lockout_duration = 30  # seconds
                request.session['2fa_lockout_until'] = (datetime.utcnow() + timedelta(seconds=lockout_duration)).isoformat()
                
                AuditLog(
                    event_type="2FA_LOCKOUT",
                    actor={
                        "user_id": pending_user_id,
                        "ip_address": request.META.get('REMOTE_ADDR'),
                        "user_agent": request.META.get('HTTP_USER_AGENT')
                    },
                    target_profile_id=profile._id,
                    payload={"message": f"Account locked after {failed_attempts} failed 2FA attempts", "lockout_seconds": lockout_duration}
                ).save()
                
                messages.error(request, f'🔒 Too many failed attempts ({failed_attempts}). Account locked for {lockout_duration} seconds.')
            else:
                remaining = 5 - failed_attempts
                messages.error(request, f'❌ Invalid code. {remaining} attempts remaining before lockout.')
            
            # Log failed attempt
            AuditLog(
                event_type="2FA_FAILED",
                actor={
                    "user_id": pending_user_id,
                    "ip_address": request.META.get('REMOTE_ADDR'),
                    "user_agent": request.META.get('HTTP_USER_AGENT')
                },
                target_profile_id=profile._id,
                payload={"message": "Invalid 2FA code attempt", "attempt_number": failed_attempts}
            ).save()
            
            return render(request, 'registration/verify_2fa.html', {'failed_attempts': failed_attempts})
    
    # GET request - show 2FA form
    return render(request, 'registration/verify_2fa.html', {'failed_attempts': failed_attempts})


@login_required
def toggle_2fa(request: HttpRequest) -> HttpResponse:
    """Toggle 2FA on/off for the current user"""
    if request.method != 'POST':
        return redirect('dashboard')
    
    user_id = str(request.user.id)
    profile = TOTPProfile.get_by_user_id(user_id)
    
    if not profile:
        messages.error(request, 'No authenticator profile found. Please contact administrator.')
        return redirect('dashboard')
    
    # Toggle 2FA status
    new_status = not profile.is_2fa_enabled
    
    # Update in database
    actor = _get_actor(request)
    profile.update({'is_2fa_enabled': new_status}, actor)
    
    # Log the change
    AuditLog(
        event_type="2FA_STATUS_CHANGED",
        actor=actor,
        target_profile_id=profile._id,
        payload={"is_2fa_enabled": new_status, "message": f"2FA {'enabled' if new_status else 'disabled'}"}
    ).save()
    
    if new_status:
        messages.success(request, '✓ Two-Factor Authentication has been ENABLED. You will need to enter a code from your authenticator app on next login.')
    else:
        messages.warning(request, '⚠️ Two-Factor Authentication has been DISABLED. Your account is now less secure.')
    
    return redirect('dashboard')


def request_account_recovery(request: HttpRequest) -> HttpResponse:
    """User requests account recovery - sends email to admin"""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        reason = request.POST.get('reason', '').strip()
        
        if not username or not email:
            messages.error(request, 'Please provide both username and email')
            return render(request, 'registration/account_recovery.html')
        
        # Check if user exists
        try:
            from django.contrib.auth.models import User
            user = User.objects.get(username=username, email=email)
        except User.DoesNotExist:
            # Don't reveal if user exists or not (security)
            messages.success(request, 'Recovery request submitted. An admin will review your request.')
            return redirect('login')
        
        # Send email to admin
        from django.core.mail import send_mail
        from django.conf import settings
        
        admin_email = "kmohdhamza10@gmail.com"
        
        subject = f"🔐 Account Recovery Request - {username}"
        message = f"""
Account Recovery Request

User Details:
-------------
Username: {username}
Email: {email}
User ID: {user.id}

Reason for Recovery:
{reason if reason else 'Not provided'}

Request Details:
----------------
IP Address: {request.META.get('REMOTE_ADDR')}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
User Agent: {request.META.get('HTTP_USER_AGENT')}

To reactivate this account:
1. Log in to admin dashboard
2. Go to User Management
3. Find user: {username}
4. Reset their 2FA / Reactivate account

Account Recovery Link:
http://{request.get_host()}/manage/users/

---
KTVS Enterprise - Automated Account Recovery System
        """
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [admin_email],
                fail_silently=False,
            )
            
            # Log the recovery request
            AuditLog(
                event_type="ACCOUNT_RECOVERY_REQUEST",
                actor={
                    "user_id": str(user.id),
                    "ip_address": request.META.get('REMOTE_ADDR'),
                    "user_agent": request.META.get('HTTP_USER_AGENT')
                },
                target_profile_id="system",
                payload={
                    "username": username,
                    "email": email,
                    "reason": reason
                }
            ).save()
            
            messages.success(request, '✓ Recovery request sent to administrator. You will be contacted at your registered email.')
        except Exception as e:
            messages.error(request, 'Failed to send recovery request. Please contact admin directly.')
        
        return redirect('login')
    
    return render(request, 'registration/account_recovery.html')


@login_required
def admin_reset_user_2fa(request: HttpRequest, user_id: int) -> HttpResponse:
    """Admin can reset user's 2FA (regenerate new QR code)"""
    if not request.user.is_superuser:
        return HttpResponseForbidden("Admin access required")
    
    from django.contrib.auth.models import User
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        # Delete old TOTP profile
        db.totp_profiles.delete_many({"user_id": str(user_id)})
        
        # Generate new TOTP profile
        actor = _get_actor(request)
        alphabet = string.ascii_uppercase + '234567'
        seed = ''.join(secrets.choice(alphabet) for _ in range(32))
        
        new_profile = TOTPProfile.create(
            user_id=str(user_id),
            seed=seed,
            metadata={
                "label": user.username,
                "issuer": settings.KTVS_SETTINGS['ISSUER'],
                "digits": settings.KTVS_SETTINGS['TOTP_DIGITS'],
                "period": settings.KTVS_SETTINGS['TOTP_PERIOD'],
                "algorithm": settings.KTVS_SETTINGS['TOTP_ALGORITHM']
            },
            kelley_attributes={
                "role": settings.KTVS_SETTINGS['DEFAULT_KELLEY_ROLE'],
                "function": settings.KTVS_SETTINGS['DEFAULT_KELLEY_FUNCTION']
            },
            security_flags={
                "is_high_privilege": False,
                "is_private": False,
                "revocation_state": "Active"
            },
            actor=actor
        )
        
        # Log admin action - use the new profile's ID
        AuditLog(
            event_type="ADMIN_2FA_RESET",
            actor=actor,
            target_profile_id=new_profile._id,
            payload={"reset_for_user": user.username, "user_id": str(user_id)}
        ).save()
        
        # Send notification email to user
        from django.core.mail import send_mail
        try:
            send_mail(
                '🔐 Your 2FA Has Been Reset',
                f'''Hi {user.username},

Your Two-Factor Authentication (2FA) has been reset by an administrator.

Please log in to your dashboard to scan the new QR code with your authenticator app.

Dashboard: http://{request.get_host()}/dashboard/

If you did not request this change, please contact support immediately.

Best regards,
KTVS Enterprise Team
                ''',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=True,
            )
        except:
            pass
        
        messages.success(request, f'✓ 2FA reset successful for {user.username}. User can now scan new QR code.')
        return redirect('user_management')
    
    return render(request, 'admin_reset_2fa.html', {'target_user': user})
