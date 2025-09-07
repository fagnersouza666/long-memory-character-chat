from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from prisma import Prisma

from app.schemas.workspace import Workspace, WorkspaceCreate, WorkspaceUpdate, WorkspaceUser, WorkspaceUserCreate
from app.core.security import get_current_user
from app.models.user import User as UserModel
from app.database.session import get_db

router = APIRouter()

@router.post("/", response_model=Workspace)
async def create_workspace(
    workspace: WorkspaceCreate,
    current_user: UserModel = Depends(get_current_user),
    db: Prisma = Depends(get_db)
):
    """Criar um novo workspace"""
    try:
        # Verificar se o usuário pertence à organização
        org_user = await db.organizationuser.find_unique(
            where={
                "userId_organizationId": {
                    "userId": current_user.id,
                    "organizationId": workspace.organizationId
                }
            }
        )
        
        if not org_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to create workspace in this organization"
            )
        
        # Criar workspace
        db_workspace = await db.workspace.create(
            data={
                "name": workspace.name,
                "organizationId": workspace.organizationId
            }
        )
        
        # Associar o usuário criador como administrador do workspace
        await db.workspaceuser.create(
            data={
                "userId": current_user.id,
                "workspaceId": db_workspace.id,
                "role": "admin"
            }
        )
        
        return db_workspace
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating workspace: {str(e)}")

@router.get("/", response_model=List[Workspace])
async def read_workspaces(
    organization_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(get_current_user),
    db: Prisma = Depends(get_db)
):
    """Listar workspaces de uma organização"""
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
                detail="Not enough permissions to access workspaces in this organization"
            )
        
        # Buscar workspaces da organização
        workspaces = await db.workspace.find_many(
            where={
                "organizationId": organization_id
            },
            skip=skip,
            take=limit
        )
        
        return workspaces
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching workspaces: {str(e)}")

@router.get("/{workspace_id}", response_model=Workspace)
async def read_workspace(
    workspace_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Prisma = Depends(get_db)
):
    """Obter detalhes de um workspace específico"""
    try:
        # Verificar se o usuário pertence ao workspace
        workspace_user = await db.workspaceuser.find_unique(
            where={
                "userId_workspaceId": {
                    "userId": current_user.id,
                    "workspaceId": workspace_id
                }
            }
        )
        
        if not workspace_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to access this workspace"
            )
        
        # Buscar workspace
        db_workspace = await db.workspace.find_unique(
            where={
                "id": workspace_id
            }
        )
        
        if not db_workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        
        return db_workspace
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching workspace: {str(e)}")

@router.put("/{workspace_id}", response_model=Workspace)
async def update_workspace(
    workspace_id: int,
    workspace: WorkspaceUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: Prisma = Depends(get_db)
):
    """Atualizar um workspace"""
    try:
        # Verificar se o usuário é administrador do workspace
        workspace_user = await db.workspaceuser.find_unique(
            where={
                "userId_workspaceId": {
                    "userId": current_user.id,
                    "workspaceId": workspace_id
                }
            }
        )
        
        if not workspace_user or workspace_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to update this workspace"
            )
        
        # Verificar se o workspace existe
        db_workspace = await db.workspace.find_unique(
            where={
                "id": workspace_id
            }
        )
        
        if not db_workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        
        # Atualizar workspace
        updated_workspace = await db.workspace.update(
            where={
                "id": workspace_id
            },
            data={
                "name": workspace.name,
                "organizationId": workspace.organizationId
            }
        )
        
        return updated_workspace
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating workspace: {str(e)}")

@router.delete("/{workspace_id}", response_model=Workspace)
async def delete_workspace(
    workspace_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Prisma = Depends(get_db)
):
    """Excluir um workspace"""
    try:
        # Verificar se o usuário é administrador do workspace
        workspace_user = await db.workspaceuser.find_unique(
            where={
                "userId_workspaceId": {
                    "userId": current_user.id,
                    "workspaceId": workspace_id
                }
            }
        )
        
        if not workspace_user or workspace_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to delete this workspace"
            )
        
        # Verificar se o workspace existe
        db_workspace = await db.workspace.find_unique(
            where={
                "id": workspace_id
            }
        )
        
        if not db_workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        
        # Excluir workspace
        deleted_workspace = await db.workspace.delete(
            where={
                "id": workspace_id
            }
        )
        
        return deleted_workspace
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting workspace: {str(e)}")

