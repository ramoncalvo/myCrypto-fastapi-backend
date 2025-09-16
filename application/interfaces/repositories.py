from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.user import User
from domain.entities.crypto_asset import CryptoAsset
from domain.entities.portfolio import Portfolio
from domain.value_objects.user_id import UserId
from domain.value_objects.asset_id import AssetId
from domain.value_objects.portfolio_id import PortfolioId
from domain.value_objects.email import Email
from domain.value_objects.symbol import Symbol


class IUserRepository(ABC):
    """Interface for user repository"""
    
    @abstractmethod
    async def create(self, user: User) -> User:
        """Create a new user"""
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: UserId) -> Optional[User]:
        """Get user by ID"""
        pass
    
    @abstractmethod
    async def get_by_email(self, email: Email) -> Optional[User]:
        """Get user by email"""
        pass
    
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination"""
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        """Update user"""
        pass
    
    @abstractmethod
    async def delete(self, user_id: UserId) -> bool:
        """Delete user"""
        pass


class ICryptoAssetRepository(ABC):
    """Interface for crypto asset repository"""
    
    @abstractmethod
    async def create(self, asset: CryptoAsset) -> CryptoAsset:
        """Create a new crypto asset"""
        pass
    
    @abstractmethod
    async def get_by_id(self, asset_id: AssetId) -> Optional[CryptoAsset]:
        """Get asset by ID"""
        pass
    
    @abstractmethod
    async def get_by_symbol(self, symbol: Symbol) -> Optional[CryptoAsset]:
        """Get asset by symbol"""
        pass
    
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[CryptoAsset]:
        """Get all assets with pagination"""
        pass
    
    @abstractmethod
    async def update(self, asset: CryptoAsset) -> CryptoAsset:
        """Update asset"""
        pass
    
    @abstractmethod
    async def delete(self, asset_id: AssetId) -> bool:
        """Delete asset"""
        pass


class IPortfolioRepository(ABC):
    """Interface for portfolio repository"""
    
    @abstractmethod
    async def create(self, portfolio: Portfolio) -> Portfolio:
        """Create a new portfolio entry"""
        pass
    
    @abstractmethod
    async def get_by_id(self, portfolio_id: PortfolioId) -> Optional[Portfolio]:
        """Get portfolio entry by ID"""
        pass
    
    @abstractmethod
    async def get_by_user_id(self, user_id: UserId) -> List[Portfolio]:
        """Get portfolio entries by user ID"""
        pass
    
    @abstractmethod
    async def get_by_user_and_asset(self, user_id: UserId, asset_id: AssetId) -> Optional[Portfolio]:
        """Get portfolio entry by user and asset"""
        pass
    
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Portfolio]:
        """Get all portfolio entries with pagination"""
        pass
    
    @abstractmethod
    async def update(self, portfolio: Portfolio) -> Portfolio:
        """Update portfolio entry"""
        pass
    
    @abstractmethod
    async def delete(self, portfolio_id: PortfolioId) -> bool:
        """Delete portfolio entry"""
        pass
