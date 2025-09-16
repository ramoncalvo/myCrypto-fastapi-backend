from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from decimal import Decimal
from enum import Enum
from domain.value_objects.transaction_id import TransactionId
from domain.value_objects.user_id import UserId
from domain.value_objects.asset_id import AssetId
from domain.value_objects.portfolio_id import PortfolioId


class TransactionType(Enum):
    """Transaction types"""
    BUY = "buy"
    SELL = "sell"
    TRANSFER_IN = "transfer_in"
    TRANSFER_OUT = "transfer_out"


class TransactionStatus(Enum):
    """Transaction status"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Transaction:
    """Transaction domain entity representing buy/sell operations"""
    
    id: TransactionId
    user_id: UserId
    portfolio_id: PortfolioId
    asset_id: AssetId
    transaction_type: TransactionType
    quantity: Decimal
    price: Decimal
    total_amount: Decimal
    fees: Decimal
    status: TransactionStatus
    created_at: datetime
    executed_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    notes: Optional[str] = None
    
    @classmethod
    def create_buy(
        cls,
        user_id: str,
        portfolio_id: str,
        asset_id: str,
        quantity: float,
        price: float,
        fees: float = 0.0,
        notes: Optional[str] = None,
        transaction_id: Optional[str] = None
    ) -> 'Transaction':
        """Factory method to create a buy transaction"""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if price < 0:
            raise ValueError("Price cannot be negative")
        if fees < 0:
            raise ValueError("Fees cannot be negative")
        
        quantity_decimal = Decimal(str(quantity))
        price_decimal = Decimal(str(price))
        fees_decimal = Decimal(str(fees))
        total_amount = (quantity_decimal * price_decimal) + fees_decimal
        
        return cls(
            id=TransactionId(transaction_id) if transaction_id else TransactionId.generate(),
            user_id=UserId(user_id),
            portfolio_id=PortfolioId(portfolio_id),
            asset_id=AssetId(asset_id),
            transaction_type=TransactionType.BUY,
            quantity=quantity_decimal,
            price=price_decimal,
            total_amount=total_amount,
            fees=fees_decimal,
            status=TransactionStatus.PENDING,
            created_at=datetime.utcnow(),
            notes=notes
        )
    
    @classmethod
    def create_sell(
        cls,
        user_id: str,
        portfolio_id: str,
        asset_id: str,
        quantity: float,
        price: float,
        fees: float = 0.0,
        notes: Optional[str] = None,
        transaction_id: Optional[str] = None
    ) -> 'Transaction':
        """Factory method to create a sell transaction"""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if price < 0:
            raise ValueError("Price cannot be negative")
        if fees < 0:
            raise ValueError("Fees cannot be negative")
        
        quantity_decimal = Decimal(str(quantity))
        price_decimal = Decimal(str(price))
        fees_decimal = Decimal(str(fees))
        total_amount = (quantity_decimal * price_decimal) - fees_decimal
        
        return cls(
            id=TransactionId(transaction_id) if transaction_id else TransactionId.generate(),
            user_id=UserId(user_id),
            portfolio_id=PortfolioId(portfolio_id),
            asset_id=AssetId(asset_id),
            transaction_type=TransactionType.SELL,
            quantity=quantity_decimal,
            price=price_decimal,
            total_amount=total_amount,
            fees=fees_decimal,
            status=TransactionStatus.PENDING,
            created_at=datetime.utcnow(),
            notes=notes
        )
    
    def execute(self):
        """Mark transaction as executed"""
        if self.status != TransactionStatus.PENDING:
            raise ValueError(f"Cannot execute transaction with status: {self.status.value}")
        
        self.status = TransactionStatus.COMPLETED
        self.executed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def cancel(self, reason: Optional[str] = None):
        """Cancel the transaction"""
        if self.status == TransactionStatus.COMPLETED:
            raise ValueError("Cannot cancel completed transaction")
        
        self.status = TransactionStatus.CANCELLED
        self.updated_at = datetime.utcnow()
        if reason:
            self.notes = f"{self.notes or ''}\nCancelled: {reason}".strip()
    
    def fail(self, reason: Optional[str] = None):
        """Mark transaction as failed"""
        if self.status == TransactionStatus.COMPLETED:
            raise ValueError("Cannot fail completed transaction")
        
        self.status = TransactionStatus.FAILED
        self.updated_at = datetime.utcnow()
        if reason:
            self.notes = f"{self.notes or ''}\nFailed: {reason}".strip()
    
    def calculate_net_amount(self) -> Decimal:
        """Calculate net amount (total - fees for buy, total + fees for sell)"""
        if self.transaction_type == TransactionType.BUY:
            return self.quantity * self.price
        else:  # SELL
            return (self.quantity * self.price) - self.fees
    
    def calculate_profit_loss(self, cost_basis: Decimal) -> Optional[Decimal]:
        """Calculate profit/loss for sell transactions"""
        if self.transaction_type != TransactionType.SELL:
            return None
        
        proceeds = self.calculate_net_amount()
        return proceeds - cost_basis
    
    @property
    def is_buy(self) -> bool:
        """Check if transaction is a buy"""
        return self.transaction_type == TransactionType.BUY
    
    @property
    def is_sell(self) -> bool:
        """Check if transaction is a sell"""
        return self.transaction_type == TransactionType.SELL
    
    @property
    def is_completed(self) -> bool:
        """Check if transaction is completed"""
        return self.status == TransactionStatus.COMPLETED
    
    @property
    def quantity_as_float(self) -> float:
        """Get quantity as float for external APIs"""
        return float(self.quantity)
    
    @property
    def price_as_float(self) -> float:
        """Get price as float for external APIs"""
        return float(self.price)
    
    @property
    def total_amount_as_float(self) -> float:
        """Get total amount as float for external APIs"""
        return float(self.total_amount)
    
    @property
    def fees_as_float(self) -> float:
        """Get fees as float for external APIs"""
        return float(self.fees)
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Transaction):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        return hash(self.id)
