"""
Management command to reset QR code counts to match actual TOTP profiles
"""
from django.core.management.base import BaseCommand
from core.mongo import db


class Command(BaseCommand):
    help = 'Reset QR code counts to match actual TOTP profiles in database'

    def handle(self, *args, **options):
        """Reset all user QR counts"""
        subscriptions = db.subscriptions.find({})
        
        fixed_count = 0
        for sub in subscriptions:
            user_id = sub['user_id']
            
            # Count actual TOTP profiles for this user
            actual_count = db.totp_profiles.count_documents({'user_id': user_id})
            
            # Get current count
            current_count = sub.get('usage', {}).get('qr_count', 0)
            
            if current_count != actual_count:
                # Update to actual count
                db.subscriptions.update_one(
                    {'user_id': user_id},
                    {'$set': {'usage.qr_count': actual_count}}
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ User {user_id}: Fixed {current_count} → {actual_count}'
                    )
                )
                fixed_count += 1
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ User {user_id}: Already correct ({actual_count})'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Reset complete! Fixed {fixed_count} user(s)'
            )
        )
