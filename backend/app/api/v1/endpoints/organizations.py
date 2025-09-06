from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from prisma import Prisma

from app.schemas.organization import Organization, OrganizationCreate, OrganizationUpdate, OrganizationUser
from app.core.security import get_current_user
from app.models.user import User as UserModel
from app.database.session import get_db

router = APIRouter()

@router.post("/", response_model=Organization)
async def create_organization(
    organization: OrganizationCreate,
    current_user: UserModel = Depends(get_current_user),
    db: Prisma = Depends(get_db)
):
    """Criar uma nova organização"""
    try:
        # Verificar se o usuário tem permissão para criar organizações
        if current_user.role not in ["admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to create organization"
            )
        
        # Criar organização
        db_organization = await db.organization.create(
            data={
                "name": organization.name
            }
        )
        
        # Associar o usuário criador como administrador da organização
        await db.organizationuser.create(
            data={
                "userId": current_user.id,
                "organizationId": db_organization.id,
                "role": "admin"
            }
        )
        
        return db_organization
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating organization: {str(e)}")

@router.get("/", response_model=List[Organization])
async def read_organizations(
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(get_current_user),
    db: Prisma = Depends(get_db)
):
    """Listar organizações às quais o usuário pertence"""
    try:
        # Buscar organizações do usuário
        org_users = await db.organizationuser.find_many(
            where={
                "userId": current_user.id
            },
            include={
                "organization": True
            }
        )
        
        organizations = [org_user.organization for org_user in org_users]
        return organizations[skip:skip + limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching organizations: {str(e)}")

@router.get("/{organization_id}", response_model=Organization)
async def read_organization(
    organization_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Prisma = Depends(get_db)
):
    """Obter detalhes de uma organização específica"""
    try:
        # Verificar se o usuário pertence à organização
        org_user = await db.organizationuser.find_unique(
            where={
                "userId_organizationId": {
                    "userId": current_user.id,
                    "organizationId": organization_id
                }
            }
        )
        
        if not org_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to access this organization"
            )
        
        # Buscar organização
        db_organization = await db.organization.find_unique(
            where={
                "id": organization_id
            }
        )
        
        if not db_organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        return db_organization
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching organization: {str(e)}")

@router.put("/{organization_id}", response_model=Organization)
async def update_organization(
    organization_id: int,
    organization: OrganizationUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: Prisma = Depends(get_db)
):
    """Atualizar uma organização"""
    try:
        # Verificar se o usuário é administrador da organização
        org_user = await db.organizationuser.find_unique(
            where={
                "userId_organizationId": {
                    "userId": current_user.id,
                    "organizationId": organization_id
                }
            }
        )
        
        if not org_user or org_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to update this organization"
            )
        
        # Verificar se a organização existe
        db_organization = await db.organization.find_unique(
            where={
                "id": organization_id
            }
        )
        
        if not db_organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        # Atualizar organização
        updated_organization = await db.organization.update(
            where={
                "id": organization_id
            },
            data={
                "name": organization.name
            }
        )
        
        return updated_organization
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating organization: {str(e)}")

@router.delete("/{organization_id}", response_model=Organization)
async def delete_organization(
    organization_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Prisma = Depends(get_db)
):
    """Excluir uma organização"""
    try:
        # Verificar se o usuário é administrador da organização
        org_user = await db.organizationuser.find_unique(
            where={
                "userId_organizationId": {
                    "userId": current_user.id,
                    "organizationId": organization_id
                }
            }
        )
        
        if not org_user or org_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to delete this organization"
            )
        
        # Verificar se a organização existe
        db_organization = await db.organization.find_unique(
            where={
                "id": organization_id
            }
        )
        
        if not db_organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        # Excluir organização (isso irá excluir em cascata os workspaces e associações)
        deleted_organization = await db.organization.delete(
            where={
                "id": organization_id
            }
        )
        
        return deleted_organization
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting organization: {str(e)}")

@router.post("/{organization_id}/users", response_model=OrganizationUser)
async def add_user_to_organization(
    organization_id: int,
    user_data: OrganizationUserCreate,
    current_user: UserModel = Depends(get_current_user),
    db: Prisma = Depends(get_db)
):
    """Adicionar um usuário a uma organização"""
    try:
        # Verificar se o usuário é administrador da organização
        org_user = await db.organizationuser.find_unique(
            where={
                "userId_organizationId": {
                    "userId": current_user.id,
                    "organizationId": organization_id
                }
            }
        )
        
        if not org_user or org_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to add users to this organization"
            )
        
        # Verificar se a organização existe
        db_organization = await db.organization.find_unique(
            where={
                "id": organization_id
            }
        )
        
        if not db_organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        # Verificar se o usuário já está na organização
        existing_org_user = await db.organizationuser.find_unique(
            where={
                "userId_organizationId": {
                    "userId": user_data.userId,
                    "organizationId": organization_id
                }
            }
        )
        
        if existing_org_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member of this organization"
            )
        
        # Adicionar usuário à organização
        new_org_user = await db.organizationuser.create(
            data={
                "userId": user_data.userId,
                "organizationId": organization_id,
                "role": user_data.role
            }
        )
        
        return new_org_user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding user to organization: {str(e)}")

@router.delete("/{organization_id}/users/{user_id}")
async def remove_user_from_organization(
    organization_id: int,
    user_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Prisma = Depends(get_db)
):
    """Remover um usuário de uma organização"""
    try:
        # Verificar se o usuário é administrador da organização ou está tentando remover a si mesmo
        org_user = await db.organizationuser.find_unique(
            where={
                "userId_organizationId": {
                    "userId": current_user.id,
                    "organizationId": organization_id
                }
            }
        )
        
        is_admin = org_user and org_user.role == "admin"
        is_self = current_user.id == user_id
        
        if not is_admin and not is_self:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to remove users from this organization"
            )
        
        # Verificar se a organização existe
        db_organization = await db.organization.find_unique(
            where={
                "id": organization_id
            }
        )
        
        if not db_organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        # Verificar se o usuário está na organização
        existing_org_user = await db.organizationuser.find_unique(
            where={
                "userId_organizationId": {
                    "userId": user_id,
                    "organizationId": organization_id
                }
            }
        )
        
        if not existing_org_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User is not a member of this organization"
            )
        
        # Não permitir que o último administrador se remova
        if is_self and org_user.role == "admin":
            # Verificar se há outros administradores
            admin_count = await db.organizationuser.count(
                where={
                    "organizationId": organization_id,
                    "role": "admin"
                }
            )
            
            if admin_count <= 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot remove the last administrator from the organization"
                )
        
        # Remover usuário da organização
        await db.organizationuser.delete(
            where={
                "userId_organizationId": {
                    "userId": user_id,
                    "organizationId": organization_id
                }
            }
        )
        
        return {"message": "User removed from organization successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error removing user from organization: {str(e)}")