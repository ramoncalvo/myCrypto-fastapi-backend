import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Environment Configuration
    environment: str = os.getenv("ENVIRONMENT", "development")
    
    # Database Configuration
    database_type: str = os.getenv("DATABASE_TYPE", "mongodb")  # mongodb or firebase
    database_name: str = "mycrypto"
    
    # MongoDB Configuration
    mongodb_url: str = "mongodb://localhost:27017"
    
    # Firebase Configuration
    firebase_project_id: str = os.getenv("FIREBASE_PROJECT_ID", "")
    firebase_credentials_path: str = os.getenv("FIREBASE_CREDENTIALS_PATH", "")
    firebase_credentials_json: str = os.getenv("FIREBASE_CREDENTIALS_JSON", "")
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # JWT Configuration
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    
    # Frontend Configuration
    use_minified_assets: bool = False
    
    def __post_init__(self):
        """Post initialization configuration"""
        # Use minified assets in production
        if self.environment == "production":
            self.use_minified_assets = True
    
    class Config:
        env_file = ".env"

settings = Settings()
# Apply post-init logic
if settings.environment == "production":
    settings.use_minified_assets = True
