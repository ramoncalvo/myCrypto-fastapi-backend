from dataclasses import dataclass
from typing import Union
import uuid


@dataclass(frozen=True)
class UserId:
    """Value object for User ID"""
    
    value: str
    
    def __init__(self, value: Union[str, None] = None):
        if value is None:
            object.__setattr__(self, 'value', str(uuid.uuid4()))
        else:
            if not isinstance(value, str) or not value.strip():
                raise ValueError("User ID must be a non-empty string")
            object.__setattr__(self, 'value', value)
    
    @classmethod
    def generate(cls) -> 'UserId':
        """Generate a new unique user ID"""
        return cls()
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, UserId):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        return hash(self.value)
