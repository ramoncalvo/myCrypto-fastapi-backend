from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from application.use_cases.user_use_cases import UserUseCases
from application.dtos.user_dtos import CreateUserRequest, UpdateUserRequest, UserResponse
from presentation.dependencies import get_user_use_cases
from presentation.schemas.user_schemas import (
    UserCreateSchema, UserUpdateSchema, UserResponseSchema
)
import hashlib


router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreateSchema,
    user_use_cases: UserUseCases = Depends(get_user_use_cases)
):
    """Create a new user"""
    try:
        # Hash password (in production, use proper password hashing like bcrypt)
        password_hash = hashlib.sha256(user_data.password.encode()).hexdigest()
        
        request = CreateUserRequest(
            email=user_data.email,
            name=user_data.name,
            password_hash=password_hash
        )
        
        user_response = await user_use_cases.create_user(request)
        return UserResponseSchema.from_dto(user_response)
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create user")


@router.get("/", response_model=List[UserResponseSchema])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    user_use_cases: UserUseCases = Depends(get_user_use_cases)
):
    """Get all users with pagination"""
    try:
        users = await user_use_cases.get_all_users(skip=skip, limit=limit)
        return [UserResponseSchema.from_dto(user) for user in users]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve users")


@router.get("/{user_id}", response_model=UserResponseSchema)
async def get_user(
    user_id: str,
    user_use_cases: UserUseCases = Depends(get_user_use_cases)
):
    """Get user by ID"""
    try:
        user = await user_use_cases.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return UserResponseSchema.from_dto(user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve user")


@router.get("/email/{email}", response_model=UserResponseSchema)
async def get_user_by_email(
    email: str,
    user_use_cases: UserUseCases = Depends(get_user_use_cases)
):
    """Get user by email"""
    try:
        user = await user_use_cases.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return UserResponseSchema.from_dto(user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve user")


@router.put("/{user_id}", response_model=UserResponseSchema)
async def update_user(
    user_id: str,
    user_data: UserUpdateSchema,
    user_use_cases: UserUseCases = Depends(get_user_use_cases)
):
    """Update user"""
    try:
        password_hash = None
        if user_data.password:
            password_hash = hashlib.sha256(user_data.password.encode()).hexdigest()
        
        request = UpdateUserRequest(
            name=user_data.name,
            email=user_data.email,
            password_hash=password_hash
        )
        
        user = await user_use_cases.update_user(user_id, request)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return UserResponseSchema.from_dto(user)
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update user")


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    user_use_cases: UserUseCases = Depends(get_user_use_cases)
):
    """Delete user"""
    try:
        success = await user_use_cases.delete_user(user_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return {"message": "User deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete user")
