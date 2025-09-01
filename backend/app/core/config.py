import os
from typing import Optional

class Settings:
    # Configurações do banco de dados
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/rag_enterprise")
    
    # Configurações JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "chave_secreta_forte_para_jwt")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Configurações do administrador
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin123")

settings = Settings()