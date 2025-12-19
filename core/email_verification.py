"""
Email Verification System
Handles email verification tokens and validation
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import secrets
import hashlib
from .mongo import db
from django.core.mail import send_mail
from django.conf import settings


class EmailVerification:
    """Manage email verification for user accounts"""
    
    @staticmethod
    def create_verification_token(user_id: str, email: str) -> str:
        """Generate a unique verification token for a user"""
        # Generate a secure random token
        token = secrets.token_urlsafe(32)
        
        # Hash the token for storage
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        # Store in database
        verification = {
            'user_id': user_id,
            'email': email,
            'token_hash': token_hash,
            'created_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(hours=24),
            'verified': False,
            'used': False
        }
        
        db.email_verifications.insert_one(verification)
        
        return token
    
    @staticmethod
    def verify_token(token: str) -> tuple[bool, Optional[Dict[str, Any]]]:
        """Verify an email verification token"""
        # Hash the provided token
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        # Find the verification record
        verification = db.email_verifications.find_one({
            'token_hash': token_hash,
            'used': False,
            'verified': False
        })
        
        if not verification:
            return False, {'error': 'Invalid or expired verification token'}
        
        # Check if token has expired
        if verification['expires_at'] < datetime.utcnow():
            return False, {'error': 'Verification token has expired'}
        
        # Mark as verified and used
        db.email_verifications.update_one(
            {'_id': verification['_id']},
            {'$set': {
                'verified': True,
                'used': True,
                'verified_at': datetime.utcnow()
            }}
        )
        
        # Update user's email verification status
        db.user_profiles.update_one(
            {'user_id': verification['user_id']},
            {'$set': {'email_verified': True, 'email_verified_at': datetime.utcnow()}},
            upsert=True
        )
        
        return True, {
            'success': True,
            'user_id': verification['user_id'],
            'email': verification['email']
        }
    
    @staticmethod
    def send_verification_email(user_id: str, email: str, username: str, request) -> bool:
        """Send verification email to user"""
        try:
            # Generate verification token
            token = EmailVerification.create_verification_token(user_id, email)
            
            # Build verification URL
            verification_url = request.build_absolute_uri(f'/verify-email/{token}/')
            
            # Email subject and message
            subject = 'KTVS Enterprise - Verify Your Email Address'
            message = f"""
Hello {username},

Thank you for registering with KTVS Enterprise!

Please verify your email address by clicking the link below:

{verification_url}

This link will expire in 24 hours.

If you didn't create this account, please ignore this email.

Best regards,
KTVS Enterprise Team

---
Secured with AES-256-GCM Encryption | NIST SP 800-63B Compliant
            """
            
            # For development, just log the URL
            if settings.DEBUG:
                print(f"\n{'='*60}")
                print(f"EMAIL VERIFICATION FOR: {email}")
                print(f"Verification URL: {verification_url}")
                print(f"{'='*60}\n")
                return True
            
            # In production, send actual email
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
            return True
            
        except Exception as e:
            print(f"Error sending verification email: {str(e)}")
            return False
    
    @staticmethod
    def is_email_verified(user_id: str) -> bool:
        """Check if user's email is verified"""
        profile = db.user_profiles.find_one({'user_id': user_id})
        if profile:
            return profile.get('email_verified', False)
        return False
    
    @staticmethod
    def resend_verification_email(user_id: str, email: str, username: str, request) -> bool:
        """Resend verification email"""
        # Invalidate old tokens
        db.email_verifications.update_many(
            {'user_id': user_id, 'used': False},
            {'$set': {'used': True}}
        )
        
        # Send new verification email
        return EmailVerification.send_verification_email(user_id, email, username, request)
    
    @staticmethod
    def manual_verify_email(user_id: str) -> bool:
        """Manually verify a user's email (admin only)"""
        try:
            db.user_profiles.update_one(
                {'user_id': user_id},
                {'$set': {
                    'email_verified': True,
                    'email_verified_at': datetime.utcnow(),
                    'manually_verified': True
                }},
                upsert=True
            )
            return True
        except Exception as e:
            print(f"Error manually verifying email: {str(e)}")
            return False
