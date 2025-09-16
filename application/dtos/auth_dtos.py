from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from domain.entities.auth_user import AuthUser


class RegisterUserRequest(BaseModel):
    """DTO for user registration request"""
    email: str
    name: str
    password: str


class LoginRequest(BaseModel):
    """DTO for login request"""
    email: str
    password: str


class AuthUserResponse(BaseModel):
    """DTO for authenticated user response"""
    id: str
    email: str
    name: str
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    @classmethod
    def from_entity(cls, user: AuthUser) -> 'AuthUserResponse':
        """Create response from domain entity"""
        return cls(
            id=str(user.id),
            email=str(user.email),
            name=user.name,
            is_verified=user.is_verified,
            created_at=user.created_at,
            last_login=user.last_login
        )


class TokenResponse(BaseModel):
    """DTO for token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    """DTO for refresh token request"""
    refresh_token: str


class UpdateProfileRequest(BaseModel):
    """DTO for profile update request"""
    name: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    """DTO for password change request"""
    current_password: str
    new_password: str
