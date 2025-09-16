from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.portfolio_aggregate import PortfolioAggregate
from domain.value_objects.portfolio_id import PortfolioId
from domain.value_objects.user_id import UserId


class PortfolioAggregateRepository(ABC):
    """Abstract repository for portfolio aggregate operations"""
    
    @abstractmethod
    async def create(self, portfolio: PortfolioAggregate) -> PortfolioAggregate:
        """Create a new portfolio"""
        pass
    
    @abstractmethod
    async def get_by_id(self, portfolio_id: PortfolioId) -> Optional[PortfolioAggregate]:
        """Get portfolio by ID"""
        pass
    
    @abstractmethod
    async def get_by_user_id(
        self, 
        user_id: UserId, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[PortfolioAggregate]:
        """Get all portfolios for a user"""
        pass
    
    @abstractmethod
    async def update(self, portfolio: PortfolioAggregate) -> PortfolioAggregate:
        """Update portfolio"""
        pass
    
    @abstractmethod
    async def delete(self, portfolio_id: PortfolioId) -> bool:
        """Delete portfolio"""
        pass
    
    @abstractmethod
    async def portfolio_exists_for_user(self, user_id: UserId, name: str) -> bool:
        """Check if portfolio with name exists for user"""
        pass
