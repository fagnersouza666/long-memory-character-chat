from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import create_access_token, verify_password, get_password_hash, get_current_user
from app.schemas.token import Token
from app.schemas.user import UserCreate
from app.models.user import User as UserModel
from app.database.session import get_db
from datetime import timedelta, datetime
from app.core.config import settings
from prisma import Prisma

router = APIRouter()

@router.post("/register", response_model=Token)
async def register_user(user: UserCreate, db: Prisma = Depends(get_db)):
    # Verificar se o usuário já existe
    db_user = await db.user.find_unique(where={"username": user.username})
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Verificar se o email já existe
    email_user = await db.user.find_unique(where={"email": user.email})
    if email_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Validar entrada
    if len(user.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long")
    
    if len(user.username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters long")
    
    # Criar novo usuário
    hashed_password = get_password_hash(user.password)
    db_user = await db.user.create(
        data={
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "department": user.department,
            "passwordHash": hashed_password
        }
    )
    
    # Criar token de acesso
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Prisma = Depends(get_db)):
    # Autenticar usuário
    db_user = await db.user.find_unique(where={"username": form_data.username})
    if not db_user or not verify_password(form_data.password, db_user.passwordHash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Atualizar data de último login
    await db.user.update(
        where={"id": db_user.id},
        data={"lastLogin": datetime.now()}
    )
    
    # Criar token de acesso
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/refresh", response_model=Token)
async def refresh_token(current_user: UserModel = Depends(get_current_user)):
    # Criar novo token de acesso
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": current_user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}