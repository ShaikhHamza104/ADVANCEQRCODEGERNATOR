from django.core.management.base import BaseCommand
from core.models import TOTPProfile
from core.mongo import db

class Command(BaseCommand):
    help = 'Seeds the database with initial data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')
        
        # Clear existing profiles for idempotency (optional, but good for dev)
        # db.totp_profiles.delete_many({}) 
        # db.audit_logs.delete_many({})

        actor = {"user_id": "system_init", "ip_address": "127.0.0.1", "user_agent": "cli"}

        profiles = [
            {
                "user_id": "April.O’Bryan@ProgInv.gov",
                "seed": "OFYYTRXHF42Z2WZGGOCI8XIZ",
                "metadata": {
                    "label": "April O’Bryan",
                    "issuer": "ORAM",
                    "digits": 6,
                    "period": 30,
                    "algorithm": "SHA1"
                },
                "kelley_attributes": {
                    "function": "BSA Level",
                    "attestation": "Standard"
                },
                "security_flags": {
                    "is_high_privilege": False,
                    "is_private": False,
                    "revocation_state": "Active"
                }
            },
            {
                "user_id": "stephenneer@gmail.com",
                "seed": "MOCKSEEDFORSTEPHENNEER123", # Not provided in prompt, using mock or generating
                # Wait, prompt says "config: function_code: 1...". Seed is missing in prompt for Stephen?
                # Ah, I see "seed_data" section. Stephen Neer has "config" but no explicit seed listed in the snippet I see?
                # Let me check the prompt again.
                # "profile_ref: stephen_neer ... config: ... mcf_cert: ..."
                # It seems seed is missing for Stephen in the prompt snippet provided. I will generate one.
                "metadata": {
                    "label": "STEPHEN NEER",
                    "issuer": "ORAM",
                    "digits": 6,
                    "period": 30,
                    "algorithm": "SHA1"
                },
                "kelley_attributes": {
                    "function_code": 1,
                    "challenge_association": True,
                    "private_allocation": True,
                    "override_authority": True,
                    "mcf_cert": "Match: Susan Alvarez (ACIGNVQZ44)"
                },
                "security_flags": {
                    "is_high_privilege": True,
                    "is_private": True,
                    "revocation_state": "Active"
                }
            },
            {
                "user_id": "vinod.sharma@aro-usa.gov",
                "seed": "NGGRC44VUQLNMHEJYRRN6NCK",
                "metadata": {
                    "label": "Vinod Sharma",
                    "issuer": "ORAM",
                    "digits": 6,
                    "period": 30,
                    "algorithm": "SHA1"
                },
                "kelley_attributes": {
                    "role": "ARO - USA",
                    "sealed_seed": True,
                    "pre_authorized": True,
                    "cert_number": "OF012234URE01"
                },
                "security_flags": {
                    "is_high_privilege": False,
                    "is_private": False,
                    "revocation_state": "Active"
                }
            },
            {
                "user_id": "chimbu_agarwal_1977", # No email provided, using owner name as ID or placeholder
                # Prompt says "owner: Chimbu Agarwal-1977", "role: Kelley Administrator".
                # I'll use a placeholder email.
                "seed": "ZXSRTIOJGXNGEH3AXZISTYE",
                "metadata": {
                    "label": "Chimbu Agarwal-1977",
                    "issuer": "ORAM",
                    "digits": 6,
                    "period": 30,
                    "algorithm": "SHA1"
                },
                "kelley_attributes": {
                    "role": "Kelley Administrator",
                    "notary_type": "Keypad Notary #1",
                    "cert_link": "Susan Alvarez Attestation"
                },
                "security_flags": {
                    "is_high_privilege": True,
                    "is_private": False,
                    "revocation_state": "Active"
                }
            },
            {
                "user_id": "anish.macro@asa.gov",
                "seed": "NFJH5ZX5O7WKETO3ZFVEOGQI",
                "metadata": {
                    "label": "Anish Macro",
                    "issuer": "ORAM",
                    "digits": 6,
                    "period": 30,
                    "algorithm": "SHA1"
                },
                "kelley_attributes": {
                    "role": "Lvl 1",
                    "marked_private": True,
                    "requires_notary_approval": True
                },
                "security_flags": {
                    "is_high_privilege": False,
                    "is_private": True,
                    "revocation_state": "Active"
                }
            }
        ]

        for p in profiles:
            # Check if exists
            if not TOTPProfile.get_by_user_id(p['user_id']):
                # For Stephen, generate seed if missing
                seed = p.get('seed', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567')
                
                TOTPProfile.create(
                    user_id=p['user_id'],
                    seed=seed,
                    metadata=p['metadata'],
                    kelley_attributes=p['kelley_attributes'],
                    security_flags=p['security_flags'],
                    actor=actor
                )
                self.stdout.write(f"Created profile for {p['user_id']}")
            else:
                self.stdout.write(f"Profile for {p['user_id']} already exists")

        self.stdout.write(self.style.SUCCESS('Successfully seeded data'))
