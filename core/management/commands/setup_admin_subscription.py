"""
Management command to set up admin users with lifetime Pro subscription
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.subscription import SubscriptionManager
from core.mongo import db
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Setup admin users with lifetime Pro subscription'

    def handle(self, *args, **kwargs):
        admin_users = User.objects.filter(is_superuser=True)
        
        for admin in admin_users:
            user_id = str(admin.id)
            
            # Check if subscription exists
            existing_sub = db.subscriptions.find_one({'user_id': user_id})
            
            if existing_sub:
                # Update to PRO with far future expiry
                db.subscriptions.update_one(
                    {'user_id': user_id},
                    {'$set': {
                        'plan_type': 'PRO',
                        'plan_name': 'Pro',
                        'status': 'active',
                        'current_period_end': datetime(2099, 12, 31),  # Far future
                        'cancel_at_period_end': False,
                        'is_admin_lifetime': True
                    }}
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Updated admin user {admin.username} to lifetime Pro plan')
                )
            else:
                # Create new Pro subscription
                SubscriptionManager.create_subscription(user_id, 'PRO', 'yearly')
                # Update with lifetime flag
                db.subscriptions.update_one(
                    {'user_id': user_id},
                    {'$set': {
                        'current_period_end': datetime(2099, 12, 31),
                        'is_admin_lifetime': True
                    }}
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Created lifetime Pro plan for admin {admin.username}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully configured {admin_users.count()} admin users')
        )
