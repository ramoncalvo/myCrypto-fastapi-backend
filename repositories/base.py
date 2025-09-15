from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, TypeVar, Generic
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class BaseRepository(ABC, Generic[T]):
    """Abstract base repository for database operations"""
    
    @abstractmethod
    async def create(self, data: Dict[str, Any]) -> T:
        """Create a new document"""
        pass
    
    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[T]:
        """Get document by ID"""
        pass
    
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all documents with pagination"""
        pass
    
    @abstractmethod
    async def update(self, id: str, data: Dict[str, Any]) -> Optional[T]:
        """Update document by ID"""
        pass
    
    @abstractmethod
    async def delete(self, id: str) -> bool:
        """Delete document by ID"""
        pass
    
    @abstractmethod
    async def find_by_field(self, field: str, value: Any) -> List[T]:
        """Find documents by field value"""
        pass

class UserRepository(BaseRepository[T]):
    """Repository interface for User operations"""
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[T]:
        """Get user by email"""
        pass

class CryptoAssetRepository(BaseRepository[T]):
    """Repository interface for CryptoAsset operations"""
    
    @abstractmethod
    async def get_by_symbol(self, symbol: str) -> Optional[T]:
        """Get crypto asset by symbol"""
        pass

class PortfolioRepository(BaseRepository[T]):
    """Repository interface for Portfolio operations"""
    
    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> List[T]:
        """Get portfolio entries by user ID"""
        pass
    
    @abstractmethod
    async def get_by_user_and_asset(self, user_id: str, asset_id: str) -> Optional[T]:
        """Get portfolio entry by user and asset"""
        pass
