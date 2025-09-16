from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional
from decimal import Decimal
from domain.value_objects.portfolio_id import PortfolioId
from domain.value_objects.user_id import UserId
from domain.entities.portfolio import Portfolio
from domain.entities.transaction import Transaction, TransactionType


@dataclass
class PortfolioSummary:
    """Portfolio summary with calculated metrics"""
    total_value: Decimal
    total_cost_basis: Decimal
    total_profit_loss: Decimal
    total_profit_loss_percentage: Decimal
    asset_count: int
    last_updated: datetime


@dataclass
class AssetHolding:
    """Represents a complete asset holding with all transactions"""
    asset_id: str
    symbol: str
    name: str
    total_quantity: Decimal
    average_cost: Decimal
    current_price: Decimal
    current_value: Decimal
    cost_basis: Decimal
    profit_loss: Decimal
    profit_loss_percentage: Decimal
    transactions: List[Transaction] = field(default_factory=list)


@dataclass
class PortfolioAggregate:
    """Portfolio aggregate entity for complete portfolio management"""
    
    id: PortfolioId
    user_id: UserId
    name: str
    description: Optional[str]
    holdings: Dict[str, AssetHolding] = field(default_factory=dict)
    transactions: List[Transaction] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    @classmethod
    def create(
        cls,
        user_id: str,
        name: str,
        description: Optional[str] = None,
        portfolio_id: Optional[str] = None
    ) -> 'PortfolioAggregate':
        """Factory method to create a new portfolio"""
        if not name or not name.strip():
            raise ValueError("Portfolio name is required")
        
        return cls(
            id=PortfolioId(portfolio_id) if portfolio_id else PortfolioId.generate(),
            user_id=UserId(user_id),
            name=name.strip(),
            description=description
        )
    
    def add_transaction(self, transaction: Transaction):
        """Add a transaction to the portfolio"""
        if str(transaction.portfolio_id) != str(self.id):
            raise ValueError("Transaction portfolio_id does not match this portfolio")
        
        if str(transaction.user_id) != str(self.user_id):
            raise ValueError("Transaction user_id does not match this portfolio")
        
        self.transactions.append(transaction)
        self._update_holdings_from_transaction(transaction)
        self.updated_at = datetime.utcnow()
    
    def _update_holdings_from_transaction(self, transaction: Transaction):
        """Update holdings based on transaction"""
        asset_id = str(transaction.asset_id)
        
        if asset_id not in self.holdings:
            # Create new holding if it doesn't exist
            self.holdings[asset_id] = AssetHolding(
                asset_id=asset_id,
                symbol="",  # Will be populated when calculating summary
                name="",    # Will be populated when calculating summary
                total_quantity=Decimal('0'),
                average_cost=Decimal('0'),
                current_price=Decimal('0'),
                current_value=Decimal('0'),
                cost_basis=Decimal('0'),
                profit_loss=Decimal('0'),
                profit_loss_percentage=Decimal('0'),
                transactions=[]
            )
        
        holding = self.holdings[asset_id]
        holding.transactions.append(transaction)
        
        if transaction.is_completed:
            if transaction.is_buy:
                self._process_buy_transaction(holding, transaction)
            elif transaction.is_sell:
                self._process_sell_transaction(holding, transaction)
    
    def _process_buy_transaction(self, holding: AssetHolding, transaction: Transaction):
        """Process a buy transaction"""
        old_cost_basis = holding.total_quantity * holding.average_cost
        new_cost_basis = old_cost_basis + (transaction.quantity * transaction.price)
        new_quantity = holding.total_quantity + transaction.quantity
        
        holding.total_quantity = new_quantity
        holding.average_cost = new_cost_basis / new_quantity if new_quantity > 0 else Decimal('0')
        holding.cost_basis = new_cost_basis
    
    def _process_sell_transaction(self, holding: AssetHolding, transaction: Transaction):
        """Process a sell transaction"""
        if transaction.quantity > holding.total_quantity:
            raise ValueError("Cannot sell more than current holding")
        
        # Update quantity
        holding.total_quantity -= transaction.quantity
        
        # Update cost basis (proportional reduction)
        if holding.total_quantity > 0:
            cost_basis_reduction = holding.average_cost * transaction.quantity
            holding.cost_basis -= cost_basis_reduction
        else:
            # All sold
            holding.cost_basis = Decimal('0')
            holding.average_cost = Decimal('0')
    
    def calculate_summary(self, asset_prices: Dict[str, Decimal]) -> PortfolioSummary:
        """Calculate portfolio summary with current prices"""
        total_value = Decimal('0')
        total_cost_basis = Decimal('0')
        asset_count = 0
        
        for asset_id, holding in self.holdings.items():
            if holding.total_quantity > 0:
                current_price = asset_prices.get(asset_id, Decimal('0'))
                holding.current_price = current_price
                holding.current_value = holding.total_quantity * current_price
                holding.profit_loss = holding.current_value - holding.cost_basis
                
                if holding.cost_basis > 0:
                    holding.profit_loss_percentage = (holding.profit_loss / holding.cost_basis) * Decimal('100')
                else:
                    holding.profit_loss_percentage = Decimal('0')
                
                total_value += holding.current_value
                total_cost_basis += holding.cost_basis
                asset_count += 1
        
        total_profit_loss = total_value - total_cost_basis
        total_profit_loss_percentage = Decimal('0')
        if total_cost_basis > 0:
            total_profit_loss_percentage = (total_profit_loss / total_cost_basis) * Decimal('100')
        
        return PortfolioSummary(
            total_value=total_value,
            total_cost_basis=total_cost_basis,
            total_profit_loss=total_profit_loss,
            total_profit_loss_percentage=total_profit_loss_percentage,
            asset_count=asset_count,
            last_updated=datetime.utcnow()
        )
    
    def get_asset_holding(self, asset_id: str) -> Optional[AssetHolding]:
        """Get holding for specific asset"""
        return self.holdings.get(asset_id)
    
    def get_active_holdings(self) -> List[AssetHolding]:
        """Get all holdings with quantity > 0"""
        return [holding for holding in self.holdings.values() if holding.total_quantity > 0]
    
    def get_transaction_history(
        self, 
        asset_id: Optional[str] = None,
        transaction_type: Optional[TransactionType] = None,
        limit: Optional[int] = None
    ) -> List[Transaction]:
        """Get transaction history with optional filters"""
        filtered_transactions = self.transactions
        
        if asset_id:
            filtered_transactions = [t for t in filtered_transactions if str(t.asset_id) == asset_id]
        
        if transaction_type:
            filtered_transactions = [t for t in filtered_transactions if t.transaction_type == transaction_type]
        
        # Sort by created_at descending (newest first)
        filtered_transactions.sort(key=lambda t: t.created_at, reverse=True)
        
        if limit:
            filtered_transactions = filtered_transactions[:limit]
        
        return filtered_transactions
    
    def update_portfolio_info(self, name: Optional[str] = None, description: Optional[str] = None):
        """Update portfolio basic information"""
        if name and name.strip():
            self.name = name.strip()
        
        if description is not None:
            self.description = description
        
        self.updated_at = datetime.utcnow()
    
    def get_performance_metrics(self, asset_prices: Dict[str, Decimal]) -> Dict[str, any]:
        """Get detailed performance metrics"""
        summary = self.calculate_summary(asset_prices)
        
        # Calculate additional metrics
        total_transactions = len(self.transactions)
        completed_transactions = len([t for t in self.transactions if t.is_completed])
        buy_transactions = len([t for t in self.transactions if t.is_buy and t.is_completed])
        sell_transactions = len([t for t in self.transactions if t.is_sell and t.is_completed])
        
        # Calculate total fees paid
        total_fees = sum(t.fees for t in self.transactions if t.is_completed)
        
        # Calculate realized vs unrealized P&L
        realized_pnl = Decimal('0')
        for transaction in self.transactions:
            if transaction.is_sell and transaction.is_completed:
                # This is a simplified calculation - in practice you'd need to track cost basis per sale
                realized_pnl += transaction.calculate_net_amount()
        
        return {
            "summary": summary,
            "transaction_stats": {
                "total_transactions": total_transactions,
                "completed_transactions": completed_transactions,
                "buy_transactions": buy_transactions,
                "sell_transactions": sell_transactions,
                "total_fees": float(total_fees)
            },
            "pnl_breakdown": {
                "realized_pnl": float(realized_pnl),
                "unrealized_pnl": float(summary.total_profit_loss),
                "total_pnl": float(realized_pnl + summary.total_profit_loss)
            }
        }
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, PortfolioAggregate):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        return hash(self.id)
