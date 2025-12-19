"""
QR Code History Management
Allows users to view their previously generated QR codes
"""

from datetime import datetime
from typing import Dict, List, Any
from .mongo import db
from bson import ObjectId


class QRHistory:
    """Manage user QR code generation history"""
    
    @staticmethod
    def add_to_history(user_id: str, qr_data: Dict[str, Any]) -> str:
        """
        Add a QR code to user's history
        
        Args:
            user_id: User ID
            qr_data: Dictionary containing:
                - qr_type: 'url' or 'totp'
                - content: URL or TOTP name
                - fg_color: Foreground color (hex)
                - bg_color: Background color (hex)
                - platform: Target platform (optional)
                - box_size: QR box size (optional)
                - border: QR border size (optional)
        
        Returns:
            History entry ID
        """
        history_entry = {
            'user_id': user_id,
            'qr_type': qr_data.get('qr_type', 'url'),
            'content': qr_data.get('content', ''),
            'fg_color': qr_data.get('fg_color', '000000'),
            'bg_color': qr_data.get('bg_color', 'ffffff'),
            'platform': qr_data.get('platform', 'medium'),
            'box_size': qr_data.get('box_size'),
            'border': qr_data.get('border'),
            'created_at': datetime.utcnow(),
            'is_favorite': False
        }
        
        result = db.qr_history.insert_one(history_entry)
        return str(result.inserted_id)
    
    @staticmethod
    def get_user_history(user_id: str, limit: int = 50, skip: int = 0) -> List[Dict[str, Any]]:
        """
        Get user's QR code history with pagination
        
        Args:
            user_id: User ID
            limit: Max number of records to return
            skip: Number of records to skip (for pagination)
        
        Returns:
            List of history entries
        """
        history = db.qr_history.find(
            {'user_id': user_id}
        ).sort('created_at', -1).skip(skip).limit(limit)
        
        result = []
        for entry in history:
            entry['id'] = str(entry['_id'])
            entry['_id'] = str(entry['_id'])
            result.append(entry)
        
        return result
    
    @staticmethod
    def get_history_count(user_id: str) -> int:
        """Get total count of user's QR history"""
        return db.qr_history.count_documents({'user_id': user_id})
    
    @staticmethod
    def get_history_entry(history_id: str, user_id: str) -> Dict[str, Any]:
        """
        Get a specific history entry (with ownership verification)
        
        Args:
            history_id: History entry ID
            user_id: User ID (for ownership verification)
        
        Returns:
            History entry or None
        """
        entry = db.qr_history.find_one({
            '_id': ObjectId(history_id),
            'user_id': user_id  # Verify ownership
        })
        
        if entry:
            entry['id'] = str(entry['_id'])
            entry['_id'] = str(entry['_id'])
        
        return entry
    
    @staticmethod
    def delete_history_entry(history_id: str, user_id: str) -> bool:
        """
        Delete a history entry (with ownership verification)
        
        Args:
            history_id: History entry ID
            user_id: User ID (for ownership verification)
        
        Returns:
            True if deleted, False otherwise
        """
        result = db.qr_history.delete_one({
            '_id': ObjectId(history_id),
            'user_id': user_id  # Verify ownership
        })
        
        return result.deleted_count > 0
    
    @staticmethod
    def toggle_favorite(history_id: str, user_id: str) -> bool:
        """
        Toggle favorite status of a history entry
        
        Args:
            history_id: History entry ID
            user_id: User ID (for ownership verification)
        
        Returns:
            New favorite status
        """
        entry = QRHistory.get_history_entry(history_id, user_id)
        if not entry:
            return False
        
        new_status = not entry.get('is_favorite', False)
        
        db.qr_history.update_one(
            {
                '_id': ObjectId(history_id),
                'user_id': user_id
            },
            {'$set': {'is_favorite': new_status}}
        )
        
        return new_status
    
    @staticmethod
    def get_favorites(user_id: str) -> List[Dict[str, Any]]:
        """Get user's favorite QR codes"""
        favorites = db.qr_history.find({
            'user_id': user_id,
            'is_favorite': True
        }).sort('created_at', -1)
        
        result = []
        for entry in favorites:
            entry['id'] = str(entry['_id'])
            entry['_id'] = str(entry['_id'])
            result.append(entry)
        
        return result
    
    @staticmethod
    def clear_user_history(user_id: str) -> int:
        """
        Clear all history for a user
        
        Returns:
            Number of entries deleted
        """
        result = db.qr_history.delete_many({'user_id': user_id})
        return result.deleted_count
