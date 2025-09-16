from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from application.dtos.user_dtos import UserResponse


class UserCreateSchema(BaseModel):
    """Schema for creating a new user"""
    email: EmailStr
    name: str
    password: str


class UserUpdateSchema(BaseModel):
    """Schema for updating user information"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class UserResponseSchema(BaseModel):
    """Schema for user response"""
    id: str
    email: str
    name: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @classmethod
    def from_dto(cls, dto: UserResponse) -> 'UserResponseSchema':
        """Create schema from DTO"""
        return cls(
            id=dto.id,
            email=dto.email,
            name=dto.name,
            created_at=dto.created_at,
            updated_at=dto.updated_at
        )
    
    class Config:
        from_attributes = True
