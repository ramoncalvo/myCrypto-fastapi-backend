from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from application.use_cases.portfolio_use_cases import PortfolioUseCases
from application.dtos.portfolio_dtos import CreatePortfolioRequest, UpdatePortfolioRequest
from presentation.dependencies import get_portfolio_use_cases
from presentation.schemas.portfolio_schemas import (
    PortfolioCreateSchema, PortfolioUpdateSchema, PortfolioResponseSchema
)


router = APIRouter(prefix="/portfolio", tags=["Portfolio"])


@router.post("/", response_model=PortfolioResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_portfolio_entry(
    portfolio_data: PortfolioCreateSchema,
    portfolio_use_cases: PortfolioUseCases = Depends(get_portfolio_use_cases)
):
    """Create a new portfolio entry"""
    try:
        request = CreatePortfolioRequest(
            user_id=portfolio_data.user_id,
            asset_id=portfolio_data.asset_id,
            quantity=portfolio_data.quantity,
            purchase_price=portfolio_data.purchase_price
        )
        
        portfolio_response = await portfolio_use_cases.create_portfolio_entry(request)
        return PortfolioResponseSchema.from_dto(portfolio_response)
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create portfolio entry")


@router.get("/", response_model=List[PortfolioResponseSchema])
async def get_all_portfolio_entries(
    skip: int = 0,
    limit: int = 100,
    portfolio_use_cases: PortfolioUseCases = Depends(get_portfolio_use_cases)
):
    """Get all portfolio entries with pagination"""
    try:
        portfolios = await portfolio_use_cases.get_all_portfolios(skip=skip, limit=limit)
        return [PortfolioResponseSchema.from_dto(portfolio) for portfolio in portfolios]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve portfolio entries")


@router.get("/{portfolio_id}", response_model=PortfolioResponseSchema)
async def get_portfolio_entry(
    portfolio_id: str,
    portfolio_use_cases: PortfolioUseCases = Depends(get_portfolio_use_cases)
):
    """Get portfolio entry by ID"""
    try:
        portfolio = await portfolio_use_cases.get_portfolio_by_id(portfolio_id)
        if not portfolio:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio entry not found")
        return PortfolioResponseSchema.from_dto(portfolio)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve portfolio entry")


@router.get("/user/{user_id}", response_model=List[PortfolioResponseSchema])
async def get_user_portfolio(
    user_id: str,
    portfolio_use_cases: PortfolioUseCases = Depends(get_portfolio_use_cases)
):
    """Get user's portfolio"""
    try:
        portfolios = await portfolio_use_cases.get_user_portfolio(user_id)
        return [PortfolioResponseSchema.from_dto(portfolio) for portfolio in portfolios]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve user portfolio")


@router.get("/user/{user_id}/value")
async def get_portfolio_value(
    user_id: str,
    portfolio_use_cases: PortfolioUseCases = Depends(get_portfolio_use_cases)
):
    """Get portfolio value analysis"""
    try:
        portfolio_value = await portfolio_use_cases.get_portfolio_value(user_id)
        return portfolio_value
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to calculate portfolio value")


@router.put("/{portfolio_id}", response_model=PortfolioResponseSchema)
async def update_portfolio_entry(
    portfolio_id: str,
    portfolio_data: PortfolioUpdateSchema,
    portfolio_use_cases: PortfolioUseCases = Depends(get_portfolio_use_cases)
):
    """Update portfolio entry"""
    try:
        request = UpdatePortfolioRequest(
            quantity=portfolio_data.quantity,
            purchase_price=portfolio_data.purchase_price
        )
        
        portfolio = await portfolio_use_cases.update_portfolio_entry(portfolio_id, request)
        if not portfolio:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio entry not found")
        return PortfolioResponseSchema.from_dto(portfolio)
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update portfolio entry")


@router.delete("/{portfolio_id}")
async def delete_portfolio_entry(
    portfolio_id: str,
    portfolio_use_cases: PortfolioUseCases = Depends(get_portfolio_use_cases)
):
    """Delete portfolio entry"""
    try:
        success = await portfolio_use_cases.delete_portfolio_entry(portfolio_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio entry not found")
        return {"message": "Portfolio entry deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete portfolio entry")
