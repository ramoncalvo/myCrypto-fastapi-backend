from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from decimal import Decimal
from domain.value_objects.asset_id import AssetId
from domain.value_objects.symbol import Symbol


@dataclass
class CryptoAsset:
    """CryptoAsset domain entity representing a cryptocurrency"""
    
    id: AssetId
    symbol: Symbol
    name: str
    current_price: Optional[Decimal]
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @classmethod
    def create(
        cls,
        symbol: str,
        name: str,
        current_price: Optional[float] = None,
        asset_id: Optional[str] = None
    ) -> 'CryptoAsset':
        """Factory method to create a new crypto asset"""
        return cls(
            id=AssetId(asset_id) if asset_id else AssetId.generate(),
            symbol=Symbol(symbol),
            name=name,
            current_price=Decimal(str(current_price)) if current_price is not None else None,
            created_at=datetime.utcnow()
        )
    
    def update_price(self, new_price: float):
        """Update the current price of the asset"""
        if new_price < 0:
            raise ValueError("Price cannot be negative")
        self.current_price = Decimal(str(new_price))
        self.updated_at = datetime.utcnow()
    
    def update_info(self, name: Optional[str] = None):
        """Update asset information"""
        if name:
            self.name = name
        self.updated_at = datetime.utcnow()
    
    @property
    def price_as_float(self) -> Optional[float]:
        """Get price as float for external APIs"""
        return float(self.current_price) if self.current_price else None
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, CryptoAsset):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        return hash(self.id)
