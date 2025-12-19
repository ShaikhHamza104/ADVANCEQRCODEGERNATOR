"""
Kelley Seal / AARO Tag Detection
Identifies high-privilege tokens and Kelley Administrators
"""

import re
from typing import Optional, Tuple, Dict
from datetime import datetime


class KelleySealDetector:
    """Detects Kelley Seal markers in TOTP seeds and profiles"""
    
    # Kelley Seal pattern matching
    KELLEY_SEAL_PATTERN = r'Kelley\s+Seal.*?id:\s*([A-Z0-9]+)'
    
    # AARO Tag pattern
    AARO_TAG_PATTERN = r'AARO\s+Tag.*?challenge:\s*(\d)'
    
    # Known Kelley Administrators (preloaded)
    KNOWN_ADMINISTRATORS = {
        'chimbu.shaikh@example.com': {
            'name': 'Chimbu Shaikh',
            'seed_identifier': 'ZXSRTIOJGXNGEH3AXZISTYE',
            'issuer': 'ORAM',
            'role': 'Kelley Administrator',
            'created_at': '2025-01-01'
        }
    }
    
    @classmethod
    def detect_kelley_seal(cls, seed_data: str) -> Tuple[bool, Optional[str]]:
        """
        Detect Kelley Seal in seed data
        
        Args:
            seed_data: Raw seed or metadata string
            
        Returns:
            Tuple of (is_sealed, seal_id)
        """
        match = re.search(cls.KELLEY_SEAL_PATTERN, seed_data, re.IGNORECASE)
        if match:
            seal_id = match.group(1)
            return True, seal_id
        return False, None
    
    @classmethod
    def detect_aaro_tag(cls, metadata: Dict) -> Tuple[bool, Optional[int]]:
        """
        Detect AARO Tag in profile metadata
        
        Args:
            metadata: Profile metadata dictionary
            
        Returns:
            Tuple of (is_tagged, challenge_digit)
        """
        comment = metadata.get('comment', '')
        match = re.search(cls.AARO_TAG_PATTERN, comment, re.IGNORECASE)
        if match:
            challenge_digit = int(match.group(1))
            if 1 <= challenge_digit <= 6:
                return True, challenge_digit
        return False, None
    
    @classmethod
    def promote_to_admin(cls, user_email: str, seal_id: str) -> Dict:
        """
        Promote user to Kelley Administrator upon seal detection
        
        Args:
            user_email: User's email
            seal_id: Kelley Seal ID
            
        Returns:
            Admin profile data
        """
        from .mongo import db
        
        admin_data = {
            'email': user_email,
            'role': 'kelley_administrator',
            'seal_id': seal_id,
            'promoted_at': datetime.utcnow(),
            'privileges': [
                'view_seed',
                'export_seed',
                'create_profile',
                'modify_profile',
                'delete_profile',
                'view_audit_logs',
                'manage_coupons',
                'view_mcfcert'
            ]
        }
        
        # Store in database
        db.kelley_admins.update_one(
            {'email': user_email},
            {'$set': admin_data},
            upsert=True
        )
        
        return admin_data
    
    @classmethod
    def is_kelley_admin(cls, user_email: str) -> bool:
        """Check if user is a Kelley Administrator"""
        from .mongo import db
        
        admin = db.kelley_admins.find_one({'email': user_email})
        return admin is not None
    
    @classmethod
    def get_mcfcert(cls, seal_id: str) -> Optional[Dict]:
        """
        Get Attestation Seal (mcfCert) for a given seal ID
        
        Returns:
            Certificate data with security attributes
        """
        from .mongo import db
        
        cert = db.mcfcert.find_one({'seal_id': seal_id})
        if cert:
            cert['_id'] = str(cert['_id'])
        return cert
    
    @classmethod
    def create_attestation_seal(cls, user_email: str, metadata: Dict) -> Dict:
        """
        Create an Attestation Seal (mcfCert) for high-privilege users
        
        Args:
            user_email: User email
            metadata: User metadata
            
        Returns:
            Certificate data
        """
        from .mongo import db
        
        mcfcert_data = {
            'user_email': user_email,
            'user_name': metadata.get('label', user_email),
            'issuer': metadata.get('issuer', 'KTVS'),
            'created_at': datetime.utcnow(),
            'seal_attributes': {
                'confidentiality_level': 'SECRET',
                'integrity_check': True,
                'audit_required': True
            },
            'validity_period': {
                'not_before': datetime.utcnow(),
                'not_after': datetime.utcnow().replace(year=datetime.utcnow().year + 2)
            }
        }
        
        result = db.mcfcert.insert_one(mcfcert_data)
        mcfcert_data['_id'] = str(result.inserted_id)
        
        return mcfcert_data
    
    @classmethod
    def verify_seal_integrity(cls, profile_data: Dict) -> Tuple[bool, str]:
        """
        Verify the integrity of a sealed profile
        
        Args:
            profile_data: Profile dictionary
            
        Returns:
            Tuple of (is_valid, message)
        """
        required_fields = ['user_id', 'seed_encrypted', 'metadata', 'security_flags']
        
        for field in required_fields:
            if field not in profile_data:
                return False, f"Missing required field: {field}"
        
        # Check for tampering indicators
        if 'created_at' in profile_data:
            created_at = profile_data['created_at']
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at)
            
            age_hours = (datetime.utcnow() - created_at).total_seconds() / 3600
            if age_hours > 87600:  # ~10 years
                return False, "Profile is too old (possible corruption)"
        
        return True, "Profile integrity verified"
