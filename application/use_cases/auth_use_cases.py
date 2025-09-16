from typing import Optional
from datetime import datetime, timedelta
from application.interfaces.auth_repository import AuthRepository
from application.dtos.auth_dtos import (
    RegisterUserRequest, LoginRequest, AuthUserResponse, 
    UpdateProfileRequest, ChangePasswordRequest
)
from domain.entities.auth_user import AuthUser
from domain.value_objects.email import Email
from domain.value_objects.user_id import UserId
from domain.value_objects.password import Password


class AuthUseCases:
    """Authentication use cases"""
    
    def __init__(self, auth_repository: AuthRepository):
        self._auth_repository = auth_repository
    
    async def register_user(self, request: RegisterUserRequest) -> AuthUserResponse:
        """Register a new user"""
        email = Email(request.email)
        
        # Check if user already exists
        if await self._auth_repository.email_exists(email):
            raise ValueError("User with this email already exists")
        
        # Create password with validation and hashing
        password = Password(request.password)
        
        # Create user entity
        user = AuthUser.create(
            email=request.email,
            name=request.name,
            password_hash=password.hash
        )
        
        # Save user
        created_user = await self._auth_repository.create_user(user)
        
        return AuthUserResponse.from_entity(created_user)
    
    async def authenticate_user(self, request: LoginRequest) -> Optional[AuthUserResponse]:
        """Authenticate user with email and password"""
        email = Email(request.email)
        
        # Get user by email
        user = await self._auth_repository.get_by_email(email)
        if not user:
            return None
        
        # Check if account is locked
        if user.is_account_locked():
            raise ValueError("Account is temporarily locked due to multiple failed login attempts")
        
        # Verify password
        password = Password.from_hash(user.password_hash)
        if not password.verify(request.password):
            # Record failed login attempt
            user.record_failed_login()
            await self._auth_repository.update_user(user)
            return None
        
        # Record successful login
        user.record_successful_login()
        updated_user = await self._auth_repository.update_user(user)
        
        return AuthUserResponse.from_entity(updated_user)
    
    async def get_user_by_id(self, user_id: str) -> Optional[AuthUserResponse]:
        """Get user by ID"""
        try:
            user_id_obj = UserId(user_id)
            user = await self._auth_repository.get_by_id(user_id_obj)
            
            if not user:
                return None
            
            return AuthUserResponse.from_entity(user)
        except ValueError:
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[AuthUserResponse]:
        """Get user by email"""
        try:
            email_obj = Email(email)
            user = await self._auth_repository.get_by_email(email_obj)
            
            if not user:
                return None
            
            return AuthUserResponse.from_entity(user)
        except ValueError:
            return None
    
    async def update_profile(self, user_id: str, request: UpdateProfileRequest) -> AuthUserResponse:
        """Update user profile"""
        user_id_obj = UserId(user_id)
        user = await self._auth_repository.get_by_id(user_id_obj)
        
        if not user:
            raise ValueError("User not found")
        
        # Update profile
        user.update_profile(name=request.name)
        
        # Save changes
        updated_user = await self._auth_repository.update_user(user)
        
        return AuthUserResponse.from_entity(updated_user)
    
    async def change_password(self, user_id: str, request: ChangePasswordRequest) -> AuthUserResponse:
        """Change user password"""
        user_id_obj = UserId(user_id)
        user = await self._auth_repository.get_by_id(user_id_obj)
        
        if not user:
            raise ValueError("User not found")
        
        # Verify current password
        current_password = Password.from_hash(user.password_hash)
        if not current_password.verify(request.current_password):
            raise ValueError("Current password is incorrect")
        
        # Create new password with validation
        new_password = Password(request.new_password)
        
        # Update password hash
        user.password_hash = new_password.hash
        user.updated_at = datetime.utcnow()
        
        # Save changes
        updated_user = await self._auth_repository.update_user(user)
        
        return AuthUserResponse.from_entity(updated_user)
    
    async def verify_account(self, user_id: str) -> AuthUserResponse:
        """Verify user account"""
        user_id_obj = UserId(user_id)
        user = await self._auth_repository.get_by_id(user_id_obj)
        
        if not user:
            raise ValueError("User not found")
        
        # Verify account
        user.verify_account()
        
        # Save changes
        updated_user = await self._auth_repository.update_user(user)
        
        return AuthUserResponse.from_entity(updated_user)
    
    async def unlock_account(self, user_id: str) -> AuthUserResponse:
        """Unlock user account"""
        user_id_obj = UserId(user_id)
        user = await self._auth_repository.get_by_id(user_id_obj)
        
        if not user:
            raise ValueError("User not found")
        
        # Unlock account
        user.unlock_account()
        
        # Save changes
        updated_user = await self._auth_repository.update_user(user)
        
        return AuthUserResponse.from_entity(updated_user)
