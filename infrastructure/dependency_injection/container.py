from motor.motor_asyncio import AsyncIOMotorDatabase
from application.interfaces.repositories import IUserRepository, ICryptoAssetRepository, IPortfolioRepository
from application.interfaces.auth_repository import AuthRepository
from application.interfaces.transaction_repository import TransactionRepository
from application.interfaces.portfolio_aggregate_repository import PortfolioAggregateRepository
from application.use_cases.user_use_cases import UserUseCases
from application.use_cases.crypto_asset_use_cases import CryptoAssetUseCases
from application.use_cases.portfolio_use_cases import PortfolioUseCases
from application.use_cases.auth_use_cases import AuthUseCases
from application.use_cases.transaction_use_cases import TransactionUseCases
from application.use_cases.portfolio_aggregate_use_cases import PortfolioAggregateUseCases
from infrastructure.repositories.mongo_user_repository import MongoUserRepository
from infrastructure.repositories.mongo_crypto_asset_repository import MongoCryptoAssetRepository
from infrastructure.repositories.mongo_portfolio_repository import MongoPortfolioRepository
from infrastructure.repositories.mongo_auth_repository import MongoAuthRepository
from infrastructure.repositories.mongo_transaction_repository import MongoTransactionRepository
from infrastructure.repositories.mongo_portfolio_aggregate_repository import MongoPortfolioAggregateRepository


class DIContainer:
    """Dependency Injection Container"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self._database = database
        self._user_repository = None
        self._crypto_asset_repository = None
        self._portfolio_repository = None
        self._auth_repository = None
        self._transaction_repository = None
        self._portfolio_aggregate_repository = None
        self._user_use_cases = None
        self._crypto_asset_use_cases = None
        self._portfolio_use_cases = None
        self._auth_use_cases = None
        self._transaction_use_cases = None
        self._portfolio_aggregate_use_cases = None
        self._setup_dependencies()
    
    def _setup_dependencies(self):
        """Setup all dependencies"""
        # Repositories
        self._user_repository = MongoUserRepository(self._database)
        self._crypto_asset_repository = MongoCryptoAssetRepository(self._database)
        self._portfolio_repository = MongoPortfolioRepository(self._database)
        self._auth_repository = MongoAuthRepository(self._database)
        self._transaction_repository = MongoTransactionRepository(self._database)
        self._portfolio_aggregate_repository = MongoPortfolioAggregateRepository(
            self._database, 
            self._transaction_repository
        )
        
        # Use Cases
        self._user_use_cases = UserUseCases(self._user_repository)
        self._crypto_asset_use_cases = CryptoAssetUseCases(self._crypto_asset_repository)
        self._portfolio_use_cases = PortfolioUseCases(
            self._portfolio_repository,
            self._user_repository,
            self._crypto_asset_repository
        )
        self._auth_use_cases = AuthUseCases(self._auth_repository)
        self._transaction_use_cases = TransactionUseCases(
            self._transaction_repository,
            self._portfolio_aggregate_repository,
            self._crypto_asset_repository
        )
        self._portfolio_aggregate_use_cases = PortfolioAggregateUseCases(
            self._portfolio_aggregate_repository,
            self._crypto_asset_repository
        )
    
    # Repository getters
    def user_repository(self) -> IUserRepository:
        return self._user_repository
    
    def crypto_asset_repository(self) -> ICryptoAssetRepository:
        return self._crypto_asset_repository
    
    def portfolio_repository(self) -> IPortfolioRepository:
        return self._portfolio_repository
    
    def auth_repository(self) -> AuthRepository:
        return self._auth_repository
    
    def transaction_repository(self) -> TransactionRepository:
        return self._transaction_repository
    
    def portfolio_aggregate_repository(self) -> PortfolioAggregateRepository:
        return self._portfolio_aggregate_repository
    
    # Use case getters
    @property
    def user_use_cases(self) -> UserUseCases:
        return self._user_use_cases
    
    @property
    def crypto_asset_use_cases(self) -> CryptoAssetUseCases:
        return self._crypto_asset_use_cases
    
    @property
    def portfolio_use_cases(self) -> PortfolioUseCases:
        return self._portfolio_use_cases
    
    @property
    def auth_use_cases(self) -> AuthUseCases:
        return self._auth_use_cases
    
    @property
    def transaction_use_cases(self) -> TransactionUseCases:
        return self._transaction_use_cases
    
    @property
    def portfolio_aggregate_use_cases(self) -> PortfolioAggregateUseCases:
        return self._portfolio_aggregate_use_cases
