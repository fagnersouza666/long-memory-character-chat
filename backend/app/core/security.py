from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings
from app.models.user import User as UserModel
from app.schemas.token import TokenData
from app.database.session import get_db
from prisma import Prisma

# Configurar o contexto de criptografia de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configurar o esquema OAuth2 para obtenção do token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

def verify_password(plain_password, hashed_password):
    """Verificar se a senha fornecida corresponde ao hash armazenado"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        # Log de erro para depuração
        print(f"Erro ao verificar senha: {e}")
        return False

def get_password_hash(password):
    """Gerar hash da senha"""
    try:
        return pwd_context.hash(password)
    except Exception as e:
        # Log de erro para depuração
        print(f"Erro ao gerar hash da senha: {e}")
        raise HTTPException(status_code=500, detail="Error processing password")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Criar token de acesso JWT"""
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    except Exception as e:
        # Log de erro para depuração
        print(f"Erro ao criar token de acesso: {e}")
        raise HTTPException(status_code=500, detail="Error creating access token")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Prisma = Depends(get_db)):
    """Obter o usuário atual a partir do token JWT"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    except Exception as e:
        # Log de erro para depuração
        print(f"Erro ao decodificar token: {e}")
        raise credentials_exception
    
    try:
        user = await db.user.find_unique(where={"username": token_data.username})
        if user is None:
            raise credentials_exception
        return user
    except Exception as e:
        # Log de erro para depuração
        print(f"Erro ao buscar usuário: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving user")