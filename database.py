from motor.motor_asyncio import AsyncIOMotorClient
from config import settings, DatabaseType
from repositories.mongodb import MongoUserRepository, MongoCryptoAssetRepository, MongoPortfolioRepository
from repositories.firestore import FirestoreUserRepository, FirestoreCryptoAssetRepository, FirestorePortfolioRepository

class DatabaseFactory:
    """Factory class to create database connections and repositories"""
    
    def __init__(self):
        self.client = None
        self.database = None
        self._user_repo = None
        self._crypto_repo = None
        self._portfolio_repo = None
    
    async def connect(self):
        """Connect to the configured database"""
        if settings.database_type == DatabaseType.MONGODB:
            await self._connect_mongodb()
        elif settings.database_type == DatabaseType.FIRESTORE:
            await self._connect_firestore()
        else:
            raise ValueError(f"Unsupported database type: {settings.database_type}")
    
    async def disconnect(self):
        """Disconnect from database"""
        if self.client and settings.database_type == DatabaseType.MONGODB:
            self.client.close()
    
    async def _connect_mongodb(self):
        """Connect to MongoDB"""
        self.client = AsyncIOMotorClient(settings.mongodb_url)
        self.database = self.client[settings.database_name]
        
        # Initialize repositories
        self._user_repo = MongoUserRepository(self.database)
        self._crypto_repo = MongoCryptoAssetRepository(self.database)
        self._portfolio_repo = MongoPortfolioRepository(self.database)
    
    async def _connect_firestore(self):
        """Connect to Firestore"""
        try:
            import firebase_admin
            from firebase_admin import credentials, firestore
            
            if not firebase_admin._apps:
                cred = credentials.Certificate(settings.firebase_credentials_path)
                firebase_admin.initialize_app(cred, {
                    'projectId': settings.firebase_project_id,
                })
            
            self.database = firestore.client()
            
            # Initialize repositories
            self._user_repo = FirestoreUserRepository(self.database)
            self._crypto_repo = FirestoreCryptoAssetRepository(self.database)
            self._portfolio_repo = FirestorePortfolioRepository(self.database)
            
        except ImportError:
            raise ImportError("Firebase dependencies not installed. Run: pip install firebase-admin")
    
    @property
    def user_repository(self):
        if not self._user_repo:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._user_repo
    
    @property
    def crypto_repository(self):
        if not self._crypto_repo:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._crypto_repo
    
    @property
    def portfolio_repository(self):
        if not self._portfolio_repo:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._portfolio_repo

# Global database factory instance
db_factory = DatabaseFactory()
