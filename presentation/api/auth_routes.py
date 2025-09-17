from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from datetime import timedelta
from config import settings
from application.use_cases.auth_use_cases import AuthUseCases
from application.dtos.auth_dtos import (
    RegisterUserRequest, LoginRequest, RefreshTokenRequest,
    UpdateProfileRequest, ChangePasswordRequest, TokenResponse
)
from presentation.schemas.auth_schemas import (
    RegisterSchema, LoginSchema, AuthUserResponseSchema, 
    TokenResponseSchema, RefreshTokenSchema, UpdateProfileSchema,
    ChangePasswordSchema
)
from infrastructure.services.jwt_service import JWTService
import jwt

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


def get_auth_use_cases() -> AuthUseCases:
    """Dependency to get auth use cases"""
    from database import db_factory
    from infrastructure.dependency_injection.container import DIContainer
    container = DIContainer(db_factory.database)
    return container.auth_use_cases


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_use_cases: AuthUseCases = Depends(get_auth_use_cases)
) -> AuthUserResponseSchema:
    """Get current authenticated user"""
    try:
        # Verify access token
        payload = JWTService.verify_token(credentials.credentials, "access")
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Get user
        user = await auth_use_cases.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return AuthUserResponseSchema.from_dto(user)
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


@router.post("/register", response_model=AuthUserResponseSchema, status_code=status.HTTP_201_CREATED)
async def register(
    register_data: RegisterSchema,
    auth_use_cases: AuthUseCases = Depends(get_auth_use_cases)
):
    """Register a new user"""
    try:
        request = RegisterUserRequest(
            email=register_data.email,
            name=register_data.name,
            password=register_data.password
        )
        
        user = await auth_use_cases.register_user(request)
        return AuthUserResponseSchema.from_dto(user)
        
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


@router.post("/login", response_model=TokenResponseSchema)
async def login(
    login_data: LoginSchema,
    auth_use_cases: AuthUseCases = Depends(get_auth_use_cases)
):
    """Authenticate user and return JWT tokens"""
    try:
        request = LoginRequest(
            email=login_data.email,
            password=login_data.password
        )
        
        # Authenticate user
        user = await auth_use_cases.authenticate_user(request)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Create tokens
        access_token_expires = timedelta(minutes=settings.jwt_access_token_expire_minutes)
        access_token = JWTService.create_access_token(
            data={"sub": user.id, "email": user.email},
            expires_delta=access_token_expires
        )
        refresh_token = JWTService.create_refresh_token(data={"sub": user.id})
        
        token_response = TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.jwt_access_token_expire_minutes * 60
        )
        
        return TokenResponseSchema.from_dto(token_response)
        
    except ValueError as e:
        # Handle account locked or validation errors
        if "locked" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        # Re-raise HTTP exceptions (like 401 Unauthorized)
        raise
    except Exception as e:
        # Log unexpected errors but don't expose internal details
        print(f"Unexpected login error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred during authentication"
        )


@router.post("/refresh", response_model=TokenResponseSchema)
async def refresh_token(
    refresh_data: RefreshTokenSchema,
    auth_use_cases: AuthUseCases = Depends(get_auth_use_cases)
):
    """Refresh access token using refresh token"""
    try:
        # Verify refresh token
        payload = JWTService.verify_token(refresh_data.refresh_token, "refresh")
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user to ensure they still exist
        user = await auth_use_cases.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Create new tokens
        access_token_expires = timedelta(minutes=settings.jwt_access_token_expire_minutes)
        access_token = JWTService.create_access_token(
            data={"sub": user.id, "email": user.email},
            expires_delta=access_token_expires
        )
        new_refresh_token = JWTService.create_refresh_token(data={"sub": user.id})
        
        token_response = TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.jwt_access_token_expire_minutes * 60
        )
        
        return TokenResponseSchema.from_dto(token_response)
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not refresh token"
        )


@router.get("/profile", response_model=AuthUserResponseSchema)
async def get_profile(current_user: AuthUserResponseSchema = Depends(get_current_user)):
    """Get current user profile"""
    return current_user


@router.put("/profile", response_model=AuthUserResponseSchema)
async def update_profile(
    profile_data: UpdateProfileSchema,
    current_user: AuthUserResponseSchema = Depends(get_current_user),
    auth_use_cases: AuthUseCases = Depends(get_auth_use_cases)
):
    """Update user profile"""
    try:
        request = UpdateProfileRequest(name=profile_data.name)
        
        updated_user = await auth_use_cases.update_profile(current_user.id, request)
        return AuthUserResponseSchema.from_dto(updated_user)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )


@router.put("/change-password", response_model=AuthUserResponseSchema)
async def change_password(
    password_data: ChangePasswordSchema,
    current_user: AuthUserResponseSchema = Depends(get_current_user),
    auth_use_cases: AuthUseCases = Depends(get_auth_use_cases)
):
    """Change user password"""
    try:
        request = ChangePasswordRequest(
            current_password=password_data.current_password,
            new_password=password_data.new_password
        )
        
        updated_user = await auth_use_cases.change_password(current_user.id, request)
        return AuthUserResponseSchema.from_dto(updated_user)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password"
        )


@router.post("/verify/{user_id}", response_model=AuthUserResponseSchema)
async def verify_account(
    user_id: str,
    auth_use_cases: AuthUseCases = Depends(get_auth_use_cases)
):
    """Verify user account (admin endpoint)"""
    try:
        verified_user = await auth_use_cases.verify_account(user_id)
        return AuthUserResponseSchema.from_dto(verified_user)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify account"
        )


@router.post("/unlock/{user_id}", response_model=AuthUserResponseSchema)
async def unlock_account(
    user_id: str,
    auth_use_cases: AuthUseCases = Depends(get_auth_use_cases)
):
    """Unlock user account (admin endpoint)"""
    try:
        unlocked_user = await auth_use_cases.unlock_account(user_id)
        return AuthUserResponseSchema.from_dto(unlocked_user)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unlock account"
        )


@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Logout user (client should discard tokens)"""
    # In a production environment, you might want to:
    # 1. Add token to a blacklist
    # 2. Store revoked tokens in Redis/database
    # 3. Use shorter token expiration times
    
    return {"message": "Successfully logged out"}


@router.get("/verify")
async def verify_token_endpoint(current_user: AuthUserResponseSchema = Depends(get_current_user)):
    """Verify if current token is valid"""
    return {"valid": True, "user": current_user}
