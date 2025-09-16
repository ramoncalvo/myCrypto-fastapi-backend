from abc import ABC, abstractmethod
from typing import Optional
from domain.entities.auth_user import AuthUser
from domain.value_objects.user_id import UserId
from domain.value_objects.email import Email


class AuthRepository(ABC):
    """Repository interface for authentication operations"""
    
    @abstractmethod
    async def create_user(self, user: AuthUser) -> AuthUser:
        """Create a new user"""
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: UserId) -> Optional[AuthUser]:
        """Get user by ID"""
        pass
    
    @abstractmethod
    async def get_by_email(self, email: Email) -> Optional[AuthUser]:
        """Get user by email"""
        pass
    
    @abstractmethod
    async def update_user(self, user: AuthUser) -> AuthUser:
        """Update existing user"""
        pass
    
    @abstractmethod
    async def email_exists(self, email: Email) -> bool:
        """Check if email already exists"""
        pass
