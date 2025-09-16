from typing import List, Optional
from application.interfaces.repositories import IPortfolioRepository, IUserRepository, ICryptoAssetRepository
from domain.entities.portfolio import Portfolio
from domain.value_objects.portfolio_id import PortfolioId
from domain.value_objects.user_id import UserId
from domain.value_objects.asset_id import AssetId
from application.dtos.portfolio_dtos import CreatePortfolioRequest, UpdatePortfolioRequest, PortfolioResponse


class PortfolioUseCases:
    """Use cases for portfolio management"""
    
    def __init__(
        self, 
        portfolio_repository: IPortfolioRepository,
        user_repository: IUserRepository,
        crypto_asset_repository: ICryptoAssetRepository
    ):
        self._portfolio_repository = portfolio_repository
        self._user_repository = user_repository
        self._crypto_asset_repository = crypto_asset_repository
    
    async def create_portfolio_entry(self, request: CreatePortfolioRequest) -> PortfolioResponse:
        """Create a new portfolio entry"""
        # Validate user exists
        user = await self._user_repository.get_by_id(UserId(request.user_id))
        if not user:
            raise ValueError(f"User with ID {request.user_id} not found")
        
        # Validate asset exists
        asset = await self._crypto_asset_repository.get_by_id(AssetId(request.asset_id))
        if not asset:
            raise ValueError(f"Asset with ID {request.asset_id} not found")
        
        # Create domain entity
        portfolio = Portfolio.create(
            user_id=request.user_id,
            asset_id=request.asset_id,
            quantity=request.quantity,
            purchase_price=request.purchase_price
        )
        
        # Save to repository
        created_portfolio = await self._portfolio_repository.create(portfolio)
        
        # Return DTO
        return PortfolioResponse.from_entity(created_portfolio)
    
    async def get_portfolio_by_id(self, portfolio_id: str) -> Optional[PortfolioResponse]:
        """Get portfolio entry by ID"""
        portfolio = await self._portfolio_repository.get_by_id(PortfolioId(portfolio_id))
        return PortfolioResponse.from_entity(portfolio) if portfolio else None
    
    async def get_user_portfolio(self, user_id: str) -> List[PortfolioResponse]:
        """Get all portfolio entries for a user"""
        portfolios = await self._portfolio_repository.get_by_user_id(UserId(user_id))
        return [PortfolioResponse.from_entity(portfolio) for portfolio in portfolios]
    
    async def get_all_portfolios(self, skip: int = 0, limit: int = 100) -> List[PortfolioResponse]:
        """Get all portfolio entries with pagination"""
        portfolios = await self._portfolio_repository.get_all(skip=skip, limit=limit)
        return [PortfolioResponse.from_entity(portfolio) for portfolio in portfolios]
    
    async def update_portfolio_entry(self, portfolio_id: str, request: UpdatePortfolioRequest) -> Optional[PortfolioResponse]:
        """Update portfolio entry"""
        portfolio = await self._portfolio_repository.get_by_id(PortfolioId(portfolio_id))
        if not portfolio:
            return None
        
        # Update domain entity
        if request.quantity is not None:
            portfolio.update_quantity(request.quantity)
        
        if request.purchase_price is not None:
            portfolio.update_purchase_price(request.purchase_price)
        
        # Save to repository
        updated_portfolio = await self._portfolio_repository.update(portfolio)
        
        # Return DTO
        return PortfolioResponse.from_entity(updated_portfolio)
    
    async def delete_portfolio_entry(self, portfolio_id: str) -> bool:
        """Delete portfolio entry"""
        return await self._portfolio_repository.delete(PortfolioId(portfolio_id))
    
    async def get_portfolio_value(self, user_id: str) -> dict:
        """Calculate total portfolio value and profit/loss"""
        portfolios = await self._portfolio_repository.get_by_user_id(UserId(user_id))
        
        total_value = 0.0
        total_cost = 0.0
        portfolio_details = []
        
        for portfolio in portfolios:
            # Get current asset price
            asset = await self._crypto_asset_repository.get_by_id(portfolio.asset_id)
            if asset and asset.current_price:
                current_price = asset.price_as_float
                value = float(portfolio.calculate_value(current_price))
                cost = float(portfolio.quantity * portfolio.purchase_price)
                profit_loss = float(portfolio.calculate_profit_loss(current_price))
                profit_loss_pct = float(portfolio.calculate_profit_loss_percentage(current_price))
                
                total_value += value
                total_cost += cost
                
                portfolio_details.append({
                    "portfolio_id": str(portfolio.id),
                    "asset_symbol": str(asset.symbol),
                    "quantity": portfolio.quantity_as_float,
                    "purchase_price": portfolio.purchase_price_as_float,
                    "current_price": current_price,
                    "current_value": value,
                    "cost_basis": cost,
                    "profit_loss": profit_loss,
                    "profit_loss_percentage": profit_loss_pct
                })
        
        total_profit_loss = total_value - total_cost
        total_profit_loss_pct = (total_profit_loss / total_cost * 100) if total_cost > 0 else 0
        
        return {
            "user_id": user_id,
            "total_value": total_value,
            "total_cost": total_cost,
            "total_profit_loss": total_profit_loss,
            "total_profit_loss_percentage": total_profit_loss_pct,
            "portfolio_details": portfolio_details
        }
