from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from domain.entities.transaction import Transaction, TransactionType, TransactionStatus
from domain.value_objects.transaction_id import TransactionId
from domain.value_objects.user_id import UserId
from domain.value_objects.portfolio_id import PortfolioId
from domain.value_objects.asset_id import AssetId


class TransactionRepository(ABC):
    """Abstract repository for transaction operations"""
    
    @abstractmethod
    async def create(self, transaction: Transaction) -> Transaction:
        """Create a new transaction"""
        pass
    
    @abstractmethod
    async def get_by_id(self, transaction_id: TransactionId) -> Optional[Transaction]:
        """Get transaction by ID"""
        pass
    
    @abstractmethod
    async def get_by_user_id(
        self, 
        user_id: UserId, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Transaction]:
        """Get all transactions for a user"""
        pass
    
    @abstractmethod
    async def get_by_portfolio_id(
        self, 
        portfolio_id: PortfolioId, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Transaction]:
        """Get all transactions for a portfolio"""
        pass
    
    @abstractmethod
    async def get_by_asset_id(
        self, 
        asset_id: AssetId, 
        user_id: Optional[UserId] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Transaction]:
        """Get all transactions for an asset, optionally filtered by user"""
        pass
    
    @abstractmethod
    async def get_by_type(
        self, 
        transaction_type: TransactionType,
        user_id: Optional[UserId] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Transaction]:
        """Get transactions by type, optionally filtered by user"""
        pass
    
    @abstractmethod
    async def get_by_status(
        self, 
        status: TransactionStatus,
        user_id: Optional[UserId] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Transaction]:
        """Get transactions by status, optionally filtered by user"""
        pass
    
    @abstractmethod
    async def get_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        user_id: Optional[UserId] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Transaction]:
        """Get transactions within date range"""
        pass
    
    @abstractmethod
    async def update(self, transaction: Transaction) -> Transaction:
        """Update transaction"""
        pass
    
    @abstractmethod
    async def delete(self, transaction_id: TransactionId) -> bool:
        """Delete transaction"""
        pass
    
    @abstractmethod
    async def get_user_transaction_stats(self, user_id: UserId) -> dict:
        """Get transaction statistics for a user"""
        pass
