from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from datetime import timedelta
from config import settings
from auth.repository import AuthRepository
from auth.utils import create_access_token, create_refresh_token, verify_token
from auth.dependencies import get_current_user, security
from models import LoginRequest, RegisterRequest, TokenResponse, RefreshTokenRequest, UserProfile, UserResponse
from database import db_factory

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Initialize auth repository
def get_auth_repository() -> AuthRepository:
    return AuthRepository(db_factory.database)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    register_data: RegisterRequest,
    auth_repo: AuthRepository = Depends(get_auth_repository)
):
    """Register a new user"""
    try:
        user = await auth_repo.register_user(register_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user"
        )

@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    auth_repo: AuthRepository = Depends(get_auth_repository)
):
    """Authenticate user and return JWT tokens"""
    # Authenticate user
    user = await auth_repo.authenticate_user(login_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create tokens
    access_token_expires = timedelta(minutes=settings.jwt_access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email},
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.jwt_access_token_expire_minutes * 60
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    auth_repo: AuthRepository = Depends(get_auth_repository)
):
    """Refresh access token using refresh token"""
    try:
        # Verify refresh token
        payload = verify_token(refresh_data.refresh_token, token_type="refresh")
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user to ensure they still exist
        user = await auth_repo.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Create new access token
        access_token_expires = timedelta(minutes=settings.jwt_access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user.id, "email": user.email},
            expires_delta=access_token_expires
        )
        
        # Create new refresh token
        new_refresh_token = create_refresh_token(data={"sub": user.id})
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.jwt_access_token_expire_minutes * 60
        )
    
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not refresh token"
        )

@router.get("/profile", response_model=UserProfile)
async def get_profile(current_user: UserProfile = Depends(get_current_user)):
    """Get current user profile"""
    return current_user

@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Logout user (client should discard tokens)"""
    # In a production environment, you might want to:
    # 1. Add token to a blacklist
    # 2. Store revoked tokens in Redis/database
    # 3. Use shorter token expiration times
    
    return {"message": "Successfully logged out"}

@router.get("/verify")
async def verify_token_endpoint(current_user: UserProfile = Depends(get_current_user)):
    """Verify if current token is valid"""
    return {"valid": True, "user": current_user}
