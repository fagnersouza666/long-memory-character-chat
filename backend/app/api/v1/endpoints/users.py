from fastapi import APIRouter, Depends, HTTPException
from app.schemas.user import User, UserCreate
from app.models.user import User as UserModel
from app.database.session import get_db
from app.core.security import get_current_user
from prisma import Prisma

router = APIRouter()

@router.get("/me", response_model=User)
async def read_users_me(current_user: UserModel = Depends(get_current_user)):
    return current_user

@router.get("/{user_id}", response_model=User)
async def read_user(user_id: int, db: Prisma = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    # Verificar se o usuário tem permissão para acessar este usuário
    # (apenas administradores podem acessar outros usuários)
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db_user = await db.user.find_unique(where={"id": user_id})
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.get("/", response_model=list[User])
async def read_users(skip: int = 0, limit: int = 100, db: Prisma = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    # Apenas administradores podem listar todos os usuários
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db_users = await db.user.find_many(skip=skip, take=limit)
    return db_users