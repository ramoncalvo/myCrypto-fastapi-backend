import json
import os
from typing import Optional
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1 import AsyncClient

from config import settings
from infrastructure.repositories.firebase_auth_repository import FirebaseAuthRepository


class FirebaseDatabaseFactory:
    """Factory class to create Firebase connections and repositories"""
    
    def __init__(self):
        self.app = None
        self.client: Optional[AsyncClient] = None
        self._auth_repo = None
    
    async def connect(self):
        """Connect to Firebase"""
        try:
            # Initialize Firebase Admin SDK
            if not firebase_admin._apps:
                if settings.firebase_credentials_path and os.path.exists(settings.firebase_credentials_path):
                    # Use service account file
                    cred = credentials.Certificate(settings.firebase_credentials_path)
                elif settings.firebase_credentials_json:
                    # Use service account JSON string (for environment variables)
                    service_account_info = json.loads(settings.firebase_credentials_json)
                    cred = credentials.Certificate(service_account_info)
                else:
                    # Use default credentials (for Google Cloud environments)
                    cred = credentials.ApplicationDefault()
                
                self.app = firebase_admin.initialize_app(cred, {
                    'projectId': settings.firebase_project_id,
                })
            else:
                self.app = firebase_admin.get_app()
            
            # Create async Firestore client
            self.client = firestore.AsyncClient(project=settings.firebase_project_id)
            
            # Initialize repositories
            self._auth_repo = FirebaseAuthRepository(self.client)
            
            print(f"✅ Connected to Firebase project: {settings.firebase_project_id}")
            
        except Exception as e:
            print(f"❌ Failed to connect to Firebase: {str(e)}")
            raise
    
    async def disconnect(self):
        """Disconnect from Firebase"""
        if self.client:
            self.client.close()
        
        if self.app:
            firebase_admin.delete_app(self.app)
    
    @property
    def auth_repository(self):
        if not self._auth_repo:
            raise RuntimeError("Firebase not connected. Call connect() first.")
        return self._auth_repo
    
    @property
    def crypto_repository(self):
        # TODO: Implement Firebase crypto repository
        raise NotImplementedError("Firebase crypto repository not implemented yet")
    
    @property
    def portfolio_repository(self):
        # TODO: Implement Firebase portfolio repository
        raise NotImplementedError("Firebase portfolio repository not implemented yet")


# Global Firebase database factory instance
firebase_db_factory = FirebaseDatabaseFactory()
