from dataclasses import dataclass


@dataclass(frozen=True)
class Symbol:
    """Value object for cryptocurrency symbol with validation"""
    
    value: str
    
    def __init__(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Symbol must be a non-empty string")
        
        # Convert to uppercase and validate format
        symbol = value.strip().upper()
        if not symbol.isalnum() or len(symbol) < 2 or len(symbol) > 10:
            raise ValueError("Symbol must be 2-10 alphanumeric characters")
        
        object.__setattr__(self, 'value', symbol)
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Symbol):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        return hash(self.value)
