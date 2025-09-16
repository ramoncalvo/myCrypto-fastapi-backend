from typing import List, Optional, Dict
from decimal import Decimal
from application.interfaces.portfolio_aggregate_repository import PortfolioAggregateRepository
from application.interfaces.repositories import ICryptoAssetRepository
from application.dtos.portfolio_aggregate_dtos import (
    CreatePortfolioRequest, UpdatePortfolioRequest, PortfolioResponse,
    PortfolioDetailResponse, PortfolioSummaryResponse, AssetHoldingResponse,
    PortfolioPerformanceResponse, PortfolioFilterRequest
)
from domain.entities.portfolio_aggregate import PortfolioAggregate, AssetHolding
from domain.value_objects.portfolio_id import PortfolioId
from domain.value_objects.user_id import UserId
from domain.value_objects.asset_id import AssetId


class PortfolioAggregateUseCases:
    """Use cases for portfolio aggregate operations"""
    
    def __init__(
        self, 
        portfolio_repository: PortfolioAggregateRepository,
        crypto_asset_repository: ICryptoAssetRepository
    ):
        self._portfolio_repository = portfolio_repository
        self._crypto_asset_repository = crypto_asset_repository
    
    async def create_portfolio(
        self, 
        user_id: str, 
        request: CreatePortfolioRequest
    ) -> PortfolioResponse:
        """Create a new portfolio"""
        # Check if portfolio name already exists for user
        exists = await self._portfolio_repository.portfolio_exists_for_user(
            UserId(user_id), 
            request.name
        )
        if exists:
            raise ValueError("Portfolio with this name already exists")
        
        # Create portfolio
        portfolio = PortfolioAggregate.create(
            user_id=user_id,
            name=request.name,
            description=request.description
        )
        
        # Save portfolio
        created_portfolio = await self._portfolio_repository.create(portfolio)
        
        return self._to_portfolio_response(created_portfolio)
    
    async def get_portfolio_by_id(
        self, 
        user_id: str, 
        portfolio_id: str
    ) -> Optional[PortfolioResponse]:
        """Get portfolio by ID"""
        portfolio = await self._portfolio_repository.get_by_id(PortfolioId(portfolio_id))
        if not portfolio:
            return None
        
        # Validate user owns portfolio
        if str(portfolio.user_id) != user_id:
            raise ValueError("Portfolio does not belong to user")
        
        return self._to_portfolio_response(portfolio)
    
    async def get_portfolio_detail(
        self, 
        user_id: str, 
        portfolio_id: str
    ) -> Optional[PortfolioDetailResponse]:
        """Get detailed portfolio information with holdings and summary"""
        portfolio = await self._portfolio_repository.get_by_id(PortfolioId(portfolio_id))
        if not portfolio:
            return None
        
        # Validate user owns portfolio
        if str(portfolio.user_id) != user_id:
            raise ValueError("Portfolio does not belong to user")
        
        # Get current asset prices
        asset_prices = await self._get_current_asset_prices(portfolio)
        
        # Calculate summary
        summary = portfolio.calculate_summary(asset_prices)
        
        # Get holdings with asset details
        holdings = await self._get_holdings_with_details(portfolio, asset_prices)
        
        return PortfolioDetailResponse(
            id=str(portfolio.id),
            user_id=str(portfolio.user_id),
            name=portfolio.name,
            description=portfolio.description,
            holdings=holdings,
            summary=self._to_summary_response(summary),
            created_at=portfolio.created_at,
            updated_at=portfolio.updated_at
        )
    
    async def get_user_portfolios(
        self, 
        user_id: str, 
        filter_request: PortfolioFilterRequest
    ) -> List[PortfolioResponse]:
        """Get all portfolios for a user"""
        portfolios = await self._portfolio_repository.get_by_user_id(
            UserId(user_id),
            filter_request.skip,
            filter_request.limit
        )
        
        return [self._to_portfolio_response(p) for p in portfolios]
    
    async def update_portfolio(
        self, 
        user_id: str, 
        portfolio_id: str,
        request: UpdatePortfolioRequest
    ) -> PortfolioResponse:
        """Update portfolio information"""
        portfolio = await self._portfolio_repository.get_by_id(PortfolioId(portfolio_id))
        if not portfolio:
            raise ValueError("Portfolio not found")
        
        # Validate user owns portfolio
        if str(portfolio.user_id) != user_id:
            raise ValueError("Portfolio does not belong to user")
        
        # Check if new name conflicts with existing portfolios
        if request.name and request.name != portfolio.name:
            exists = await self._portfolio_repository.portfolio_exists_for_user(
                UserId(user_id), 
                request.name
            )
            if exists:
                raise ValueError("Portfolio with this name already exists")
        
        # Update portfolio
        portfolio.update_portfolio_info(request.name, request.description)
        
        # Save changes
        updated_portfolio = await self._portfolio_repository.update(portfolio)
        
        return self._to_portfolio_response(updated_portfolio)
    
    async def delete_portfolio(self, user_id: str, portfolio_id: str) -> bool:
        """Delete a portfolio"""
        portfolio = await self._portfolio_repository.get_by_id(PortfolioId(portfolio_id))
        if not portfolio:
            return False
        
        # Validate user owns portfolio
        if str(portfolio.user_id) != user_id:
            raise ValueError("Portfolio does not belong to user")
        
        # Delete portfolio
        return await self._portfolio_repository.delete(PortfolioId(portfolio_id))
    
    async def get_portfolio_performance(
        self, 
        user_id: str, 
        portfolio_id: str
    ) -> Optional[PortfolioPerformanceResponse]:
        """Get detailed portfolio performance metrics"""
        portfolio = await self._portfolio_repository.get_by_id(PortfolioId(portfolio_id))
        if not portfolio:
            return None
        
        # Validate user owns portfolio
        if str(portfolio.user_id) != user_id:
            raise ValueError("Portfolio does not belong to user")
        
        # Get current asset prices
        asset_prices = await self._get_current_asset_prices(portfolio)
        
        # Get performance metrics
        performance = portfolio.get_performance_metrics(asset_prices)
        
        # Get holdings with details
        holdings = await self._get_holdings_with_details(portfolio, asset_prices)
        
        # Sort holdings by performance
        holdings_sorted = sorted(holdings, key=lambda h: h.profit_loss_percentage, reverse=True)
        top_performers = holdings_sorted[:5]  # Top 5
        worst_performers = holdings_sorted[-5:] if len(holdings_sorted) > 5 else []  # Bottom 5
        
        return PortfolioPerformanceResponse(
            summary=self._to_summary_response(performance["summary"]),
            transaction_stats=performance["transaction_stats"],
            pnl_breakdown=performance["pnl_breakdown"],
            top_performers=top_performers,
            worst_performers=worst_performers
        )
    
    async def get_portfolio_summary(
        self, 
        user_id: str, 
        portfolio_id: str
    ) -> Optional[PortfolioSummaryResponse]:
        """Get portfolio summary only"""
        portfolio = await self._portfolio_repository.get_by_id(PortfolioId(portfolio_id))
        if not portfolio:
            return None
        
        # Validate user owns portfolio
        if str(portfolio.user_id) != user_id:
            raise ValueError("Portfolio does not belong to user")
        
        # Get current asset prices
        asset_prices = await self._get_current_asset_prices(portfolio)
        
        # Calculate summary
        summary = portfolio.calculate_summary(asset_prices)
        
        return self._to_summary_response(summary)
    
    async def get_user_portfolio_overview(self, user_id: str) -> Dict[str, any]:
        """Get overview of all user portfolios"""
        portfolios = await self._portfolio_repository.get_by_user_id(UserId(user_id))
        
        total_portfolios = len(portfolios)
        total_value = Decimal('0')
        total_cost_basis = Decimal('0')
        total_assets = 0
        
        portfolio_summaries = []
        
        for portfolio in portfolios:
            # Get current asset prices for this portfolio
            asset_prices = await self._get_current_asset_prices(portfolio)
            
            # Calculate summary
            summary = portfolio.calculate_summary(asset_prices)
            
            total_value += summary.total_value
            total_cost_basis += summary.total_cost_basis
            total_assets += summary.asset_count
            
            portfolio_summaries.append({
                "id": str(portfolio.id),
                "name": portfolio.name,
                "summary": self._to_summary_response(summary)
            })
        
        total_profit_loss = total_value - total_cost_basis
        total_profit_loss_percentage = Decimal('0')
        if total_cost_basis > 0:
            total_profit_loss_percentage = (total_profit_loss / total_cost_basis) * Decimal('100')
        
        return {
            "total_portfolios": total_portfolios,
            "total_value": float(total_value),
            "total_cost_basis": float(total_cost_basis),
            "total_profit_loss": float(total_profit_loss),
            "total_profit_loss_percentage": float(total_profit_loss_percentage),
            "total_assets": total_assets,
            "portfolios": portfolio_summaries
        }
    
    async def _get_current_asset_prices(self, portfolio: PortfolioAggregate) -> Dict[str, Decimal]:
        """Get current prices for all assets in portfolio"""
        asset_prices = {}
        
        for asset_id in portfolio.holdings.keys():
            try:
                asset = await self._crypto_asset_repository.get_by_id(AssetId(asset_id))
                if asset:
                    asset_prices[asset_id] = Decimal(str(asset.current_price))
                else:
                    asset_prices[asset_id] = Decimal('0')
            except Exception:
                asset_prices[asset_id] = Decimal('0')
        
        return asset_prices
    
    async def _get_holdings_with_details(
        self, 
        portfolio: PortfolioAggregate, 
        asset_prices: Dict[str, Decimal]
    ) -> List[AssetHoldingResponse]:
        """Get holdings with asset details"""
        holdings = []
        
        for asset_id, holding in portfolio.holdings.items():
            if holding.total_quantity > 0:
                # Get asset details
                asset = await self._crypto_asset_repository.get_by_id(AssetId(asset_id))
                
                # Update holding with current price
                current_price = asset_prices.get(asset_id, Decimal('0'))
                holding.current_price = current_price
                holding.current_value = holding.total_quantity * current_price
                holding.profit_loss = holding.current_value - holding.cost_basis
                
                if holding.cost_basis > 0:
                    holding.profit_loss_percentage = (holding.profit_loss / holding.cost_basis) * Decimal('100')
                else:
                    holding.profit_loss_percentage = Decimal('0')
                
                holdings.append(AssetHoldingResponse(
                    asset_id=holding.asset_id,
                    symbol=asset.symbol if asset else "UNKNOWN",
                    name=asset.name if asset else "Unknown Asset",
                    total_quantity=float(holding.total_quantity),
                    average_cost=float(holding.average_cost),
                    current_price=float(holding.current_price),
                    current_value=float(holding.current_value),
                    cost_basis=float(holding.cost_basis),
                    profit_loss=float(holding.profit_loss),
                    profit_loss_percentage=float(holding.profit_loss_percentage),
                    transaction_count=len(holding.transactions)
                ))
        
        return holdings
    
    def _to_portfolio_response(self, portfolio: PortfolioAggregate) -> PortfolioResponse:
        """Convert portfolio entity to response DTO"""
        return PortfolioResponse(
            id=str(portfolio.id),
            user_id=str(portfolio.user_id),
            name=portfolio.name,
            description=portfolio.description,
            created_at=portfolio.created_at,
            updated_at=portfolio.updated_at
        )
    
    def _to_summary_response(self, summary) -> PortfolioSummaryResponse:
        """Convert portfolio summary to response DTO"""
        return PortfolioSummaryResponse(
            total_value=float(summary.total_value),
            total_cost_basis=float(summary.total_cost_basis),
            total_profit_loss=float(summary.total_profit_loss),
            total_profit_loss_percentage=float(summary.total_profit_loss_percentage),
            asset_count=summary.asset_count,
            last_updated=summary.last_updated
        )
