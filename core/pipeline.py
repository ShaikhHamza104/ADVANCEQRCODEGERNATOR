"""

Social auth pipeline to automatically create TOTP profiles for OAuth users
"""
from .totp import TOTPProfile
import secrets
import string
import sys
import traceback

def create_totp_profile(backend, user, response, *args, **kwargs):
    """
    Pipeline function to create TOTP profile for new OAuth users
    """
    try:
        print(f"DEBUG: Starting create_totp_profile for user {user.username if user else 'None'}", file=sys.stderr)
        
        if user and not kwargs.get('is_new', False):
            # Only create for existing users without profiles
            user_id = str(user.id)
            existing_profile = TOTPProfile.get_by_user_id(user_id)
            
            if not existing_profile:
                # Generate random seed
                alphabet = string.ascii_uppercase + '234567'
                seed = ''.join(secrets.choice(alphabet) for _ in range(32))
                
                # Get IP address
                ip_address = "0.0.0.0"
                try:
                    request = backend.strategy.request
                    if request:
                        ip_address = request.META.get('REMOTE_ADDR', "0.0.0.0")
                except Exception as e:
                    print(f"DEBUG: Failed to get IP: {e}", file=sys.stderr)

                actor = {
                    "user_id": "oauth_pipeline",
                    "ip_address": ip_address,
                    "user_agent": f"{backend.name} OAuth"
                }
                
                TOTPProfile.create(
                    user_id=user_id,
                    seed=seed,
                    metadata={
                        "label": user.get_full_name() or user.username,
                        "issuer": "KTVS",
                        "digits": 6,
                        "period": 30,
                        "algorithm": "SHA1"
                    },
                    kelley_attributes={
                        "role": "User",
                        "function": "OAuth Authenticated",
                        "oauth_provider": backend.name
                    },
                    security_flags={
                        "is_high_privilege": False,
                        "is_private": False,
                        "revocation_state": "Active"
                    },
                    actor=actor
                )
                print(f"DEBUG: Created TOTP profile for existing user {user.username}", file=sys.stderr)
        
        elif user and kwargs.get('is_new', False):
            # New user from OAuth
            user_id = str(user.id)
            
            # Generate random seed
            alphabet = string.ascii_uppercase + '234567'
            seed = ''.join(secrets.choice(alphabet) for _ in range(32))
            
            # Get IP address
            ip_address = "0.0.0.0"
            try:
                request = backend.strategy.request
                if request:
                    ip_address = request.META.get('REMOTE_ADDR', "0.0.0.0")
            except Exception as e:
                print(f"DEBUG: Failed to get IP: {e}", file=sys.stderr)
                
            actor = {
                "user_id": "oauth_registration",
                "ip_address": ip_address,
                "user_agent": f"{backend.name} OAuth"
            }
            
            TOTPProfile.create(
                user_id=user_id,
                seed=seed,
                metadata={
                    "label": user.get_full_name() or user.username,
                    "issuer": "KTVS",
                    "digits": 6,
                    "period": 30,
                    "algorithm": "SHA1"
                },
                kelley_attributes={
                    "role": "User",
                    "function": "OAuth New User",
                    "oauth_provider": backend.name
                },
                security_flags={
                    "is_high_privilege": False,
                    "is_private": False,
                    "revocation_state": "Active"
                },
                actor=actor
            )
            print(f"DEBUG: Created TOTP profile for new user {user.username}", file=sys.stderr)

    except Exception as e:
        print(f"ERROR in create_totp_profile pipeline: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        # We generally don't want to stop the login flow just because TOTP profile creation failed,
        # but in this app, TOTP seems central. For now, we swallow the error to allow login to complete.
        return None
