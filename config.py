import os
from dotenv import load_dotenv
from enum import Enum

load_dotenv()

class DatabaseType(str, Enum):
    MONGODB = "mongodb"
    FIRESTORE = "firestore"
    FIREBASE = "firebase"

class Settings:
    # Database configuration
    database_type: DatabaseType = DatabaseType(os.getenv("DATABASE_TYPE", "mongodb"))
    database_name: str = os.getenv("DATABASE_NAME", "mycrypto")
    
    # MongoDB configuration
    mongodb_url: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017/mycrypto")
    
    # Firebase/Firestore configuration
    firebase_credentials_path: str = os.getenv("FIREBASE_CREDENTIALS_PATH", "")
    firebase_project_id: str = os.getenv("FIREBASE_PROJECT_ID", "")
    
    class Config:
        env_file = ".env"

settings = Settings()
