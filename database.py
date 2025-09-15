from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
from repositories.mongodb import MongoDBUserRepository, MongoDBCryptoAssetRepository, MongoDBPortfolioRepository

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
        if settings.database_type == "mongodb":
            await self._connect_mongodb()
        else:
            raise ValueError(f"Unsupported database type: {settings.database_type}")
    
    async def disconnect(self):
        """Disconnect from database"""
        if self.client and settings.database_type == "mongodb":
            self.client.close()
    
    async def _connect_mongodb(self):
        """Connect to MongoDB"""
        self.client = AsyncIOMotorClient(settings.mongodb_url)
        self.database = self.client[settings.database_name]
        
        # Initialize repositories
        self._user_repo = MongoDBUserRepository(self.database)
        self._crypto_repo = MongoDBCryptoAssetRepository(self.database)
        self._portfolio_repo = MongoDBPortfolioRepository(self.database)
    
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
