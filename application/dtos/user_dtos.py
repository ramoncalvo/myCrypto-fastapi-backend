from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from domain.entities.user import User


@dataclass
class CreateUserRequest:
    """DTO for creating a new user"""
    email: str
    name: str
    password_hash: str


@dataclass
class UpdateUserRequest:
    """DTO for updating user information"""
    name: Optional[str] = None
    email: Optional[str] = None
    password_hash: Optional[str] = None


@dataclass
class UserResponse:
    """DTO for user response"""
    id: str
    email: str
    name: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @classmethod
    def from_entity(cls, user: User) -> 'UserResponse':
        """Create DTO from domain entity"""
        return cls(
            id=str(user.id),
            email=str(user.email),
            name=user.name,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
