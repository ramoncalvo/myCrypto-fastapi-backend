from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from application.interfaces.auth_repository import AuthRepository
from domain.entities.auth_user import AuthUser
from domain.value_objects.user_id import UserId
from domain.value_objects.email import Email


class MongoAuthRepository(AuthRepository):
    """MongoDB implementation of AuthRepository"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database.users
    
    async def create_user(self, user: AuthUser) -> AuthUser:
        """Create a new user"""
        user_doc = self._to_document(user)
        result = await self.collection.insert_one(user_doc)
        
        # Update user with generated MongoDB ID
        created_doc = await self.collection.find_one({"_id": result.inserted_id})
        return self._to_entity(created_doc)
    
    async def get_by_id(self, user_id: UserId) -> Optional[AuthUser]:
        """Get user by ID"""
        try:
            doc = await self.collection.find_one({"_id": ObjectId(str(user_id))})
            return self._to_entity(doc) if doc else None
        except Exception:
            return None
    
    async def get_by_email(self, email: Email) -> Optional[AuthUser]:
        """Get user by email"""
        doc = await self.collection.find_one({"email": str(email)})
        return self._to_entity(doc) if doc else None
    
    async def update_user(self, user: AuthUser) -> AuthUser:
        """Update existing user"""
        user_doc = self._to_document(user)
        user_doc.pop("_id", None)  # Remove _id for update
        
        await self.collection.update_one(
            {"_id": ObjectId(str(user.id))},
            {"$set": user_doc}
        )
        
        # Return updated user
        updated_doc = await self.collection.find_one({"_id": ObjectId(str(user.id))})
        return self._to_entity(updated_doc)
    
    async def email_exists(self, email: Email) -> bool:
        """Check if email already exists"""
        doc = await self.collection.find_one({"email": str(email)})
        return doc is not None
    
    def _to_document(self, user: AuthUser) -> dict:
        """Convert domain entity to MongoDB document"""
        doc = {
            "email": str(user.email),
            "name": user.name,
            "password_hash": user.password_hash,
            "created_at": user.created_at,
            "updated_at": user.updated_at or user.created_at,  # Use created_at if updated_at is None
            "is_verified": user.is_verified,
            "failed_login_attempts": user.failed_login_attempts,
        }
        
        # Only add optional fields if they have values
        if user.last_login:
            doc["last_login"] = user.last_login
        if user.locked_until:
            doc["locked_until"] = user.locked_until
        
        # Only add _id if user has an existing MongoDB ObjectId
        if hasattr(user, '_mongo_id') and user._mongo_id:
            doc["_id"] = ObjectId(user._mongo_id)
        
        return doc
    
    def _to_entity(self, doc: dict) -> AuthUser:
        """Convert MongoDB document to domain entity"""
        entity = AuthUser(
            id=UserId(str(doc["_id"])),
            email=Email(doc["email"]),
            name=doc["name"],
            password_hash=doc["password_hash"],
            created_at=doc["created_at"],
            updated_at=doc.get("updated_at"),
            is_verified=doc.get("is_verified", False),
            last_login=doc.get("last_login"),
            failed_login_attempts=doc.get("failed_login_attempts", 0),
            locked_until=doc.get("locked_until")
        )
        # Store MongoDB ObjectId for future updates
        entity._mongo_id = str(doc["_id"])
        return entity
