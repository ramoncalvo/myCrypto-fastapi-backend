from motor.motor_asyncio import AsyncIOMotorDatabase
from application.interfaces.repositories import IUserRepository, ICryptoAssetRepository, IPortfolioRepository
from application.use_cases.user_use_cases import UserUseCases
from application.use_cases.crypto_asset_use_cases import CryptoAssetUseCases
from application.use_cases.portfolio_use_cases import PortfolioUseCases
from infrastructure.repositories.mongo_user_repository import MongoUserRepository
from infrastructure.repositories.mongo_crypto_asset_repository import MongoCryptoAssetRepository
from infrastructure.repositories.mongo_portfolio_repository import MongoPortfolioRepository


class DIContainer:
    """Dependency Injection Container for clean architecture"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self._database = database
        self._repositories = {}
        self._use_cases = {}
        self._setup_dependencies()
    
    def _setup_dependencies(self):
        """Setup all dependencies"""
        # Repositories
        self._repositories['user'] = MongoUserRepository(self._database)
        self._repositories['crypto_asset'] = MongoCryptoAssetRepository(self._database)
        self._repositories['portfolio'] = MongoPortfolioRepository(self._database)
        
        # Use Cases
        self._use_cases['user'] = UserUseCases(self._repositories['user'])
        self._use_cases['crypto_asset'] = CryptoAssetUseCases(self._repositories['crypto_asset'])
        self._use_cases['portfolio'] = PortfolioUseCases(
            self._repositories['portfolio'],
            self._repositories['user'],
            self._repositories['crypto_asset']
        )
    
    # Repository getters
    @property
    def user_repository(self) -> IUserRepository:
        return self._repositories['user']
    
    @property
    def crypto_asset_repository(self) -> ICryptoAssetRepository:
        return self._repositories['crypto_asset']
    
    @property
    def portfolio_repository(self) -> IPortfolioRepository:
        return self._repositories['portfolio']
    
    # Use case getters
    @property
    def user_use_cases(self) -> UserUseCases:
        return self._use_cases['user']
    
    @property
    def crypto_asset_use_cases(self) -> CryptoAssetUseCases:
        return self._use_cases['crypto_asset']
    
    @property
    def portfolio_use_cases(self) -> PortfolioUseCases:
        return self._use_cases['portfolio']
