from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from domain.value_objects.email import Email
from domain.value_objects.user_id import UserId


@dataclass
class User:
    """User domain entity representing a user in the system"""
    
    id: UserId
    email: Email
    name: str
    password_hash: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @classmethod
    def create(
        cls,
        email: str,
        name: str,
        password_hash: str,
        user_id: Optional[str] = None
    ) -> 'User':
        """Factory method to create a new user"""
        return cls(
            id=UserId(user_id) if user_id else UserId.generate(),
            email=Email(email),
            name=name,
            password_hash=password_hash,
            created_at=datetime.utcnow()
        )
    
    def update_profile(self, name: Optional[str] = None, email: Optional[str] = None):
        """Update user profile information"""
        if name:
            self.name = name
        if email:
            self.email = Email(email)
        self.updated_at = datetime.utcnow()
    
    def change_password(self, new_password_hash: str):
        """Change user password"""
        self.password_hash = new_password_hash
        self.updated_at = datetime.utcnow()
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, User):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        return hash(self.id)