@router.post("/{workspace_id}/users", response_model=WorkspaceUser)
async def add_user_to_workspace(
    workspace_id: int,
    user_data: WorkspaceUserCreate,
    current_user: UserModel = Depends(get_current_user),
    db: Prisma = Depends(get_db)
):
    """Adicionar um usuário a um workspace"""
    try:
        # Verificar se o usuário é administrador do workspace
        workspace_user = await db.workspaceuser.find_unique(
            where={
                "userId_workspaceId": {
                    "userId": current_user.id,
                    "workspaceId": workspace_id
                }
            }
        )
        
        if not workspace_user or workspace_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to add users to this workspace"
            )
        
        # Verificar se o workspace existe
        db_workspace = await db.workspace.find_unique(
            where={
                "id": workspace_id
            }
        )
        
        if not db_workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        
        # Verificar se o usuário já está no workspace
        existing_workspace_user = await db.workspaceuser.find_unique(
            where={
                "userId_workspaceId": {
                    "userId": user_data.userId,
                    "workspaceId": workspace_id
                }
            }
        )
        
        if existing_workspace_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member of this workspace"
            )
        
        # Verificar se o usuário pertence à organização do workspace
        workspace_org = await db.workspace.find_unique(
            where={
                "id": workspace_id
            }
        )
        
        if not workspace_org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        
        org_user = await db.organizationuser.find_unique(
            where={
                "userId_organizationId": {
                    "userId": user_data.userId,
                    "organizationId": workspace_org.organizationId
                }
            }
        )
        
        if not org_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User must be a member of the organization to be added to a workspace"
            )
        
        # Adicionar usuário ao workspace
        new_workspace_user = await db.workspaceuser.create(
            data={
                "userId": user_data.userId,
                "workspaceId": workspace_id,
                "role": user_data.role
            }
        )
        
        return new_workspace_user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding user to workspace: {str(e)}")

@router.delete("/{workspace_id}/users/{user_id}")
async def remove_user_from_workspace(
    workspace_id: int,
    user_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Prisma = Depends(get_db)
):
    """Remover um usuário de um workspace"""
    try:
        # Verificar se o usuário é administrador do workspace ou está tentando remover a si mesmo
        workspace_user = await db.workspaceuser.find_unique(
            where={
                "userId_workspaceId": {
                    "userId": current_user.id,
                    "workspaceId": workspace_id
                }
            }
        )
        
        is_admin = workspace_user and workspace_user.role == "admin"
        is_self = current_user.id == user_id
        
        if not is_admin and not is_self:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to remove users from this workspace"
            )
        
        # Verificar se o workspace existe
        db_workspace = await db.workspace.find_unique(
            where={
                "id": workspace_id
            }
        )
        
        if not db_workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        
        # Verificar se o usuário está no workspace
        existing_workspace_user = await db.workspaceuser.find_unique(
            where={
                "userId_workspaceId": {
                    "userId": user_id,
                    "workspaceId": workspace_id
                }
            }
        )
        
        if not existing_workspace_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User is not a member of this workspace"
            )
        
        # Não permitir que o último administrador se remova
        if is_self and workspace_user.role == "admin":
            # Verificar se há outros administradores
            admin_count = await db.workspaceuser.count(
                where={
                    "workspaceId": workspace_id,
                    "role": "admin"
                }
            )
            
            if admin_count <= 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot remove the last administrator from the workspace"
                )
        
        # Remover usuário do workspace
        await db.workspaceuser.delete(
            where={
                "userId_workspaceId": {
                    "userId": user_id,
                    "workspaceId": workspace_id
                }
            }
        )
        
        return {"message": "User removed from workspace successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error removing user from workspace: {str(e)}")