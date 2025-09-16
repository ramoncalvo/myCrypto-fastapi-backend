from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Email:
    """Value object for email addresses with validation"""
    
    value: str
    
    def __init__(self, value: str):
        if not self._is_valid_email(value):
            raise ValueError(f"Invalid email format: {value}")
        object.__setattr__(self, 'value', value.lower().strip())
    
    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Validate email format using regex"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Email):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        return hash(self.value)
