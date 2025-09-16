from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import List, Optional
from datetime import datetime
from application.use_cases.transaction_use_cases import TransactionUseCases
from application.dtos.transaction_dtos import (
    CreateTransactionRequest, UpdateTransactionRequest, ExecuteTransactionRequest,
    CancelTransactionRequest, TransactionFilterRequest
)
from presentation.schemas.transaction_schemas import (
    CreateTransactionSchema, UpdateTransactionSchema, ExecuteTransactionSchema,
    CancelTransactionSchema, TransactionResponseSchema, TransactionStatsResponseSchema,
    TransactionFilterSchema, TransactionTypeEnum, TransactionStatusEnum
)
from presentation.api.auth_routes import get_current_user
from presentation.schemas.auth_schemas import AuthUserResponseSchema


router = APIRouter(prefix="/transactions", tags=["Transactions"])
security = HTTPBearer()


def get_transaction_use_cases() -> TransactionUseCases:
    """Dependency to get transaction use cases"""
    from database import db_factory
    from infrastructure.dependency_injection.container import DIContainer
    container = DIContainer(db_factory.database)
    return container.transaction_use_cases


@router.post("/buy", response_model=TransactionResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_buy_transaction(
    transaction_data: CreateTransactionSchema,
    current_user: AuthUserResponseSchema = Depends(get_current_user),
    transaction_use_cases: TransactionUseCases = Depends(get_transaction_use_cases)
):
    """Create a buy transaction"""
    try:
        # Force transaction type to buy
        transaction_data.transaction_type = "buy"
        
        request = CreateTransactionRequest(
            portfolio_id=transaction_data.portfolio_id,
            asset_id=transaction_data.asset_id,
            transaction_type=transaction_data.transaction_type,
            quantity=transaction_data.quantity,
            price=transaction_data.price,
            fees=transaction_data.fees,
            notes=transaction_data.notes
        )
        
        transaction = await transaction_use_cases.create_buy_transaction(current_user.id, request)
        return transaction
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create buy transaction"
        )


@router.post("/sell", response_model=TransactionResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_sell_transaction(
    transaction_data: CreateTransactionSchema,
    # current_user: AuthUserResponseSchema = Depends(get_current_user),
    transaction_use_cases: TransactionUseCases = Depends(get_transaction_use_cases)
):
    """Create a sell transaction"""
    try:
        # Force transaction type to sell
        transaction_data.transaction_type = "sell"
        
        request = CreateTransactionRequest(
            portfolio_id=transaction_data.portfolio_id,
            asset_id=transaction_data.asset_id,
            transaction_type=transaction_data.transaction_type,
            quantity=transaction_data.quantity,
            price=transaction_data.price,
            fees=transaction_data.fees,
            notes=transaction_data.notes
        )
        
        # Use a test user ID for now
        test_user_id = "test-user-123"
        transaction = await transaction_use_cases.create_sell_transaction(test_user_id, request)
        return transaction
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create sell transaction"
        )


@router.post("/execute", response_model=TransactionResponseSchema)
async def execute_transaction(
    execute_data: ExecuteTransactionSchema,
    current_user: AuthUserResponseSchema = Depends(get_current_user),
    transaction_use_cases: TransactionUseCases = Depends(get_transaction_use_cases)
):
    """Execute a pending transaction"""
    try:
        request = ExecuteTransactionRequest(transaction_id=execute_data.transaction_id)
        transaction = await transaction_use_cases.execute_transaction(current_user.id, request)
        return transaction
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to execute transaction"
        )


@router.post("/cancel", response_model=TransactionResponseSchema)
async def cancel_transaction(
    cancel_data: CancelTransactionSchema,
    # current_user: AuthUserResponseSchema = Depends(get_current_user),
    transaction_use_cases: TransactionUseCases = Depends(get_transaction_use_cases)
):
    """Cancel a pending transaction"""
    try:
        request = CancelTransactionRequest(
            transaction_id=cancel_data.transaction_id,
            reason=cancel_data.reason
        )
        # Use a test user ID for now
        test_user_id = "test-user-123"
        transaction = await transaction_use_cases.cancel_transaction(test_user_id, request)
        return transaction
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel transaction"
        )


