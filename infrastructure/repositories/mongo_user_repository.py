from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime

from application.interfaces.repositories import IUserRepository
from domain.entities.user import User
from domain.value_objects.user_id import UserId
from domain.value_objects.email import Email


class MongoUserRepository(IUserRepository):
    """MongoDB implementation of user repository"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database.users
    
    async def create(self, user: User) -> User:
        """Create a new user"""
        user_doc = self._to_document(user)
        result = await self.collection.insert_one(user_doc)
        user_doc["_id"] = result.inserted_id
        return self._to_entity(user_doc)
    
    async def get_by_id(self, user_id: UserId) -> Optional[User]:
        """Get user by ID"""
        try:
            user_doc = await self.collection.find_one({"_id": ObjectId(str(user_id))})
            return self._to_entity(user_doc) if user_doc else None
        except Exception:
            return None
    
    async def get_by_email(self, email: Email) -> Optional[User]:
        """Get user by email"""
        user_doc = await self.collection.find_one({"email": str(email)})
        return self._to_entity(user_doc) if user_doc else None
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination"""
        cursor = self.collection.find().skip(skip).limit(limit)
        user_docs = await cursor.to_list(length=limit)
        return [self._to_entity(doc) for doc in user_docs]
    
    async def update(self, user: User) -> User:
        """Update user"""
        user_doc = self._to_document(user)
        user_doc.pop("_id", None)  # Remove _id from update data
        
        await self.collection.update_one(
            {"_id": ObjectId(str(user.id))},
            {"$set": user_doc}
        )
        return user
    
    async def delete(self, user_id: UserId) -> bool:
        """Delete user"""
        result = await self.collection.delete_one({"_id": ObjectId(str(user_id))})
        return result.deleted_count > 0
    
    def _to_document(self, user: User) -> Dict[str, Any]:
        """Convert domain entity to MongoDB document"""
        return {
            "_id": ObjectId(str(user.id)),
            "email": str(user.email),
            "name": user.name,
            "password_hash": user.password_hash,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }
    
    def _to_entity(self, user_doc: Dict[str, Any]) -> User:
        """Convert MongoDB document to domain entity"""
        return User(
            id=UserId(str(user_doc["_id"])),
            email=Email(user_doc["email"]),
            name=user_doc["name"],
            password_hash=user_doc.get("password_hash", ""),  # Handle missing password_hash
            created_at=user_doc["created_at"],
            updated_at=user_doc.get("updated_at")
        )
