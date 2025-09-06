from fastapi import APIRouter, Depends, HTTPException
from app.schemas.user import User, UserCreate, UserUpdate
from app.models.user import User as UserModel
from app.database.session import get_db
from app.core.security import get_current_user
from prisma import Prisma

router = APIRouter()

@router.get("/me", response_model=User)
async def read_users_me(current_user: UserModel = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=User)
async def update_users_me(
    user_update: UserUpdate,
    db: Prisma = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    # Atualizar apenas os campos fornecidos
    update_data = user_update.dict(exclude_unset=True)
    
    # Remover campos sensíveis que não podem ser atualizados pelo usuário
    update_data.pop("role", None)
    update_data.pop("is_active", None)
    
    # Atualizar usuário
    updated_user = await db.user.update(
        where={"id": current_user.id},
        data=update_data
    )
    
    return updated_user

@router.get("/{user_id}", response_model=User)
async def read_user(user_id: int, db: Prisma = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    # Verificar se o usuário tem permissão para acessar este usuário
    # Administradores podem acessar qualquer usuário
    # Usuários podem acessar seu próprio perfil
    if current_user.id != user_id and current_user.role not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db_user = await db.user.find_unique(where={"id": user_id})
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Prisma = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    # Verificar permissões
    # Administradores podem atualizar qualquer usuário
    # Gerentes podem atualizar usuários comuns
    # Usuários podem atualizar seu próprio perfil (com restrições)
    target_user = await db.user.find_unique(where={"id": user_id})
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if current_user.id != user_id:
        if current_user.role != "admin":
            if current_user.role != "manager" or target_user.role == "admin":
                raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Se for um usuário comum tentando atualizar seu próprio perfil
    update_data = user_update.dict(exclude_unset=True)
    
    if current_user.id == user_id:
        # Remover campos sensíveis que não podem ser atualizados pelo próprio usuário
        update_data.pop("role", None)
        update_data.pop("is_active", None)
    
    # Atualizar usuário
    updated_user = await db.user.update(
        where={"id": user_id},
        data=update_data
    )
    
    return updated_user

@router.delete("/{user_id}", response_model=User)
async def delete_user(
    user_id: int,
    db: Prisma = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    # Apenas administradores podem excluir usuários
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Não permitir que um administrador se exclua
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    db_user = await db.user.find_unique(where={"id": user_id})
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verificar se o usuário é um administrador
    if db_user.role == "admin":
        # Verificar se há outros administradores
        admin_count = await db.user.count(where={"role": "admin"})
        if admin_count <= 1:
            raise HTTPException(status_code=400, detail="Cannot delete the last administrator")
    
    deleted_user = await db.user.delete(where={"id": user_id})
    return deleted_user

@router.get("/", response_model=list[User])
async def read_users(
    skip: int = 0, 
    limit: int = 100, 
    role: str = None,
    department: str = None,
    db: Prisma = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user)
):
    # Apenas administradores e gerentes podem listar todos os usuários
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Construir filtro
    where = {}
    if role:
        where["role"] = role
    if department:
        where["department"] = department
    
    db_users = await db.user.find_many(
        skip=skip, 
        take=limit,
        where=where
    )
    return db_users

@router.post("/assign-role/{user_id}", response_model=User)
async def assign_role(
    user_id: int,
    role: str,
    db: Prisma = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    # Apenas administradores podem atribuir papéis
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Validar papel
    valid_roles = ["admin", "manager", "employee"]
    if role not in valid_roles:
        raise HTTPException(status_code=400, detail=f"Invalid role. Valid roles: {valid_roles}")
    
    db_user = await db.user.find_unique(where={"id": user_id})
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Se estiver removendo o papel de administrador do último administrador
    if db_user.role == "admin" and role != "admin":
        admin_count = await db.user.count(where={"role": "admin"})
        if admin_count <= 1:
            raise HTTPException(status_code=400, detail="Cannot remove admin role from the last administrator")
    
    updated_user = await db.user.update(
        where={"id": user_id},
        data={"role": role}
    )
    
    return updated_user