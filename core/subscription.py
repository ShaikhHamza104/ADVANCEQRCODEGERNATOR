"""
Subscription and Pricing Management System
Supports: Free, Pro, and Enterprise plans
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from .mongo import db
from bson import ObjectId


@dataclass
class PlanFeatures:
    """Plan feature definitions"""
    name: str
    qr_limit: int  # Maximum QR codes (-1 = unlimited)
    storage_mb: int  # Storage limit in MB
    api_calls_per_day: int
    priority_support: bool
    custom_branding: bool
    advanced_analytics: bool
    price_monthly: float
    price_yearly: float


# Plan Definitions
PLANS = {
    'FREE': PlanFeatures(
        name='Free',
        qr_limit=100,
        storage_mb=100,
        api_calls_per_day=100,
        priority_support=False,
        custom_branding=False,
        advanced_analytics=False,
        price_monthly=0.0,
        price_yearly=0.0
    ),
    'PRO': PlanFeatures(
        name='Pro',
        qr_limit=500,
        storage_mb=1000,  # 1GB
        api_calls_per_day=10000,
        priority_support=True,
        custom_branding=True,
        advanced_analytics=False,
        price_monthly=9.99,
        price_yearly=99.99  # ~17% discount
    ),
    'ENTERPRISE': PlanFeatures(
        name='Enterprise',
        qr_limit=-1,  # Unlimited
        storage_mb=-1,  # Unlimited
        api_calls_per_day=-1,  # Unlimited
        priority_support=True,
        custom_branding=True,
        advanced_analytics=True,
        price_monthly=49.99,
        price_yearly=499.99  # ~17% discount
    )
}


class SubscriptionManager:
    """Manage user subscriptions and plan features"""
    
    @staticmethod
    def get_user_subscription(user_id: str) -> Dict[str, Any]:
        """Get user's current subscription details"""
        sub = db.subscriptions.find_one({'user_id': user_id})
        
        if not sub:
            # Create default FREE subscription
            return SubscriptionManager.create_subscription(user_id, 'FREE')
        
        return sub
    
    @staticmethod
    def create_subscription(user_id: str, plan_type: str = 'FREE', billing_cycle: str = 'monthly') -> Dict[str, Any]:
        """Create a new subscription for a user"""
        plan = PLANS.get(plan_type, PLANS['FREE'])
        
        subscription = {
            'user_id': user_id,
            'plan_type': plan_type,
            'plan_name': plan.name,
            'billing_cycle': billing_cycle,  # 'monthly' or 'yearly'
            'status': 'active',
            'created_at': datetime.utcnow(),
            'current_period_start': datetime.utcnow(),
            'current_period_end': datetime.utcnow() + timedelta(days=30 if billing_cycle == 'monthly' else 365),
            'cancel_at_period_end': False,
            'features': {
                'qr_limit': plan.qr_limit,
                'storage_mb': plan.storage_mb,
                'api_calls_per_day': plan.api_calls_per_day,
                'priority_support': plan.priority_support,
                'custom_branding': plan.custom_branding,
                'advanced_analytics': plan.advanced_analytics
            },
            'usage': {
                'qr_count': 0,
                'storage_used_mb': 0,
                'api_calls_today': 0,
                'last_api_call_date': None
            }
        }
        
        result = db.subscriptions.insert_one(subscription)
        subscription['_id'] = result.inserted_id
        
        return subscription
    
    @staticmethod
    def upgrade_subscription(user_id: str, new_plan_type: str, billing_cycle: str = 'monthly') -> Dict[str, Any]:
        """Upgrade user's subscription to a new plan"""
        plan = PLANS.get(new_plan_type, PLANS['FREE'])
        
        update_data = {
            'plan_type': new_plan_type,
            'plan_name': plan.name,
            'billing_cycle': billing_cycle,
            'upgraded_at': datetime.utcnow(),
            'current_period_start': datetime.utcnow(),
            'current_period_end': datetime.utcnow() + timedelta(days=30 if billing_cycle == 'monthly' else 365),
            'features': {
                'qr_limit': plan.qr_limit,
                'storage_mb': plan.storage_mb,
                'api_calls_per_day': plan.api_calls_per_day,
                'priority_support': plan.priority_support,
                'custom_branding': plan.custom_branding,
                'advanced_analytics': plan.advanced_analytics
            }
        }
        
        db.subscriptions.update_one(
            {'user_id': user_id},
            {'$set': update_data}
        )
        
        return SubscriptionManager.get_user_subscription(user_id)
    
    @staticmethod
    def check_feature_access(user_id: str, feature: str) -> bool:
        """Check if user has access to a specific feature"""
        sub = SubscriptionManager.get_user_subscription(user_id)
        return sub.get('features', {}).get(feature, False)
    
    @staticmethod
    def check_qr_quota(user_id: str) -> tuple[bool, Dict[str, Any]]:
        """Check if user can create more QR codes"""
        sub = SubscriptionManager.get_user_subscription(user_id)
        
        qr_limit = sub['features']['qr_limit']
        current_count = sub['usage']['qr_count']
        
        if qr_limit == -1:  # Unlimited
            return True, {
                'can_create': True,
                'limit': 'unlimited',
                'used': current_count,
                'remaining': 'unlimited'
            }
        
        can_create = current_count < qr_limit
        
        return can_create, {
            'can_create': can_create,
            'limit': qr_limit,
            'used': current_count,
            'remaining': max(0, qr_limit - current_count)
        }
    
    @staticmethod
    def increment_qr_count(user_id: str) -> None:
        """Increment user's QR code count"""
        db.subscriptions.update_one(
            {'user_id': user_id},
            {'$inc': {'usage.qr_count': 1}}
        )
    
    @staticmethod
    def decrement_qr_count(user_id: str) -> None:
        """Decrement user's QR code count (when deleting)"""
        db.subscriptions.update_one(
            {'user_id': user_id},
            {'$inc': {'usage.qr_count': -1}}
        )
    
    @staticmethod
    def cancel_subscription(user_id: str, immediate: bool = False) -> Dict[str, Any]:
        """Cancel user's subscription"""
        if immediate:
            # Downgrade to FREE immediately
            return SubscriptionManager.upgrade_subscription(user_id, 'FREE')
        else:
            # Cancel at end of billing period
            db.subscriptions.update_one(
                {'user_id': user_id},
                {'$set': {'cancel_at_period_end': True}}
            )
            return SubscriptionManager.get_user_subscription(user_id)


