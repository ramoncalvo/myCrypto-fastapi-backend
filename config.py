from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database Configuration
    database_type: str = "mongodb"
    database_name: str = "mycrypto"
    
    # MongoDB Configuration
    mongodb_url: str = "mongodb://localhost:27017"
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    class Config:
        env_file = ".env"

settings = Settings()
