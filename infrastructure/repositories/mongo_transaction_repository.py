from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from application.interfaces.transaction_repository import TransactionRepository
from domain.entities.transaction import Transaction, TransactionType, TransactionStatus
from domain.value_objects.transaction_id import TransactionId
from domain.value_objects.user_id import UserId
from domain.value_objects.portfolio_id import PortfolioId
from domain.value_objects.asset_id import AssetId


class MongoTransactionRepository(TransactionRepository):
    """MongoDB implementation of transaction repository"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database.transactions
    
    async def create(self, transaction: Transaction) -> Transaction:
        """Create a new transaction"""
        transaction_doc = self._to_document(transaction)
        result = await self.collection.insert_one(transaction_doc)
        
        # Get the created document
        created_doc = await self.collection.find_one({"_id": result.inserted_id})
        return self._to_entity(created_doc)
    
    async def get_by_id(self, transaction_id: TransactionId) -> Optional[Transaction]:
        """Get transaction by ID"""
        try:
            doc = await self.collection.find_one({"_id": ObjectId(str(transaction_id))})
            return self._to_entity(doc) if doc else None
        except Exception:
            return None
    
    async def get_by_user_id(
        self, 
        user_id: UserId, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Transaction]:
        """Get all transactions for a user"""
        cursor = self.collection.find({"user_id": str(user_id)}).skip(skip).limit(limit).sort("created_at", -1)
        docs = await cursor.to_list(length=limit)
        return [self._to_entity(doc) for doc in docs]
    
    async def get_by_portfolio_id(
        self, 
        portfolio_id: PortfolioId, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Transaction]:
        """Get all transactions for a portfolio"""
        cursor = self.collection.find({"portfolio_id": str(portfolio_id)}).skip(skip).limit(limit).sort("created_at", -1)
        docs = await cursor.to_list(length=limit)
        return [self._to_entity(doc) for doc in docs]
    
    async def get_by_asset_id(
        self, 
        asset_id: AssetId, 
        user_id: Optional[UserId] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Transaction]:
        """Get all transactions for an asset, optionally filtered by user"""
        query = {"asset_id": str(asset_id)}
        if user_id:
            query["user_id"] = str(user_id)
        
        cursor = self.collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
        docs = await cursor.to_list(length=limit)
        return [self._to_entity(doc) for doc in docs]
    
    async def get_by_type(
        self, 
        transaction_type: TransactionType,
        user_id: Optional[UserId] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Transaction]:
        """Get transactions by type, optionally filtered by user"""
        query = {"transaction_type": transaction_type.value}
        if user_id:
            query["user_id"] = str(user_id)
        
        cursor = self.collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
        docs = await cursor.to_list(length=limit)
        return [self._to_entity(doc) for doc in docs]
    
    async def get_by_status(
        self, 
        status: TransactionStatus,
        user_id: Optional[UserId] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Transaction]:
        """Get transactions by status, optionally filtered by user"""
        query = {"status": status.value}
        if user_id:
            query["user_id"] = str(user_id)
        
        cursor = self.collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
        docs = await cursor.to_list(length=limit)
        return [self._to_entity(doc) for doc in docs]
    
    async def get_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        user_id: Optional[UserId] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Transaction]:
        """Get transactions within date range"""
        query = {
            "created_at": {
                "$gte": start_date,
                "$lte": end_date
            }
        }
        if user_id:
            query["user_id"] = str(user_id)
        
        cursor = self.collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
        docs = await cursor.to_list(length=limit)
        return [self._to_entity(doc) for doc in docs]
    
    async def update(self, transaction: Transaction) -> Transaction:
        """Update transaction"""
        transaction_doc = self._to_document(transaction)
        transaction_doc.pop("_id", None)  # Remove _id for update
        
        # Store MongoDB ObjectId for updates
        mongo_id = getattr(transaction, '_mongo_id', None)
        if mongo_id:
            object_id = ObjectId(mongo_id)
        else:
            object_id = ObjectId(str(transaction.id))
        
        await self.collection.update_one(
            {"_id": object_id},
            {"$set": transaction_doc}
        )
        
        # Return updated transaction
        updated_doc = await self.collection.find_one({"_id": object_id})
        return self._to_entity(updated_doc)
    
    async def delete(self, transaction_id: TransactionId) -> bool:
        """Delete transaction"""
        result = await self.collection.delete_one({"_id": ObjectId(str(transaction_id))})
        return result.deleted_count > 0
    
    async def get_user_transaction_stats(self, user_id: UserId) -> dict:
        """Get transaction statistics for a user"""
        pipeline = [
            {"$match": {"user_id": str(user_id)}},
            {"$group": {
                "_id": None,
                "total_transactions": {"$sum": 1},
                "completed_transactions": {
                    "$sum": {"$cond": [{"$eq": ["$status", "completed"]}, 1, 0]}
                },
                "buy_transactions": {
                    "$sum": {"$cond": [{"$eq": ["$transaction_type", "buy"]}, 1, 0]}
                },
                "sell_transactions": {
                    "$sum": {"$cond": [{"$eq": ["$transaction_type", "sell"]}, 1, 0]}
                },
                "total_fees": {"$sum": "$fees"},
                "total_buy_amount": {
                    "$sum": {"$cond": [{"$eq": ["$transaction_type", "buy"]}, "$total_amount", 0]}
                },
                "total_sell_amount": {
                    "$sum": {"$cond": [{"$eq": ["$transaction_type", "sell"]}, "$total_amount", 0]}
                }
            }}
        ]
        
        result = await self.collection.aggregate(pipeline).to_list(length=1)
        if result:
            stats = result[0]
            stats.pop("_id", None)
            return stats
        
        return {
            "total_transactions": 0,
            "completed_transactions": 0,
            "buy_transactions": 0,
            "sell_transactions": 0,
            "total_fees": 0,
            "total_buy_amount": 0,
            "total_sell_amount": 0
        }
    
    def _to_document(self, transaction: Transaction) -> Dict[str, Any]:
        """Convert domain entity to MongoDB document"""
        doc = {
            "user_id": str(transaction.user_id),
            "portfolio_id": str(transaction.portfolio_id),
            "asset_id": str(transaction.asset_id),
            "transaction_type": transaction.transaction_type.value,
            "quantity": float(transaction.quantity),
            "price": float(transaction.price),
            "total_amount": float(transaction.total_amount),
            "fees": float(transaction.fees),
            "status": transaction.status.value,
            "created_at": transaction.created_at,
            "executed_at": transaction.executed_at,
            "updated_at": transaction.updated_at or transaction.created_at,
            "notes": transaction.notes
        }
        
        # Only add _id if transaction has an existing MongoDB ObjectId
        if hasattr(transaction, '_mongo_id') and transaction._mongo_id:
            doc["_id"] = ObjectId(transaction._mongo_id)
        
        return doc
    
    def _to_entity(self, doc: Dict[str, Any]) -> Transaction:
        """Convert MongoDB document to domain entity"""
        entity = Transaction(
            id=TransactionId(str(doc["_id"])),
            user_id=UserId(doc["user_id"]),
            portfolio_id=PortfolioId(doc["portfolio_id"]),
            asset_id=AssetId(doc["asset_id"]),
            transaction_type=TransactionType(doc["transaction_type"]),
            quantity=doc["quantity"],
            price=doc["price"],
            total_amount=doc["total_amount"],
            fees=doc["fees"],
            status=TransactionStatus(doc["status"]),
            created_at=doc["created_at"],
            executed_at=doc.get("executed_at"),
            updated_at=doc.get("updated_at"),
            notes=doc.get("notes")
        )
        
        # Store MongoDB ObjectId for future updates
        entity._mongo_id = str(doc["_id"])
        return entity
