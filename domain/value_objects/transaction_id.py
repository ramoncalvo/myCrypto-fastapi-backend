from dataclasses import dataclass
import uuid


@dataclass(frozen=True)
class TransactionId:
    """Value object for transaction ID"""
    
    value: str
    
    def __init__(self, value: str):
        if not value or not isinstance(value, str):
            raise ValueError("Transaction ID must be a non-empty string")
        object.__setattr__(self, 'value', value)
    
    @classmethod
    def generate(cls) -> 'TransactionId':
        """Generate a new transaction ID"""
        return cls(str(uuid.uuid4()))
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, TransactionId):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        return hash(self.value)