class CouponSystem:
    """Enhanced coupon system for Pro plan upgrades"""
    
    @staticmethod
    def create_coupon(code: str, discount_percent: int, plan_type: str = 'PRO', 
                     max_uses: int = 1, expiry_days: int = 30) -> Dict[str, Any]:
        """Create a new coupon code"""
        coupon = {
            'code': code.upper(),
            'discount_percent': discount_percent,
            'plan_type': plan_type,
            'max_uses': max_uses,
            'current_uses': 0,
            'created_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(days=expiry_days),
            'active': True
        }
        
        result = db.coupons.insert_one(coupon)
        coupon['_id'] = result.inserted_id
        
        return coupon
    
    @staticmethod
    def validate_coupon(code: str) -> tuple[bool, Dict[str, Any]]:
        """Validate a coupon code"""
        coupon = db.coupons.find_one({'code': code.upper(), 'active': True})
        
        if not coupon:
            return False, {'error': 'Invalid coupon code'}
        
        # Check expiry
        if coupon['expires_at'] < datetime.utcnow():
            return False, {'error': 'Coupon has expired'}
        
        # Check usage limit
        if coupon['current_uses'] >= coupon['max_uses']:
            return False, {'error': 'Coupon usage limit reached'}
        
        return True, {
            'valid': True,
            'discount_percent': coupon['discount_percent'],
            'plan_type': coupon['plan_type']
        }
    
    @staticmethod
    def apply_coupon(user_id: str, code: str, billing_cycle: str = 'monthly') -> tuple[bool, Dict[str, Any]]:
        """Apply a coupon to upgrade user's subscription"""
        is_valid, result = CouponSystem.validate_coupon(code)
        
        if not is_valid:
            return False, result
        
        # Check if user already has this plan or higher
        current_sub = SubscriptionManager.get_user_subscription(user_id)
        current_plan = current_sub.get('plan_type', 'FREE')
        target_plan = result['plan_type']
        
        plan_hierarchy = {'FREE': 0, 'PRO': 1, 'ENTERPRISE': 2}
        current_level = plan_hierarchy.get(current_plan, 0)
        target_level = plan_hierarchy.get(target_plan, 0)
        
        if current_level >= target_level:
            if current_plan == target_plan:
                return False, {'error': f'You already have the {current_plan} plan! No need to apply this coupon.'}
            else:
                return False, {'error': f'You already have the {current_plan} plan which is higher than {target_plan}. No upgrade needed!'}
        
        # Increment usage
        db.coupons.update_one(
            {'code': code.upper()},
            {'$inc': {'current_uses': 1}}
        )
        
        # Upgrade subscription
        plan_type = result['plan_type']
        discount = result['discount_percent']
        
        sub = SubscriptionManager.upgrade_subscription(user_id, plan_type, billing_cycle)
        
        # Record coupon usage
        db.coupon_usage.insert_one({
            'user_id': user_id,
            'code': code.upper(),
            'plan_type': plan_type,
            'discount_percent': discount,
            'applied_at': datetime.utcnow()
        })
        
        return True, {
            'success': True,
            'plan': plan_type,
            'discount': discount,
            'subscription': sub
        }
