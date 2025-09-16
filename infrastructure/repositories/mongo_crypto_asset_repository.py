from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from decimal import Decimal

from application.interfaces.repositories import ICryptoAssetRepository
from domain.entities.crypto_asset import CryptoAsset
from domain.value_objects.asset_id import AssetId
from domain.value_objects.symbol import Symbol


class MongoCryptoAssetRepository(ICryptoAssetRepository):
    """MongoDB implementation of crypto asset repository"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database.crypto_assets
    
    async def create(self, asset: CryptoAsset) -> CryptoAsset:
        """Create a new crypto asset"""
        asset_doc = self._to_document(asset)
        result = await self.collection.insert_one(asset_doc)
        asset_doc["_id"] = result.inserted_id
        return self._to_entity(asset_doc)
    
    async def get_by_id(self, asset_id: AssetId) -> Optional[CryptoAsset]:
        """Get asset by ID"""
        try:
            asset_doc = await self.collection.find_one({"_id": ObjectId(str(asset_id))})
            return self._to_entity(asset_doc) if asset_doc else None
        except Exception:
            return None
    
    async def get_by_symbol(self, symbol: Symbol) -> Optional[CryptoAsset]:
        """Get asset by symbol"""
        asset_doc = await self.collection.find_one({"symbol": str(symbol)})
        return self._to_entity(asset_doc) if asset_doc else None
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[CryptoAsset]:
        """Get all assets with pagination"""
        cursor = self.collection.find().skip(skip).limit(limit)
        asset_docs = await cursor.to_list(length=limit)
        return [self._to_entity(doc) for doc in asset_docs]
    
    async def update(self, asset: CryptoAsset) -> CryptoAsset:
        """Update asset"""
        asset_doc = self._to_document(asset)
        asset_doc.pop("_id", None)  # Remove _id from update data
        
        await self.collection.update_one(
            {"_id": ObjectId(str(asset.id))},
            {"$set": asset_doc}
        )
        return asset
    
    async def delete(self, asset_id: AssetId) -> bool:
        """Delete asset"""
        result = await self.collection.delete_one({"_id": ObjectId(str(asset_id))})
        return result.deleted_count > 0
    
    def _to_document(self, asset: CryptoAsset) -> Dict[str, Any]:
        """Convert domain entity to MongoDB document"""
        return {
            "_id": ObjectId(str(asset.id)),
            "symbol": str(asset.symbol),
            "name": asset.name,
            "current_price": float(asset.current_price) if asset.current_price else None,
            "created_at": asset.created_at,
            "updated_at": asset.updated_at
        }
    
    def _to_entity(self, asset_doc: Dict[str, Any]) -> CryptoAsset:
        """Convert MongoDB document to domain entity"""
        current_price = None
        if asset_doc.get("current_price") is not None:
            current_price = Decimal(str(asset_doc["current_price"]))
        
        return CryptoAsset(
            id=AssetId(str(asset_doc["_id"])),
            symbol=Symbol(asset_doc["symbol"]),
            name=asset_doc["name"],
            current_price=current_price,
            created_at=asset_doc["created_at"],
            updated_at=asset_doc.get("updated_at")
        )
