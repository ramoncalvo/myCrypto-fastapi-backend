from typing import List, Optional
from datetime import datetime
from application.interfaces.transaction_repository import TransactionRepository
from application.interfaces.portfolio_aggregate_repository import PortfolioAggregateRepository
from application.interfaces.repositories import ICryptoAssetRepository
from application.dtos.transaction_dtos import (
    CreateTransactionRequest, UpdateTransactionRequest, ExecuteTransactionRequest,
    CancelTransactionRequest, TransactionResponse, TransactionStatsResponse,
    TransactionFilterRequest
)
from domain.entities.transaction import Transaction, TransactionType, TransactionStatus
from domain.value_objects.transaction_id import TransactionId
from domain.value_objects.user_id import UserId
from domain.value_objects.portfolio_id import PortfolioId
from domain.value_objects.asset_id import AssetId


class TransactionUseCases:
    """Use cases for transaction operations"""
    
    def __init__(
        self, 
        transaction_repository: TransactionRepository,
        portfolio_repository: PortfolioAggregateRepository,
        crypto_asset_repository: ICryptoAssetRepository
    ):
        self._transaction_repository = transaction_repository
        self._portfolio_repository = portfolio_repository
        self._crypto_asset_repository = crypto_asset_repository
    
    async def create_buy_transaction(
        self, 
        user_id: str, 
        request: CreateTransactionRequest
    ) -> TransactionResponse:
        """Create a buy transaction"""
        # Validate portfolio exists and belongs to user
        portfolio = await self._portfolio_repository.get_by_id(PortfolioId(request.portfolio_id))
        if not portfolio:
            raise ValueError("Portfolio not found")
        
        if str(portfolio.user_id) != user_id:
            raise ValueError("Portfolio does not belong to user")
        
        # Validate asset exists
        asset = await self._crypto_asset_repository.get_by_id(AssetId(request.asset_id))
        if not asset:
            raise ValueError("Asset not found")
        
        # Validate transaction type
        if request.transaction_type.lower() != "buy":
            raise ValueError("Invalid transaction type for buy transaction")
        
        # Create transaction
        transaction = Transaction.create_buy(
            user_id=user_id,
            portfolio_id=request.portfolio_id,
            asset_id=request.asset_id,
            quantity=request.quantity,
            price=request.price,
            fees=request.fees,
            notes=request.notes
        )
        
        # Save transaction
        created_transaction = await self._transaction_repository.create(transaction)
        
        return self._to_transaction_response(created_transaction)
    
    async def create_sell_transaction(
        self, 
        user_id: str, 
        request: CreateTransactionRequest
    ) -> TransactionResponse:
        """Create a sell transaction"""
        # Validate portfolio exists and belongs to user
        portfolio = await self._portfolio_repository.get_by_id(PortfolioId(request.portfolio_id))
        if not portfolio:
            raise ValueError("Portfolio not found")
        
        if str(portfolio.user_id) != user_id:
            raise ValueError("Portfolio does not belong to user")
        
        # Validate asset exists
        asset = await self._crypto_asset_repository.get_by_id(AssetId(request.asset_id))
        if not asset:
            raise ValueError("Asset not found")
        
        # Validate transaction type
        if request.transaction_type.lower() != "sell":
            raise ValueError("Invalid transaction type for sell transaction")
        
        # Check if user has enough quantity to sell
        holding = portfolio.get_asset_holding(request.asset_id)
        if not holding or holding.total_quantity < request.quantity:
            raise ValueError("Insufficient quantity to sell")
        
        # Create transaction
        transaction = Transaction.create_sell(
            user_id=user_id,
            portfolio_id=request.portfolio_id,
            asset_id=request.asset_id,
            quantity=request.quantity,
            price=request.price,
            fees=request.fees,
            notes=request.notes
        )
        
        # Save transaction
        created_transaction = await self._transaction_repository.create(transaction)
        
        return self._to_transaction_response(created_transaction)
    
    async def execute_transaction(
        self, 
        user_id: str, 
        request: ExecuteTransactionRequest
    ) -> TransactionResponse:
        """Execute a pending transaction"""
        # Get transaction
        transaction = await self._transaction_repository.get_by_id(TransactionId(request.transaction_id))
        if not transaction:
            raise ValueError("Transaction not found")
        
        # Validate user owns transaction
        if str(transaction.user_id) != user_id:
            raise ValueError("Transaction does not belong to user")
        
        # Execute transaction
        transaction.execute()
        
        # Update transaction
        updated_transaction = await self._transaction_repository.update(transaction)
        
        # Update portfolio with transaction
        portfolio = await self._portfolio_repository.get_by_id(transaction.portfolio_id)
        if portfolio:
            portfolio.add_transaction(updated_transaction)
            await self._portfolio_repository.update(portfolio)
        
        return self._to_transaction_response(updated_transaction)
    
    async def cancel_transaction(
        self, 
        user_id: str, 
        request: CancelTransactionRequest
    ) -> TransactionResponse:
        """Cancel a pending transaction"""
        # Get transaction
        transaction = await self._transaction_repository.get_by_id(TransactionId(request.transaction_id))
        if not transaction:
            raise ValueError("Transaction not found")
        
        # Validate user owns transaction
        if str(transaction.user_id) != user_id:
            raise ValueError("Transaction does not belong to user")
        
        # Cancel transaction
        transaction.cancel(request.reason)
        
        # Update transaction
        updated_transaction = await self._transaction_repository.update(transaction)
        
        return self._to_transaction_response(updated_transaction)
    
    async def get_transaction_by_id(
        self, 
        user_id: str, 
        transaction_id: str
    ) -> Optional[TransactionResponse]:
        """Get transaction by ID"""
        transaction = await self._transaction_repository.get_by_id(TransactionId(transaction_id))
        if not transaction:
            return None
        
        # Validate user owns transaction
        if str(transaction.user_id) != user_id:
            raise ValueError("Transaction does not belong to user")
        
        return self._to_transaction_response(transaction)
    
    async def get_user_transactions(
        self, 
        user_id: str, 
        filter_request: TransactionFilterRequest
    ) -> List[TransactionResponse]:
        """Get user transactions with filters"""
        transactions = []
        
        if filter_request.asset_id:
            transactions = await self._transaction_repository.get_by_asset_id(
                AssetId(filter_request.asset_id),
                UserId(user_id),
                filter_request.skip,
                filter_request.limit
            )
        elif filter_request.transaction_type:
            transaction_type = TransactionType(filter_request.transaction_type.lower())
            transactions = await self._transaction_repository.get_by_type(
                transaction_type,
                UserId(user_id),
                filter_request.skip,
                filter_request.limit
            )
        elif filter_request.status:
            status = TransactionStatus(filter_request.status.lower())
            transactions = await self._transaction_repository.get_by_status(
                status,
                UserId(user_id),
                filter_request.skip,
                filter_request.limit
            )
        elif filter_request.start_date and filter_request.end_date:
            transactions = await self._transaction_repository.get_by_date_range(
                filter_request.start_date,
                filter_request.end_date,
                UserId(user_id),
                filter_request.skip,
                filter_request.limit
            )
        else:
            transactions = await self._transaction_repository.get_by_user_id(
                UserId(user_id),
                filter_request.skip,
                filter_request.limit
            )
        
        return [self._to_transaction_response(t) for t in transactions]
    
    async def get_portfolio_transactions(
        self, 
        user_id: str, 
        portfolio_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[TransactionResponse]:
        """Get transactions for a specific portfolio"""
        # Validate portfolio belongs to user
        portfolio = await self._portfolio_repository.get_by_id(PortfolioId(portfolio_id))
        if not portfolio:
            raise ValueError("Portfolio not found")
        
        if str(portfolio.user_id) != user_id:
            raise ValueError("Portfolio does not belong to user")
        
        transactions = await self._transaction_repository.get_by_portfolio_id(
            PortfolioId(portfolio_id),
            skip,
            limit
        )
        
        return [self._to_transaction_response(t) for t in transactions]
    
    async def get_user_transaction_stats(self, user_id: str) -> TransactionStatsResponse:
        """Get transaction statistics for user"""
        stats = await self._transaction_repository.get_user_transaction_stats(UserId(user_id))
        
        return TransactionStatsResponse(
            total_transactions=stats.get("total_transactions", 0),
            completed_transactions=stats.get("completed_transactions", 0),
            buy_transactions=stats.get("buy_transactions", 0),
            sell_transactions=stats.get("sell_transactions", 0),
            total_fees=stats.get("total_fees", 0.0),
            total_buy_amount=stats.get("total_buy_amount", 0.0),
            total_sell_amount=stats.get("total_sell_amount", 0.0)
        )
    
    async def update_transaction(
        self, 
        user_id: str, 
        transaction_id: str,
        request: UpdateTransactionRequest
    ) -> TransactionResponse:
        """Update a pending transaction"""
        # Get transaction
        transaction = await self._transaction_repository.get_by_id(TransactionId(transaction_id))
        if not transaction:
            raise ValueError("Transaction not found")
        
        # Validate user owns transaction
        if str(transaction.user_id) != user_id:
            raise ValueError("Transaction does not belong to user")
        
        # Can only update pending transactions
        if transaction.status != TransactionStatus.PENDING:
            raise ValueError("Can only update pending transactions")
        
        # Update fields
        if request.quantity is not None:
            if request.quantity <= 0:
                raise ValueError("Quantity must be positive")
            transaction.quantity = request.quantity
            # Recalculate total amount
            if transaction.is_buy:
                transaction.total_amount = (transaction.quantity * transaction.price) + transaction.fees
            else:
                transaction.total_amount = (transaction.quantity * transaction.price) - transaction.fees
        
        if request.price is not None:
            if request.price < 0:
                raise ValueError("Price cannot be negative")
            transaction.price = request.price
            # Recalculate total amount
            if transaction.is_buy:
                transaction.total_amount = (transaction.quantity * transaction.price) + transaction.fees
            else:
                transaction.total_amount = (transaction.quantity * transaction.price) - transaction.fees
        
        if request.fees is not None:
            if request.fees < 0:
                raise ValueError("Fees cannot be negative")
            transaction.fees = request.fees
            # Recalculate total amount
            if transaction.is_buy:
                transaction.total_amount = (transaction.quantity * transaction.price) + transaction.fees
            else:
                transaction.total_amount = (transaction.quantity * transaction.price) - transaction.fees
        
        if request.notes is not None:
            transaction.notes = request.notes
        
        transaction.updated_at = datetime.utcnow()
        
        # Update transaction
        updated_transaction = await self._transaction_repository.update(transaction)
        
        return self._to_transaction_response(updated_transaction)
    
    def _to_transaction_response(self, transaction: Transaction) -> TransactionResponse:
        """Convert transaction entity to response DTO"""
        return TransactionResponse(
            id=str(transaction.id),
            user_id=str(transaction.user_id),
            portfolio_id=str(transaction.portfolio_id),
            asset_id=str(transaction.asset_id),
            transaction_type=transaction.transaction_type.value,
            quantity=transaction.quantity_as_float,
            price=transaction.price_as_float,
            total_amount=transaction.total_amount_as_float,
            fees=transaction.fees_as_float,
            status=transaction.status.value,
            created_at=transaction.created_at,
            executed_at=transaction.executed_at,
            updated_at=transaction.updated_at,
            notes=transaction.notes
        )
