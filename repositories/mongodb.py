from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime

from repositories.base import UserRepository, CryptoAssetRepository, PortfolioRepository
from models import User, CryptoAsset, Portfolio, UserResponse, CryptoAssetResponse, PortfolioResponse

class MongoUserRepository(UserRepository[UserResponse]):
    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database.users
    
    async def create(self, data: Dict[str, Any]) -> UserResponse:
        data['created_at'] = datetime.utcnow()
        result = await self.collection.insert_one(data)
        created_user = await self.collection.find_one({"_id": result.inserted_id})
        return self._to_response(created_user)
    
    async def get_by_id(self, id: str) -> Optional[UserResponse]:
        user = await self.collection.find_one({"_id": ObjectId(id)})
        return self._to_response(user) if user else None
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        cursor = self.collection.find().skip(skip).limit(limit)
        users = await cursor.to_list(length=limit)
        return [self._to_response(user) for user in users]
    
    async def update(self, id: str, data: Dict[str, Any]) -> Optional[UserResponse]:
        # Remove None values
        update_data = {k: v for k, v in data.items() if v is not None}
        if not update_data:
            return await self.get_by_id(id)
        
        result = await self.collection.update_one(
            {"_id": ObjectId(id)}, 
            {"$set": update_data}
        )
        if result.modified_count:
            return await self.get_by_id(id)
        return None
    
    async def delete(self, id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0
    
    async def find_by_field(self, field: str, value: Any) -> List[UserResponse]:
        cursor = self.collection.find({field: value})
        users = await cursor.to_list(length=None)
        return [self._to_response(user) for user in users]
    
    async def get_by_email(self, email: str) -> Optional[UserResponse]:
        user = await self.collection.find_one({"email": email})
        return self._to_response(user) if user else None
    
    def _to_response(self, user_doc: Dict) -> UserResponse:
        if not user_doc:
            return None
        return UserResponse(
            id=str(user_doc["_id"]),
            email=user_doc["email"],
            name=user_doc["name"],
            created_at=user_doc["created_at"]
        )

class MongoCryptoAssetRepository(CryptoAssetRepository[CryptoAssetResponse]):
    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database.crypto_assets
    
    async def create(self, data: Dict[str, Any]) -> CryptoAssetResponse:
        data['created_at'] = datetime.utcnow()
        result = await self.collection.insert_one(data)
        created_asset = await self.collection.find_one({"_id": result.inserted_id})
        return self._to_response(created_asset)
    
    async def get_by_id(self, id: str) -> Optional[CryptoAssetResponse]:
        asset = await self.collection.find_one({"_id": ObjectId(id)})
        return self._to_response(asset) if asset else None
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[CryptoAssetResponse]:
        cursor = self.collection.find().skip(skip).limit(limit)
        assets = await cursor.to_list(length=limit)
        return [self._to_response(asset) for asset in assets]
    
    async def update(self, id: str, data: Dict[str, Any]) -> Optional[CryptoAssetResponse]:
        update_data = {k: v for k, v in data.items() if v is not None}
        if not update_data:
            return await self.get_by_id(id)
        
        result = await self.collection.update_one(
            {"_id": ObjectId(id)}, 
            {"$set": update_data}
        )
        if result.modified_count:
            return await self.get_by_id(id)
        return None
    
    async def delete(self, id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0
    
    async def find_by_field(self, field: str, value: Any) -> List[CryptoAssetResponse]:
        cursor = self.collection.find({field: value})
        assets = await cursor.to_list(length=None)
        return [self._to_response(asset) for asset in assets]
    
    async def get_by_symbol(self, symbol: str) -> Optional[CryptoAssetResponse]:
        asset = await self.collection.find_one({"symbol": symbol})
        return self._to_response(asset) if asset else None
    
    def _to_response(self, asset_doc: Dict) -> CryptoAssetResponse:
        if not asset_doc:
            return None
        return CryptoAssetResponse(
            id=str(asset_doc["_id"]),
            symbol=asset_doc["symbol"],
            name=asset_doc["name"],
            current_price=asset_doc.get("current_price"),
            created_at=asset_doc["created_at"]
        )

class MongoPortfolioRepository(PortfolioRepository[PortfolioResponse]):
    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database.portfolio
    
    async def create(self, data: Dict[str, Any]) -> PortfolioResponse:
        data['created_at'] = datetime.utcnow()
        result = await self.collection.insert_one(data)
        created_portfolio = await self.collection.find_one({"_id": result.inserted_id})
        return self._to_response(created_portfolio)
    
    async def get_by_id(self, id: str) -> Optional[PortfolioResponse]:
        portfolio = await self.collection.find_one({"_id": ObjectId(id)})
        return self._to_response(portfolio) if portfolio else None
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[PortfolioResponse]:
        cursor = self.collection.find().skip(skip).limit(limit)
        portfolios = await cursor.to_list(length=limit)
        return [self._to_response(portfolio) for portfolio in portfolios]
    
    async def update(self, id: str, data: Dict[str, Any]) -> Optional[PortfolioResponse]:
        update_data = {k: v for k, v in data.items() if v is not None}
        if not update_data:
            return await self.get_by_id(id)
        
        result = await self.collection.update_one(
            {"_id": ObjectId(id)}, 
            {"$set": update_data}
        )
        if result.modified_count:
            return await self.get_by_id(id)
        return None
    
    async def delete(self, id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0
    
    async def find_by_field(self, field: str, value: Any) -> List[PortfolioResponse]:
        cursor = self.collection.find({field: value})
        portfolios = await cursor.to_list(length=None)
        return [self._to_response(portfolio) for portfolio in portfolios]
    
    async def get_by_user_id(self, user_id: str) -> List[PortfolioResponse]:
        cursor = self.collection.find({"user_id": user_id})
        portfolios = await cursor.to_list(length=None)
        return [self._to_response(portfolio) for portfolio in portfolios]
    
    async def get_by_user_and_asset(self, user_id: str, asset_id: str) -> Optional[PortfolioResponse]:
        portfolio = await self.collection.find_one({"user_id": user_id, "asset_id": asset_id})
        return self._to_response(portfolio) if portfolio else None
    
    def _to_response(self, portfolio_doc: Dict) -> PortfolioResponse:
        if not portfolio_doc:
            return None
        return PortfolioResponse(
            id=str(portfolio_doc["_id"]),
            user_id=portfolio_doc["user_id"],
            asset_id=portfolio_doc["asset_id"],
            quantity=portfolio_doc["quantity"],
            purchase_price=portfolio_doc["purchase_price"],
            created_at=portfolio_doc["created_at"]
        )
