"""
Context processors for KTVS
Adds global variables to all templates
"""
from datetime import datetime
from .mongo import db


def active_coupons(request):
    """Add active coupons to template context"""
    try:
        # Get active coupons that haven't expired and have remaining uses
        coupons = list(db.coupons.find({
            'active': True,
            'expires_at': {'$gt': datetime.utcnow()},
            '$expr': {'$lt': ['$current_uses', '$max_uses']}
        }).sort('discount_percent', -1).limit(10))
        
        # Format coupon data for display
        coupon_list = []
        for coupon in coupons:
            coupon_list.append({
                'code': coupon['code'],
                'discount': coupon['discount_percent'],
                'plan': coupon['plan_type']
            })
        
        return {'active_coupons': coupon_list}
    except Exception:
        return {'active_coupons': []}
