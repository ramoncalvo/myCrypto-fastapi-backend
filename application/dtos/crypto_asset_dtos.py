from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from domain.entities.crypto_asset import CryptoAsset


@dataclass
class CreateCryptoAssetRequest:
    """DTO for creating a new crypto asset"""
    symbol: str
    name: str
    current_price: Optional[float] = None


@dataclass
class UpdateCryptoAssetRequest:
    """DTO for updating crypto asset information"""
    name: Optional[str] = None
    current_price: Optional[float] = None


@dataclass
class CryptoAssetResponse:
    """DTO for crypto asset response"""
    id: str
    symbol: str
    name: str
    current_price: Optional[float]
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @classmethod
    def from_entity(cls, asset: CryptoAsset) -> 'CryptoAssetResponse':
        """Create DTO from domain entity"""
        return cls(
            id=str(asset.id),
            symbol=str(asset.symbol),
            name=asset.name,
            current_price=asset.price_as_float,
            created_at=asset.created_at,
            updated_at=asset.updated_at
        )
