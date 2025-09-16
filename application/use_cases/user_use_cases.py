from typing import List, Optional
from application.interfaces.repositories import IUserRepository
from domain.entities.user import User
from domain.value_objects.user_id import UserId
from domain.value_objects.email import Email
from application.dtos.user_dtos import CreateUserRequest, UpdateUserRequest, UserResponse


class UserUseCases:
    """Use cases for user management"""
    
    def __init__(self, user_repository: IUserRepository):
        self._user_repository = user_repository
    
    async def create_user(self, request: CreateUserRequest) -> UserResponse:
        """Create a new user"""
        # Check if user with email already exists
        existing_user = await self._user_repository.get_by_email(Email(request.email))
        if existing_user:
            raise ValueError(f"User with email {request.email} already exists")
        
        # Create domain entity
        user = User.create(
            email=request.email,
            name=request.name,
            password_hash=request.password_hash
        )
        
        # Save to repository
        created_user = await self._user_repository.create(user)
        
        # Return DTO
        return UserResponse.from_entity(created_user)
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        """Get user by ID"""
        user = await self._user_repository.get_by_id(UserId(user_id))
        return UserResponse.from_entity(user) if user else None
    
    async def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """Get user by email"""
        user = await self._user_repository.get_by_email(Email(email))
        return UserResponse.from_entity(user) if user else None
    
    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        """Get all users with pagination"""
        users = await self._user_repository.get_all(skip=skip, limit=limit)
        return [UserResponse.from_entity(user) for user in users]
    
    async def update_user(self, user_id: str, request: UpdateUserRequest) -> Optional[UserResponse]:
        """Update user"""
        user = await self._user_repository.get_by_id(UserId(user_id))
        if not user:
            return None
        
        # Update domain entity
        if request.name or request.email:
            user.update_profile(name=request.name, email=request.email)
        
        if request.password_hash:
            user.change_password(request.password_hash)
        
        # Save to repository
        updated_user = await self._user_repository.update(user)
        
        # Return DTO
        return UserResponse.from_entity(updated_user)
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete user"""
        return await self._user_repository.delete(UserId(user_id))
