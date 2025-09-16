from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from decimal import Decimal
from domain.value_objects.portfolio_id import PortfolioId
from domain.value_objects.user_id import UserId
from domain.value_objects.asset_id import AssetId


@dataclass
class Portfolio:
    """Portfolio domain entity representing a user's crypto asset holding"""
    
    id: PortfolioId
    user_id: UserId
    asset_id: AssetId
    quantity: Decimal
    purchase_price: Decimal
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @classmethod
    def create(
        cls,
        user_id: str,
        asset_id: str,
        quantity: float,
        purchase_price: float,
        portfolio_id: Optional[str] = None
    ) -> 'Portfolio':
        """Factory method to create a new portfolio entry"""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if purchase_price < 0:
            raise ValueError("Purchase price cannot be negative")
        
        return cls(
            id=PortfolioId(portfolio_id) if portfolio_id else PortfolioId.generate(),
            user_id=UserId(user_id),
            asset_id=AssetId(asset_id),
            quantity=Decimal(str(quantity)),
            purchase_price=Decimal(str(purchase_price)),
            created_at=datetime.utcnow()
        )
    
    def update_quantity(self, new_quantity: float):
        """Update the quantity of the asset"""
        if new_quantity <= 0:
            raise ValueError("Quantity must be positive")
        self.quantity = Decimal(str(new_quantity))
        self.updated_at = datetime.utcnow()
    
    def update_purchase_price(self, new_price: float):
        """Update the purchase price"""
        if new_price < 0:
            raise ValueError("Purchase price cannot be negative")
        self.purchase_price = Decimal(str(new_price))
        self.updated_at = datetime.utcnow()
    
    def calculate_value(self, current_price: float) -> Decimal:
        """Calculate current value of the holding"""
        return self.quantity * Decimal(str(current_price))
    
    def calculate_profit_loss(self, current_price: float) -> Decimal:
        """Calculate profit/loss based on current price"""
        current_value = self.calculate_value(current_price)
        cost_basis = self.quantity * self.purchase_price
        return current_value - cost_basis
    
    def calculate_profit_loss_percentage(self, current_price: float) -> Decimal:
        """Calculate profit/loss percentage"""
        cost_basis = self.quantity * self.purchase_price
        if cost_basis == 0:
            return Decimal('0')
        
        profit_loss = self.calculate_profit_loss(current_price)
        return (profit_loss / cost_basis) * Decimal('100')
    
    @property
    def quantity_as_float(self) -> float:
        """Get quantity as float for external APIs"""
        return float(self.quantity)
    
    @property
    def purchase_price_as_float(self) -> float:
        """Get purchase price as float for external APIs"""
        return float(self.purchase_price)
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Portfolio):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        return hash(self.id)
