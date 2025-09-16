from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from application.use_cases.user_use_cases import UserUseCases
from application.use_cases.crypto_asset_use_cases import CryptoAssetUseCases
from application.use_cases.portfolio_use_cases import PortfolioUseCases
from infrastructure.dependency_injection.container import DIContainer
from database import db_factory


def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    return db_factory.database


def get_di_container() -> DIContainer:
    """Get dependency injection container"""
    from database import db_factory
    return DIContainer(db_factory.database)


def get_user_use_cases(container: DIContainer = Depends(get_di_container)) -> UserUseCases:
    """Get user use cases"""
    return container.user_use_cases


def get_crypto_asset_use_cases(container: DIContainer = Depends(get_di_container)) -> CryptoAssetUseCases:
    """Get crypto asset use cases"""
    return container.crypto_asset_use_cases


def get_portfolio_use_cases(container: DIContainer = Depends(get_di_container)) -> PortfolioUseCases:
    """Get portfolio use cases"""
    return container.portfolio_use_cases
