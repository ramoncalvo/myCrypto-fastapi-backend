import re
import bcrypt
from typing import Union


class Password:
    """Password value object with validation and hashing"""
    
    def __init__(self, value: str, is_hashed: bool = False):
        if is_hashed:
            self._hashed_value = value
        else:
            self._validate_password(value)
            self._hashed_value = self._hash_password(value)
    
    @staticmethod
    def _validate_password(password: str) -> None:
        """Validate password strength"""
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        if len(password) > 128:
            raise ValueError("Password must be less than 128 characters")
        
        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', password):
            raise ValueError("Password must contain at least one uppercase letter")
        
        # Check for at least one lowercase letter
        if not re.search(r'[a-z]', password):
            raise ValueError("Password must contain at least one lowercase letter")
        
        # Check for at least one digit
        if not re.search(r'\d', password):
            raise ValueError("Password must contain at least one digit")
        
        # Check for at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValueError("Password must contain at least one special character")
    
    @staticmethod
    def _hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @classmethod
    def from_hash(cls, hashed_password: str) -> 'Password':
        """Create Password object from existing hash"""
        return cls(hashed_password, is_hashed=True)
    
    def verify(self, plain_password: str) -> bool:
        """Verify plain password against hash"""
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            self._hashed_value.encode('utf-8')
        )
    
    @property
    def hash(self) -> str:
        """Get the hashed password"""
        return self._hashed_value
    
    def __str__(self) -> str:
        return "[PROTECTED]"
    
    def __repr__(self) -> str:
        return "Password([PROTECTED])"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Password):
            return False
        return self._hashed_value == other._hashed_value
