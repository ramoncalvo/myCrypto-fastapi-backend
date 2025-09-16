from dataclasses import dataclass
from typing import Union
import uuid


@dataclass(frozen=True)
class PortfolioId:
    """Value object for Portfolio ID"""
    
    value: str
    
    def __init__(self, value: Union[str, None] = None):
        if value is None:
            object.__setattr__(self, 'value', str(uuid.uuid4()))
        else:
            if not isinstance(value, str) or not value.strip():
                raise ValueError("Portfolio ID must be a non-empty string")
            object.__setattr__(self, 'value', value)
    
    @classmethod
    def generate(cls) -> 'PortfolioId':
        """Generate a new unique portfolio ID"""
        return cls()
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, PortfolioId):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        return hash(self.value)
