from typing import Optional
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1 import AsyncClient
from datetime import datetime

from application.interfaces.auth_repository import AuthRepository
from domain.entities.auth_user import AuthUser
from domain.value_objects.email import Email
from domain.value_objects.user_id import UserId


class FirebaseAuthRepository(AuthRepository):
    """Firebase implementation of AuthRepository"""
    
    def __init__(self, firestore_client: AsyncClient):
        self.db = firestore_client
        self.collection = "users"
    
    async def create_user(self, user: AuthUser) -> AuthUser:
        """Create a new user in Firebase"""
        user_data = {
            "id": str(user.id),
            "email": str(user.email),
            "name": user.name,
            "password_hash": user.password_hash,
            "is_verified": user.is_verified,
            "is_active": user.is_active,
            "failed_login_attempts": user.failed_login_attempts,
            "locked_until": user.locked_until,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "last_login": user.last_login
        }
        
        # Use user ID as document ID for easy retrieval
        doc_ref = self.db.collection(self.collection).document(str(user.id))
        await doc_ref.set(user_data)
        
        return user
    
    async def get_by_id(self, user_id: UserId) -> Optional[AuthUser]:
        """Get user by ID from Firebase"""
        doc_ref = self.db.collection(self.collection).document(str(user_id))
        doc = await doc_ref.get()
        
        if not doc.exists:
            return None
        
        data = doc.to_dict()
        return self._dict_to_auth_user(data)
    
    async def get_by_email(self, email: Email) -> Optional[AuthUser]:
        """Get user by email from Firebase"""
        query = self.db.collection(self.collection).where("email", "==", str(email)).limit(1)
        docs = await query.get()
        
        if not docs:
            return None
        
        data = docs[0].to_dict()
        return self._dict_to_auth_user(data)
    
    async def update_user(self, user: AuthUser) -> AuthUser:
        """Update user in Firebase"""
        user_data = {
            "name": user.name,
            "password_hash": user.password_hash,
            "is_verified": user.is_verified,
            "is_active": user.is_active,
            "failed_login_attempts": user.failed_login_attempts,
            "locked_until": user.locked_until,
            "updated_at": datetime.utcnow(),
            "last_login": user.last_login
        }
        
        doc_ref = self.db.collection(self.collection).document(str(user.id))
        await doc_ref.update(user_data)
        
        # Update the user object
        user.updated_at = user_data["updated_at"]
        return user
    
    async def delete_user(self, user_id: UserId) -> bool:
        """Delete user from Firebase"""
        doc_ref = self.db.collection(self.collection).document(str(user_id))
        await doc_ref.delete()
        return True
    
    async def email_exists(self, email: Email) -> bool:
        """Check if email exists in Firebase"""
        query = self.db.collection(self.collection).where("email", "==", str(email)).limit(1)
        docs = await query.get()
        return len(docs) > 0
    
    def _dict_to_auth_user(self, data: dict) -> AuthUser:
        """Convert Firebase document to AuthUser entity"""
        return AuthUser(
            id=UserId(data["id"]),
            email=Email(data["email"]),
            name=data["name"],
            password_hash=data["password_hash"],
            is_verified=data.get("is_verified", False),
            is_active=data.get("is_active", True),
            failed_login_attempts=data.get("failed_login_attempts", 0),
            locked_until=data.get("locked_until"),
            created_at=data["created_at"],
            updated_at=data.get("updated_at"),
            last_login=data.get("last_login")
        )
