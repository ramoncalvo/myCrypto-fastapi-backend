from datetime import datetime
from typing import Optional
from domain.value_objects.user_id import UserId
from domain.value_objects.email import Email


class AuthUser:
    """Authentication domain entity with security-focused behavior"""
    
    def __init__(
        self,
        id: UserId,
        email: Email,
        name: str,
        password_hash: str,
        created_at: datetime,
        updated_at: Optional[datetime] = None,
        is_verified: bool = False,
        last_login: Optional[datetime] = None,
        failed_login_attempts: int = 0,
        locked_until: Optional[datetime] = None
    ):
        self.id = id
        self.email = email
        self.name = name
        self.password_hash = password_hash
        self.created_at = created_at
        self.updated_at = updated_at
        self.is_verified = is_verified
        self.last_login = last_login
        self.failed_login_attempts = failed_login_attempts
        self.locked_until = locked_until
    
    @classmethod
    def create(
        cls,
        email: str,
        name: str,
        password_hash: str
    ) -> 'AuthUser':
        """Create a new auth user"""
        return cls(
            id=UserId.generate(),
            email=Email(email),
            name=name,
            password_hash=password_hash,
            created_at=datetime.utcnow(),
            is_verified=False,
            failed_login_attempts=0
        )
    
    def update_profile(self, name: Optional[str] = None) -> None:
        """Update user profile information"""
        if name is not None:
            self.name = name
        self.updated_at = datetime.utcnow()
    
    def verify_account(self) -> None:
        """Mark account as verified"""
        self.is_verified = True
        self.updated_at = datetime.utcnow()
    
    def record_successful_login(self) -> None:
        """Record successful login"""
        self.last_login = datetime.utcnow()
        self.failed_login_attempts = 0
        self.locked_until = None
        self.updated_at = datetime.utcnow()
    
    def record_failed_login(self) -> None:
        """Record failed login attempt"""
        self.failed_login_attempts += 1
        self.updated_at = datetime.utcnow()
        
        # Lock account after 5 failed attempts for 30 minutes
        if self.failed_login_attempts >= 5:
            from datetime import timedelta
            self.locked_until = datetime.utcnow() + timedelta(minutes=30)
    
    def is_account_locked(self) -> bool:
        """Check if account is currently locked"""
        if self.locked_until is None:
            return False
        return datetime.utcnow() < self.locked_until
    
    def unlock_account(self) -> None:
        """Manually unlock account"""
        self.locked_until = None
        self.failed_login_attempts = 0
        self.updated_at = datetime.utcnow()
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, AuthUser):
            return False
        return self.id == other.id
    
    def __str__(self) -> str:
        return f"AuthUser(id={self.id}, email={self.email}, name={self.name})"
