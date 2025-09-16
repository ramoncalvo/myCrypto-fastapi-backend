from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import List, Optional
from application.use_cases.portfolio_aggregate_use_cases import PortfolioAggregateUseCases
from application.dtos.portfolio_aggregate_dtos import (
    CreatePortfolioRequest, UpdatePortfolioRequest, PortfolioFilterRequest
)
from presentation.schemas.portfolio_aggregate_schemas import (
    CreatePortfolioSchema, UpdatePortfolioSchema, PortfolioResponseSchema,
    PortfolioDetailResponseSchema, PortfolioPerformanceResponseSchema,
    PortfolioFilterSchema, PortfolioOverviewResponseSchema
)
from presentation.api.auth_routes import get_current_user
from presentation.schemas.auth_schemas import AuthUserResponseSchema


router = APIRouter(prefix="/portfolios", tags=["Portfolio Management"])
security = HTTPBearer()


def get_portfolio_aggregate_use_cases() -> PortfolioAggregateUseCases:
    """Dependency to get portfolio aggregate use cases"""
    from database import db_factory
    from infrastructure.dependency_injection.container import DIContainer
    container = DIContainer(db_factory.database)
    return container.portfolio_aggregate_use_cases


@router.post("/", response_model=PortfolioResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_portfolio(
    portfolio_data: CreatePortfolioSchema,
    current_user: AuthUserResponseSchema = Depends(get_current_user),
    portfolio_use_cases: PortfolioAggregateUseCases = Depends(get_portfolio_aggregate_use_cases)
):
    """Create a new portfolio"""
    try:
        request = CreatePortfolioRequest(
            name=portfolio_data.name,
            description=portfolio_data.description
        )
        
        portfolio = await portfolio_use_cases.create_portfolio(current_user.id, request)
        return portfolio
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create portfolio"
        )


@router.get("/", response_model=List[PortfolioResponseSchema])
async def get_user_portfolios(
    current_user: AuthUserResponseSchema = Depends(get_current_user),
    portfolio_use_cases: PortfolioAggregateUseCases = Depends(get_portfolio_aggregate_use_cases),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return")
):
    """Get user portfolios"""
    try:
        filter_request = PortfolioFilterRequest(skip=skip, limit=limit)
        portfolios = await portfolio_use_cases.get_user_portfolios(current_user.id, filter_request)
        return portfolios
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve portfolios"
        )


@router.get("/overview", response_model=PortfolioOverviewResponseSchema)
async def get_portfolio_overview(
    current_user: AuthUserResponseSchema = Depends(get_current_user),
    portfolio_use_cases: PortfolioAggregateUseCases = Depends(get_portfolio_aggregate_use_cases)
):
    """Get comprehensive portfolio overview for the user"""
    try:
        overview = await portfolio_use_cases.get_user_portfolio_overview(current_user.id)
        return overview
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve portfolio overview"
        )


@router.get("/{portfolio_id}", response_model=PortfolioResponseSchema)
async def get_portfolio(
    portfolio_id: str,
    # current_user: AuthUserResponseSchema = Depends(get_current_user),
    portfolio_use_cases: PortfolioAggregateUseCases = Depends(get_portfolio_aggregate_use_cases)
):
    """Get portfolio by ID"""
    try:
        # Use a test user ID for now
        test_user_id = "test-user-123"
        portfolio = await portfolio_use_cases.get_portfolio_by_id(test_user_id, portfolio_id)
        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio not found"
            )
        return portfolio
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve portfolio"
        )


@router.get("/{portfolio_id}/details", response_model=PortfolioDetailResponseSchema)
async def get_portfolio_details(
    portfolio_id: str,
    # current_user: AuthUserResponseSchema = Depends(get_current_user),
    portfolio_use_cases: PortfolioAggregateUseCases = Depends(get_portfolio_aggregate_use_cases)
):
    """Get detailed portfolio information including holdings and summary"""
    try:
        # Use a test user ID for now
        test_user_id = "test-user-123"
        portfolio_details = await portfolio_use_cases.get_portfolio_details(test_user_id, portfolio_id)
        if not portfolio_details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio not found"
            )
        return portfolio_details
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve portfolio details"
        )


@router.get("/{portfolio_id}/performance", response_model=PortfolioPerformanceResponseSchema)
async def get_portfolio_performance(
    portfolio_id: str,
    # current_user: AuthUserResponseSchema = Depends(get_current_user),
    portfolio_use_cases: PortfolioAggregateUseCases = Depends(get_portfolio_aggregate_use_cases)
):
    """Get portfolio performance metrics and analytics"""
    try:
        # Use a test user ID for now
        test_user_id = "test-user-123"
        performance = await portfolio_use_cases.get_portfolio_performance(test_user_id, portfolio_id)
        if not performance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio not found"
            )
        return performance
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve portfolio performance"
        )


@router.put("/{portfolio_id}", response_model=PortfolioResponseSchema)
async def update_portfolio(
    portfolio_id: str,
    update_data: UpdatePortfolioSchema,
    # current_user: AuthUserResponseSchema = Depends(get_current_user),
    portfolio_use_cases: PortfolioAggregateUseCases = Depends(get_portfolio_aggregate_use_cases)
):
    """Update portfolio information"""
    try:
        request = UpdatePortfolioRequest(
            name=update_data.name,
            description=update_data.description
        )
        
        # Use a test user ID for now
        test_user_id = "test-user-123"
        portfolio = await portfolio_use_cases.update_portfolio(test_user_id, portfolio_id, request)
        return portfolio
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update portfolio"
        )


@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_portfolio(
    portfolio_id: str,
    # current_user: AuthUserResponseSchema = Depends(get_current_user),
    portfolio_use_cases: PortfolioAggregateUseCases = Depends(get_portfolio_aggregate_use_cases)
):
    """Delete a portfolio"""
    try:
        # Use a test user ID for now
        test_user_id = "test-user-123"
        success = await portfolio_use_cases.delete_portfolio(test_user_id, portfolio_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio not found"
            )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete portfolio"
        )
