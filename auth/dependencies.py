from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from auth.utils import get_user_id_from_token
from database import db_factory
from models import UserProfile

# JWT Bearer token scheme
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserProfile:
    """Get current authenticated user from JWT token"""
    try:
        # Extract user ID from token
        user_id = get_user_id_from_token(credentials.credentials)
        
        # Get user from database
        user = await db_factory.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Convert to UserProfile
        return UserProfile(
            id=user.id,
            email=user.email,
            name=user.name,
            created_at=user.created_at
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> Optional[UserProfile]:
    """Get current user if token is provided, otherwise return None"""
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None
