from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from auth.utils import get_password_hash, verify_password
from models import RegisterRequest, LoginRequest, UserProfile, UserResponse

class AuthRepository:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database.users
    
    async def register_user(self, register_data: RegisterRequest) -> UserResponse:
        """Register a new user"""
        # Check if user already exists
        existing_user = await self.collection.find_one({"email": register_data.email})
        if existing_user:
            raise ValueError("User with this email already exists")
        
        # Hash password
        hashed_password = get_password_hash(register_data.password)
        
        # Create user document
        user_doc = {
            "email": register_data.email,
            "name": register_data.name,
            "password": hashed_password,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Insert user
        result = await self.collection.insert_one(user_doc)
        
        # Get created user
        created_user = await self.collection.find_one({"_id": result.inserted_id})
        
        return UserResponse(
            id=str(created_user["_id"]),
            email=created_user["email"],
            name=created_user["name"],
            created_at=created_user["created_at"]
        )
    
    async def authenticate_user(self, login_data: LoginRequest) -> Optional[UserProfile]:
        """Authenticate user with email and password"""
        # Find user by email
        user = await self.collection.find_one({"email": login_data.email})
        if not user:
            return None
        
        # Verify password
        if not verify_password(login_data.password, user["password"]):
            return None
        
        # Return user profile
        return UserProfile(
            id=str(user["_id"]),
            email=user["email"],
            name=user["name"],
            created_at=user["created_at"]
        )
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserProfile]:
        """Get user by ID"""
        try:
            user = await self.collection.find_one({"_id": ObjectId(user_id)})
            if not user:
                return None
            
            return UserProfile(
                id=str(user["_id"]),
                email=user["email"],
                name=user["name"],
                created_at=user["created_at"]
            )
        except Exception:
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[UserProfile]:
        """Get user by email"""
        user = await self.collection.find_one({"email": email})
        if not user:
            return None
        
        return UserProfile(
            id=str(user["_id"]),
            email=user["email"],
            name=user["name"],
            created_at=user["created_at"]
        )
