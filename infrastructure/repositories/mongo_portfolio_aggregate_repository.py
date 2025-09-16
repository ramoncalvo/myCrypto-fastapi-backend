from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from application.interfaces.portfolio_aggregate_repository import PortfolioAggregateRepository
from application.interfaces.transaction_repository import TransactionRepository
from domain.entities.portfolio_aggregate import PortfolioAggregate, AssetHolding
from domain.entities.transaction import Transaction, TransactionType, TransactionStatus
from domain.value_objects.portfolio_id import PortfolioId
from domain.value_objects.user_id import UserId
from domain.value_objects.transaction_id import TransactionId
from domain.value_objects.asset_id import AssetId


class MongoPortfolioAggregateRepository(PortfolioAggregateRepository):
    """MongoDB implementation of portfolio aggregate repository"""
    
    def __init__(self, database: AsyncIOMotorDatabase, transaction_repository: TransactionRepository):
        self.collection = database.portfolio_aggregates
        self.transaction_repository = transaction_repository
    
    async def create(self, portfolio: PortfolioAggregate) -> PortfolioAggregate:
        """Create a new portfolio"""
        portfolio_doc = self._to_document(portfolio)
        result = await self.collection.insert_one(portfolio_doc)
        
        # Get the created document
        created_doc = await self.collection.find_one({"_id": result.inserted_id})
        return await self._to_entity(created_doc)
    
    async def get_by_id(self, portfolio_id: PortfolioId) -> Optional[PortfolioAggregate]:
        """Get portfolio by ID"""
        try:
            doc = await self.collection.find_one({"_id": ObjectId(str(portfolio_id))})
            return await self._to_entity(doc) if doc else None
        except Exception:
            return None
    
    async def get_by_user_id(
        self, 
        user_id: UserId, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[PortfolioAggregate]:
        """Get all portfolios for a user"""
        cursor = self.collection.find({"user_id": str(user_id)}).skip(skip).limit(limit).sort("created_at", -1)
        docs = await cursor.to_list(length=limit)
        portfolios = []
        for doc in docs:
            portfolio = await self._to_entity(doc)
            portfolios.append(portfolio)
        return portfolios
    
    async def update(self, portfolio: PortfolioAggregate) -> PortfolioAggregate:
        """Update portfolio"""
        portfolio_doc = self._to_document(portfolio)
        portfolio_doc.pop("_id", None)  # Remove _id for update
        
        # Store MongoDB ObjectId for updates
        mongo_id = getattr(portfolio, '_mongo_id', None)
        if mongo_id:
            object_id = ObjectId(mongo_id)
        else:
            object_id = ObjectId(str(portfolio.id))
        
        await self.collection.update_one(
            {"_id": object_id},
            {"$set": portfolio_doc}
        )
        
        # Return updated portfolio
        updated_doc = await self.collection.find_one({"_id": object_id})
        return await self._to_entity(updated_doc)
    
    async def delete(self, portfolio_id: PortfolioId) -> bool:
        """Delete portfolio"""
        result = await self.collection.delete_one({"_id": ObjectId(str(portfolio_id))})
        return result.deleted_count > 0
    
    async def portfolio_exists_for_user(self, user_id: UserId, name: str) -> bool:
        """Check if portfolio with name exists for user"""
        doc = await self.collection.find_one({
            "user_id": str(user_id),
            "name": name
        })
        return doc is not None
    
    def _to_document(self, portfolio: PortfolioAggregate) -> Dict[str, Any]:
        """Convert domain entity to MongoDB document"""
        doc = {
            "user_id": str(portfolio.user_id),
            "name": portfolio.name,
            "description": portfolio.description,
            "created_at": portfolio.created_at,
            "updated_at": portfolio.updated_at or portfolio.created_at,
            # Holdings will be calculated from transactions, not stored directly
            "holdings_summary": {
                asset_id: {
                    "asset_id": holding.asset_id,
                    "symbol": holding.symbol,
                    "name": holding.name,
                    "total_quantity": float(holding.total_quantity),
                    "average_cost": float(holding.average_cost),
                    "cost_basis": float(holding.cost_basis)
                }
                for asset_id, holding in portfolio.holdings.items()
                if holding.total_quantity > 0
            }
        }
        
        # Only add _id if portfolio has an existing MongoDB ObjectId
        if hasattr(portfolio, '_mongo_id') and portfolio._mongo_id:
            doc["_id"] = ObjectId(portfolio._mongo_id)
        
        return doc
    
    async def _to_entity(self, doc: Dict[str, Any]) -> PortfolioAggregate:
        """Convert MongoDB document to domain entity"""
        portfolio_id = PortfolioId(str(doc["_id"]))
        
        # Create portfolio aggregate
        entity = PortfolioAggregate(
            id=portfolio_id,
            user_id=UserId(doc["user_id"]),
            name=doc["name"],
            description=doc.get("description"),
            created_at=doc["created_at"],
            updated_at=doc.get("updated_at")
        )
        
        # Load transactions for this portfolio
        transactions = await self.transaction_repository.get_by_portfolio_id(portfolio_id)
        
        # Rebuild holdings from transactions
        for transaction in transactions:
            entity.add_transaction(transaction)
        
        # Store MongoDB ObjectId for future updates
        entity._mongo_id = str(doc["_id"])
        return entity
