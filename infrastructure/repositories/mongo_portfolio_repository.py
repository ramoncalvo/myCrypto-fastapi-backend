from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from decimal import Decimal

from application.interfaces.repositories import IPortfolioRepository
from domain.entities.portfolio import Portfolio
from domain.value_objects.portfolio_id import PortfolioId
from domain.value_objects.user_id import UserId
from domain.value_objects.asset_id import AssetId


class MongoPortfolioRepository(IPortfolioRepository):
    """MongoDB implementation of portfolio repository"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database.portfolio
    
    async def create(self, portfolio: Portfolio) -> Portfolio:
        """Create a new portfolio entry"""
        portfolio_doc = self._to_document(portfolio)
        result = await self.collection.insert_one(portfolio_doc)
        portfolio_doc["_id"] = result.inserted_id
        return self._to_entity(portfolio_doc)
    
    async def get_by_id(self, portfolio_id: PortfolioId) -> Optional[Portfolio]:
        """Get portfolio entry by ID"""
        try:
            portfolio_doc = await self.collection.find_one({"_id": ObjectId(str(portfolio_id))})
            return self._to_entity(portfolio_doc) if portfolio_doc else None
        except Exception:
            return None
    
    async def get_by_user_id(self, user_id: UserId) -> List[Portfolio]:
        """Get portfolio entries by user ID"""
        cursor = self.collection.find({"user_id": str(user_id)})
        portfolio_docs = await cursor.to_list(length=None)
        return [self._to_entity(doc) for doc in portfolio_docs]
    
    async def get_by_user_and_asset(self, user_id: UserId, asset_id: AssetId) -> Optional[Portfolio]:
        """Get portfolio entry by user and asset"""
        portfolio_doc = await self.collection.find_one({
            "user_id": str(user_id),
            "asset_id": str(asset_id)
        })
        return self._to_entity(portfolio_doc) if portfolio_doc else None
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Portfolio]:
        """Get all portfolio entries with pagination"""
        cursor = self.collection.find().skip(skip).limit(limit)
        portfolio_docs = await cursor.to_list(length=limit)
        return [self._to_entity(doc) for doc in portfolio_docs]
    
    async def update(self, portfolio: Portfolio) -> Portfolio:
        """Update portfolio entry"""
        portfolio_doc = self._to_document(portfolio)
        portfolio_doc.pop("_id", None)  # Remove _id from update data
        
        await self.collection.update_one(
            {"_id": ObjectId(str(portfolio.id))},
            {"$set": portfolio_doc}
        )
        return portfolio
    
    async def delete(self, portfolio_id: PortfolioId) -> bool:
        """Delete portfolio entry"""
        result = await self.collection.delete_one({"_id": ObjectId(str(portfolio_id))})
        return result.deleted_count > 0
    
    def _to_document(self, portfolio: Portfolio) -> Dict[str, Any]:
        """Convert domain entity to MongoDB document"""
        return {
            "_id": ObjectId(str(portfolio.id)),
            "user_id": str(portfolio.user_id),
            "asset_id": str(portfolio.asset_id),
            "quantity": float(portfolio.quantity),
            "purchase_price": float(portfolio.purchase_price),
            "created_at": portfolio.created_at,
            "updated_at": portfolio.updated_at
        }
    
    def _to_entity(self, portfolio_doc: Dict[str, Any]) -> Portfolio:
        """Convert MongoDB document to domain entity"""
        return Portfolio(
            id=PortfolioId(str(portfolio_doc["_id"])),
            user_id=UserId(portfolio_doc["user_id"]),
            asset_id=AssetId(portfolio_doc["asset_id"]),
            quantity=Decimal(str(portfolio_doc["quantity"])),
            purchase_price=Decimal(str(portfolio_doc["purchase_price"])),
            created_at=portfolio_doc["created_at"],
            updated_at=portfolio_doc.get("updated_at")
        )