@router.get("/{transaction_id}", response_model=TransactionResponseSchema)
async def get_transaction(
    transaction_id: str,
    # current_user: AuthUserResponseSchema = Depends(get_current_user),
    transaction_use_cases: TransactionUseCases = Depends(get_transaction_use_cases)
):
    """Get transaction by ID"""
    try:
        # Use a test user ID for now
        test_user_id = "test-user-123"
        transaction = await transaction_use_cases.get_transaction_by_id(test_user_id, transaction_id)
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        return transaction
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve transaction"
        )


@router.put("/{transaction_id}", response_model=TransactionResponseSchema)
async def update_transaction(
    transaction_id: str,
    update_data: UpdateTransactionSchema,
    # current_user: AuthUserResponseSchema = Depends(get_current_user),
    transaction_use_cases: TransactionUseCases = Depends(get_transaction_use_cases)
):
    """Update a pending transaction"""
    try:
        request = UpdateTransactionRequest(
            quantity=update_data.quantity,
            price=update_data.price,
            fees=update_data.fees,
            notes=update_data.notes
        )
        
        # Use a test user ID for now
        test_user_id = "test-user-123"
        transaction = await transaction_use_cases.update_transaction(test_user_id, transaction_id, request)
        return transaction
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update transaction"
        )


@router.get("/", response_model=List[TransactionResponseSchema])
async def get_user_transactions(
    # current_user: AuthUserResponseSchema = Depends(get_current_user),
    transaction_use_cases: TransactionUseCases = Depends(get_transaction_use_cases),
    asset_id: Optional[str] = Query(None, description="Filter by asset ID"),
    transaction_type: Optional[TransactionTypeEnum] = Query(None, description="Filter by transaction type"),
    status_filter: Optional[TransactionStatusEnum] = Query(None, alias="status", description="Filter by status"),
    start_date: Optional[datetime] = Query(None, description="Start date for filtering"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return")
):
    """Get user transactions with optional filters"""
    try:
        filter_request = TransactionFilterRequest(
            asset_id=asset_id,
            transaction_type=transaction_type.value if transaction_type else None,
            status=status_filter.value if status_filter else None,
            start_date=start_date,
            end_date=end_date,
            skip=skip,
            limit=limit
        )
        
        # Use a test user ID for now
        test_user_id = "test-user-123"
        transactions = await transaction_use_cases.get_user_transactions(test_user_id, filter_request)
        return transactions
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve transactions"
        )


@router.get("/portfolio/{portfolio_id}", response_model=List[TransactionResponseSchema])
async def get_portfolio_transactions(
    portfolio_id: str,
    # current_user: AuthUserResponseSchema = Depends(get_current_user),
    transaction_use_cases: TransactionUseCases = Depends(get_transaction_use_cases),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return")
):
    """Get transactions for a specific portfolio"""
    try:
        # Use a test user ID for now
        test_user_id = "test-user-123"
        transactions = await transaction_use_cases.get_portfolio_transactions(
            test_user_id, 
            portfolio_id,
            skip,
            limit
        )
        return transactions
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve portfolio transactions"
        )


@router.get("/stats/summary", response_model=TransactionStatsResponseSchema)
async def get_transaction_stats(
    # current_user: AuthUserResponseSchema = Depends(get_current_user),
    transaction_use_cases: TransactionUseCases = Depends(get_transaction_use_cases)
):
    """Get transaction statistics for the current user"""
    try:
        # Use a test user ID for now
        test_user_id = "test-user-123"
        stats = await transaction_use_cases.get_user_transaction_stats(test_user_id)
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve transaction statistics"
        )
