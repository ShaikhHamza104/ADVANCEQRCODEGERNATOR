from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import List, Optional, Any
from .mongo import db
from .crypto import crypto_manager
from bson import ObjectId
import pyotp
import time

@dataclass
class AuditLog:
    event_type: str
    actor: dict  # {user_id, ip_address, user_agent}
    target_profile_id: str
    payload: dict
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def save(self):
        data = asdict(self)
        if isinstance(data['target_profile_id'], str):
            data['target_profile_id'] = ObjectId(data['target_profile_id'])
        db.audit_logs.insert_one(data)

@dataclass
class TOTPProfile:
    user_id: str
    seed_encrypted: str  # Base64 encoded encrypted seed
    metadata: dict
    kelley_attributes: dict
    security_flags: dict
    is_2fa_enabled: bool = True  # Whether 2FA is required for login (enabled by default)
    history: List[dict] = field(default_factory=list)
    _id: Optional[str] = None
    
    @property
    def id(self):
        """Property to access _id in templates (Django doesn't allow underscore-prefixed attributes)"""
        return self._id

    @classmethod
    def create(cls, user_id, seed, metadata, kelley_attributes, security_flags, actor):
        encrypted_seed = crypto_manager.encrypt_to_b64(seed)
        
        profile = cls(
            user_id=user_id,
            seed_encrypted=encrypted_seed,
            metadata=metadata,
            kelley_attributes=kelley_attributes,
            security_flags=security_flags,
            history=[]
        )
        
        data = asdict(profile)
        del data['_id']
        
        result = db.totp_profiles.insert_one(data)
        profile._id = str(result.inserted_id)
        
        # Audit Log
        AuditLog(
            event_type="PROFILE_CREATED",
            actor=actor,
            target_profile_id=profile._id,
            payload={"metadata": metadata}
        ).save()
        
        return profile

    @classmethod
    def get_by_user_id(cls, user_id):
        data = db.totp_profiles.find_one({"user_id": user_id})
        if data:
            data['_id'] = str(data['_id'])
            return cls(**data)
        return None

    def get_decrypted_seed(self, actor):
        # Audit Log for viewing seed
        AuditLog(
            event_type="VIEW_SEED",
            actor=actor,
            target_profile_id=self._id,
            payload={"message": f"Viewed by: {actor.get('user_id')}"}
        ).save()
        
        return crypto_manager.decrypt_from_b64(self.seed_encrypted)

    def update(self, updates: dict, actor):
        # Append to history
        history_entry = {
            "timestamp": datetime.utcnow(),
            "actor": actor,
            "changes": updates
        }
        
        db.totp_profiles.update_one(
            {"_id": ObjectId(self._id)},
            {
                "$set": updates,
                "$push": {"history": history_entry}
            }
        )
        
        # Audit Log
        AuditLog(
            event_type="PROFILE_MODIFIED",
            actor=actor,
            target_profile_id=self._id,
            payload=updates
        ).save()

        # Update local object
        for k, v in updates.items():
            setattr(self, k, v)
        self.history.append(history_entry)

    def verify_totp(self, code: str) -> bool:
        """Verify a TOTP code against the stored seed."""
        try:
            seed = crypto_manager.decrypt_from_b64(self.seed_encrypted)
            totp = pyotp.TOTP(seed)
            # Allow 1 time window before and after (30 seconds each) for clock drift
            return totp.verify(code, valid_window=1)
        except Exception:
            return False
    
    def generate_current_code(self) -> str:
        """Generate the current TOTP code (for testing/admin purposes)."""
        seed = crypto_manager.decrypt_from_b64(self.seed_encrypted)
        totp = pyotp.TOTP(seed)
        return totp.now()
