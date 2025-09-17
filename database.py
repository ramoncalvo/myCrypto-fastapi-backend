from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
from repositories.mongodb import MongoUserRepository, MongoCryptoAssetRepository, MongoPortfolioRepository

class DatabaseFactory:
    """Factory class to create database connections and repositories"""
    
    def __init__(self):
        self.client = None
        self.database = None
        self._user_repo = None
        self._crypto_repo = None
        self._portfolio_repo = None
        self._auth_repo = None
    
    async def connect(self):
        """Connect to the configured database"""
        if settings.database_type == "mongodb":
            await self._connect_mongodb()
        elif settings.database_type == "firebase":
            await self._connect_firebase()
        else:
            raise ValueError(f"Unsupported database type: {settings.database_type}")
    
    async def disconnect(self):
        """Disconnect from database"""
        if settings.database_type == "mongodb" and self.client:
            self.client.close()
        elif settings.database_type == "firebase":
            from database_firebase import firebase_db_factory
            await firebase_db_factory.disconnect()
    
    async def _connect_mongodb(self):
        """Connect to MongoDB"""
        self.client = AsyncIOMotorClient(settings.mongodb_url)
        self.database = self.client[settings.database_name]
        
        # Initialize MongoDB repositories
        from infrastructure.repositories.mongo_auth_repository import MongoAuthRepository
        self._user_repo = MongoUserRepository(self.database)
        self._crypto_repo = MongoCryptoAssetRepository(self.database)
        self._portfolio_repo = MongoPortfolioRepository(self.database)
        self._auth_repo = MongoAuthRepository(self.database)
    
    async def _connect_firebase(self):
        """Connect to Firebase"""
        from database_firebase import firebase_db_factory
        await firebase_db_factory.connect()
        
        # Initialize Firebase repositories
        self._auth_repo = firebase_db_factory.auth_repository
        # TODO: Add other Firebase repositories when implemented
        # self._crypto_repo = firebase_db_factory.crypto_repository
        # self._portfolio_repo = firebase_db_factory.portfolio_repository
    
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
    
    @property
    def auth_repository(self):
        if not self._auth_repo:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._auth_repo

# Global database factory instance
db_factory = DatabaseFactory()
