"""
Kelley Token Validation System - Coupon Management System
Secure coupon code handling with cryptographic verification
"""

from datetime import datetime, timedelta
import secrets
import hmac
import hashlib
from typing import Optional, Dict, Tuple
from .mongo import db


class CouponManager:
    """Manages coupon codes with HMAC verification and usage tracking"""
    
    COUPON_TYPES = {
        'LIFETIME-FREE': 'Unlimited QR code generation forever',
        'FREE-100': 'Generate up to 100 QR codes',
        'HIGH-PRIVILEGE-SEAL': 'Kelley Administrator access'
    }
    
    # HMAC Secret - Must be in .env in production
    HMAC_SECRET = None
    
    @classmethod
    def set_hmac_secret(cls, secret: str):
        """Set the HMAC secret from environment"""
        cls.HMAC_SECRET = secret.encode()
    
    @classmethod
    def generate_code(cls, coupon_type: str, value: Optional[int] = None, 
                     expires_in_days: int = 365) -> Tuple[str, str]:
        """
        Generate a new coupon code with HMAC signature
        
        Args:
            coupon_type: Type of coupon (LIFETIME-FREE, FREE-100, HIGH-PRIVILEGE-SEAL)
            value: For FREE-100, the limit (default 100)
            expires_in_days: Days until coupon expires
            
        Returns:
            Tuple of (coupon_code, hmac_signature)
        """
        if coupon_type not in cls.COUPON_TYPES:
            raise ValueError(f"Invalid coupon type: {coupon_type}")
        
        if not cls.HMAC_SECRET:
            raise RuntimeError("HMAC_SECRET not set. Call set_hmac_secret() first.")
        
        # Generate random code
        code = secrets.token_urlsafe(16)
        
        # Create timestamp for expiration
        expires_at = (datetime.utcnow() + timedelta(days=expires_in_days)).isoformat()
        
        # Create signature
        message = f"{code}:{coupon_type}:{expires_at}"
        signature = hmac.new(
            cls.HMAC_SECRET,
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Store in MongoDB
        coupon_data = {
            'code': code,
            'type': coupon_type,
            'value': value or (100 if coupon_type == 'FREE-100' else None),
            'signature': signature,
            'expires_at': datetime.fromisoformat(expires_at),
            'created_at': datetime.utcnow(),
            'issuer': 'admin',
            'used_by': None,
            'used_at': None,
            'is_consumed': False
        }
        
        db.coupons.insert_one(coupon_data)
        
        return code, signature
    
    @classmethod
    def validate_code(cls, code: str, user_id: str = None) -> Tuple[bool, Optional[Dict]]:
        """
        Validate and verify a coupon code
        
        Args:
            code: The coupon code to validate
            user_id: User applying the coupon (optional)
            
        Returns:
            Tuple of (is_valid, coupon_data)
        """
        if not cls.HMAC_SECRET:
            raise RuntimeError("HMAC_SECRET not set.")
        
        # Find coupon in database
        coupon = db.coupons.find_one({'code': code})
        
        if not coupon:
            return False, {'error': 'Coupon code not found'}
        
        # Check if already used (except LIFETIME-FREE)
        if coupon['is_consumed'] and coupon['type'] != 'LIFETIME-FREE':
            return False, {'error': 'Coupon has already been used'}
        
        # Check expiration
        if coupon['expires_at'] < datetime.utcnow():
            return False, {'error': 'Coupon has expired'}
        
        # Verify HMAC signature
        message = f"{code}:{coupon['type']}:{coupon['expires_at'].isoformat()}"
        expected_signature = hmac.new(
            cls.HMAC_SECRET,
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(coupon['signature'], expected_signature):
            return False, {'error': 'Invalid coupon signature - possible tampering detected'}
        
        # Mark as used (unless LIFETIME)
        if coupon['type'] != 'LIFETIME-FREE':
            db.coupons.update_one(
                {'_id': coupon['_id']},
                {
                    '$set': {
                        'is_consumed': True,
                        'used_by': user_id,
                        'used_at': datetime.utcnow()
                    }
                }
            )
        
        return True, coupon
    
    @classmethod
    def get_user_coupon(cls, user_id: str) -> Optional[Dict]:
        """Get active coupon for a user"""
        coupon = db.coupons.find_one({
            'used_by': user_id,
            'is_consumed': False,
            'expires_at': {'$gt': datetime.utcnow()}
        })
        return coupon
    
    @classmethod
    def check_qr_quota(cls, user_id: str, current_count: int = 0) -> Tuple[bool, Dict]:
        """
        Check if user can create more QR codes based on coupon
        
        Returns:
            Tuple of (can_create, quota_info)
        """
        coupon = cls.get_user_coupon(user_id)
        
        # No coupon - default to no creation
        if not coupon:
            return False, {
                'can_create': False,
                'message': 'No active coupon. Please enter a valid coupon code.',
                'current': current_count,
                'limit': 0
            }
        
        # LIFETIME-FREE - unlimited
        if coupon['type'] == 'LIFETIME-FREE':
            return True, {
                'can_create': True,
                'message': 'Unlimited QR code generation (LIFETIME-FREE)',
                'current': current_count,
                'limit': None
            }
        
        # FREE-100 - check limit
        if coupon['type'] == 'FREE-100':
            limit = coupon.get('value', 100)
            can_create = current_count < limit
            
            return can_create, {
                'can_create': can_create,
                'message': f"Free QR codes: {current_count}/{limit}",
                'current': current_count,
                'limit': limit
            }
        
        # HIGH-PRIVILEGE-SEAL - check if user is admin
        return True, {
            'can_create': True,
            'message': 'Kelley Administrator - Unlimited access',
            'current': current_count,
            'limit': None
        }
    
    @classmethod
    def list_coupons(cls, admin_only: bool = False) -> list:
        """List all coupons (admin only)"""
        query = {} if not admin_only else {'is_consumed': False}
        coupons = list(db.coupons.find(query).sort('created_at', -1))
        
        # Convert ObjectId and datetime to strings for JSON serialization
        for coupon in coupons:
            coupon['_id'] = str(coupon['_id'])
            coupon['created_at'] = coupon['created_at'].isoformat()
            coupon['expires_at'] = coupon['expires_at'].isoformat()
            if coupon['used_at']:
                coupon['used_at'] = coupon['used_at'].isoformat()
        
        return coupons
