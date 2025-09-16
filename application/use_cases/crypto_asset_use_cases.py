from typing import List, Optional
from application.interfaces.repositories import ICryptoAssetRepository
from domain.entities.crypto_asset import CryptoAsset
from domain.value_objects.asset_id import AssetId
from domain.value_objects.symbol import Symbol
from application.dtos.crypto_asset_dtos import CreateCryptoAssetRequest, UpdateCryptoAssetRequest, CryptoAssetResponse


class CryptoAssetUseCases:
    """Use cases for crypto asset management"""
    
    def __init__(self, crypto_asset_repository: ICryptoAssetRepository):
        self._crypto_asset_repository = crypto_asset_repository
    
    async def create_crypto_asset(self, request: CreateCryptoAssetRequest) -> CryptoAssetResponse:
        """Create a new crypto asset"""
        # Check if asset with symbol already exists
        existing_asset = await self._crypto_asset_repository.get_by_symbol(Symbol(request.symbol))
        if existing_asset:
            raise ValueError(f"Asset with symbol {request.symbol} already exists")
        
        # Create domain entity
        asset = CryptoAsset.create(
            symbol=request.symbol,
            name=request.name,
            current_price=request.current_price
        )
        
        # Save to repository
        created_asset = await self._crypto_asset_repository.create(asset)
        
        # Return DTO
        return CryptoAssetResponse.from_entity(created_asset)
    
    async def get_asset_by_id(self, asset_id: str) -> Optional[CryptoAssetResponse]:
        """Get asset by ID"""
        asset = await self._crypto_asset_repository.get_by_id(AssetId(asset_id))
        return CryptoAssetResponse.from_entity(asset) if asset else None
    
    async def get_asset_by_symbol(self, symbol: str) -> Optional[CryptoAssetResponse]:
        """Get asset by symbol"""
        asset = await self._crypto_asset_repository.get_by_symbol(Symbol(symbol))
        return CryptoAssetResponse.from_entity(asset) if asset else None
    
    async def get_all_assets(self, skip: int = 0, limit: int = 100) -> List[CryptoAssetResponse]:
        """Get all assets with pagination"""
        assets = await self._crypto_asset_repository.get_all(skip=skip, limit=limit)
        return [CryptoAssetResponse.from_entity(asset) for asset in assets]
    
    async def update_asset(self, asset_id: str, request: UpdateCryptoAssetRequest) -> Optional[CryptoAssetResponse]:
        """Update asset"""
        asset = await self._crypto_asset_repository.get_by_id(AssetId(asset_id))
        if not asset:
            return None
        
        # Update domain entity
        if request.current_price is not None:
            asset.update_price(request.current_price)
        
        if request.name:
            asset.update_info(name=request.name)
        
        # Save to repository
        updated_asset = await self._crypto_asset_repository.update(asset)
        
        # Return DTO
        return CryptoAssetResponse.from_entity(updated_asset)
    
    async def delete_asset(self, asset_id: str) -> bool:
        """Delete asset"""
        return await self._crypto_asset_repository.delete(AssetId(asset_id))
