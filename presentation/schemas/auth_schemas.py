from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from application.dtos.auth_dtos import AuthUserResponse, TokenResponse


class RegisterSchema(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    name: str
    password: str


class LoginSchema(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class AuthUserResponseSchema(BaseModel):
    """Schema for authenticated user response"""
    id: str
    email: str
    name: str
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    @classmethod
    def from_dto(cls, dto: AuthUserResponse) -> 'AuthUserResponseSchema':
        """Create schema from DTO"""
        return cls(
            id=dto.id,
            email=dto.email,
            name=dto.name,
            is_verified=dto.is_verified,
            created_at=dto.created_at,
            last_login=dto.last_login
        )
    
    class Config:
        from_attributes = True


class TokenResponseSchema(BaseModel):
    """Schema for token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    
    @classmethod
    def from_dto(cls, dto: TokenResponse) -> 'TokenResponseSchema':
        """Create schema from DTO"""
        return cls(
            access_token=dto.access_token,
            refresh_token=dto.refresh_token,
            token_type=dto.token_type,
            expires_in=dto.expires_in
        )


class RefreshTokenSchema(BaseModel):
    """Schema for refresh token request"""
    refresh_token: str


class UpdateProfileSchema(BaseModel):
    """Schema for profile update"""
    name: Optional[str] = None


class ChangePasswordSchema(BaseModel):
    """Schema for password change"""
    current_password: str
    new_password: str
