from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from typing import List, Optional
from prisma import Prisma
import os
import uuid
from datetime import datetime

from app.schemas.document import Document, DocumentCreate, DocumentUpdate
from app.core.security import get_current_user
from app.models.user import User as UserModel
from app.database.session import get_db

router = APIRouter()

# Diretório para armazenamento de documentos
DOCUMENT_STORAGE_PATH = "docs/storage"

# Criar diretório se não existir
os.makedirs(DOCUMENT_STORAGE_PATH, exist_ok=True)

@router.post("/", response_model=Document)
async def upload_document(
    file: UploadFile = File(...),
    title: str = None,
    workspace_id: int = None,
    tags: str = None,  # Tags separadas por vírgula
    current_user: UserModel = Depends(get_current_user),
    db: Prisma = Depends(get_db)
):
    """Fazer upload de um documento"""
    try:
        # Verificar se o usuário pertence ao workspace
        if workspace_id:
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
                    detail="Not enough permissions to upload document to this workspace"
                )
        
        # Gerar nome de arquivo único
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(DOCUMENT_STORAGE_PATH, unique_filename)
        
        # Salvar arquivo
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Parse tags
        tag_list = tags.split(",") if tags else []
        tag_list = [tag.strip() for tag in tag_list if tag.strip()]
        
        # Criar documento no banco de dados
        db_document = await db.document.create(
            data={
                "title": title or file.filename,
                "filePath": file_path,
                "fileType": file.content_type or "application/octet-stream",
                "size": len(content),
                "authorId": current_user.id,
                "workspaceId": workspace_id or 0,  # 0 para documentos pessoais
                "status": "active"
            }
        )
        
        return db_document
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")

@router.get("/", response_model=List[Document])
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    workspace_id: Optional[int] = None,
    file_type: Optional[str] = None,
    tag: Optional[str] = None,
    current_user: UserModel = Depends(get_current_user),
    db: Prisma = Depends(get_db)
):
    """Listar documentos"""
    try:
        # Construir condição WHERE
        where = {}
        
        # Filtrar por workspace (se especificado)
        if workspace_id is not None:
            # Verificar se o usuário tem acesso ao workspace
            if workspace_id > 0:
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
                        detail="Not enough permissions to access documents in this workspace"
                    )
            
            where["workspaceId"] = workspace_id
        
        # Filtrar por tipo de arquivo
        if file_type:
            where["fileType"] = file_type
        
        # Filtrar por tag (simplificado - na implementação completa, seria necessário uma tabela de tags)
        # Para esta implementação, assumimos que tags são armazenadas como string separada por vírgulas
        
        # Buscar documentos
        documents = await db.document.find_many(
            where=where,
            skip=skip,
            take=limit,
            order={
                "uploadDate": "desc"
            }
        )
        
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")

@router.get("/{document_id}", response_model=Document)
async def get_document(
    document_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Prisma = Depends(get_db)
):
    """Obter detalhes de um documento"""
    try:
        # Buscar documento
        db_document = await db.document.find_unique(
            where={
                "id": document_id
            }
        )
        
        if not db_document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Verificar permissões
        if db_document.workspaceId > 0:
            # Documento em workspace - verificar se usuário tem acesso
            workspace_user = await db.workspaceuser.find_unique(
                where={
                    "userId_workspaceId": {
                        "userId": current_user.id,
                        "workspaceId": db_document.workspaceId
                    }
                }
            )
            
            if not workspace_user:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions to access this document"
                )
        else:
            # Documento pessoal - apenas o autor pode acessar
            if db_document.authorId != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions to access this document"
                )
        
        return db_document
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching document: {str(e)}")

@router.put("/{document_id}", response_model=Document)
async def update_document(
    document_id: int,
    document_update: DocumentUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: Prisma = Depends(get_db)
):
    """Atualizar um documento"""
    try:
        # Buscar documento
        db_document = await db.document.find_unique(
            where={
                "id": document_id
            }
        )
        
        if not db_document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Verificar permissões
        if db_document.workspaceId > 0:
            # Documento em workspace - verificar se usuário tem acesso
            workspace_user = await db.workspaceuser.find_unique(
                where={
                    "userId_workspaceId": {
                        "userId": current_user.id,
                        "workspaceId": db_document.workspaceId
                    }
                }
            )
            
            if not workspace_user:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions to update this document"
                )
            
            # Apenas administradores do workspace podem atualizar documentos de outros usuários
            if db_document.authorId != current_user.id and workspace_user.role != "admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions to update this document"
                )
        else:
            # Documento pessoal - apenas o autor pode atualizar
            if db_document.authorId != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions to update this document"
                )
        
        # Atualizar documento
        update_data = document_update.dict(exclude_unset=True)
        updated_document = await db.document.update(
            where={
                "id": document_id
            },
            data={
                **update_data,
                "updatedAt": datetime.now()
            }
        )
        
        return updated_document
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating document: {str(e)}")

@router.delete("/{document_id}", response_model=Document)
async def delete_document(
    document_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Prisma = Depends(get_db)
):
    """Excluir um documento"""
    try:
        # Buscar documento
        db_document = await db.document.find_unique(
            where={
                "id": document_id
            }
        )
        
        if not db_document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Verificar permissões
        if db_document.workspaceId > 0:
            # Documento em workspace - verificar se usuário tem acesso
            workspace_user = await db.workspaceuser.find_unique(
                where={
                    "userId_workspaceId": {
                        "userId": current_user.id,
                        "workspaceId": db_document.workspaceId
                    }
                }
            )
            
            if not workspace_user:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions to delete this document"
                )
            
            # Apenas administradores do workspace podem excluir documentos de outros usuários
            if db_document.authorId != current_user.id and workspace_user.role != "admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions to delete this document"
                )
        else:
            # Documento pessoal - apenas o autor pode excluir
            if db_document.authorId != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions to delete this document"
                )
        
        # Excluir arquivo do sistema de arquivos
        if os.path.exists(db_document.filePath):
            os.remove(db_document.filePath)
        
        # Excluir documento do banco de dados
        deleted_document = await db.document.delete(
            where={
                "id": document_id
            }
        )
        
        return deleted_document
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")

@router.get("/{document_id}/download")
async def download_document(
    document_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Prisma = Depends(get_db)
):
    """Baixar um documento"""
    try:
        # Buscar documento
        db_document = await db.document.find_unique(
            where={
                "id": document_id
            }
        )
        
        if not db_document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Verificar permissões
        if db_document.workspaceId > 0:
            # Documento em workspace - verificar se usuário tem acesso
            workspace_user = await db.workspaceuser.find_unique(
                where={
                    "userId_workspaceId": {
                        "userId": current_user.id,
                        "workspaceId": db_document.workspaceId
                    }
                }
            )
            
            if not workspace_user:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions to download this document"
                )
        else:
            # Documento pessoal - apenas o autor pode acessar
            if db_document.authorId != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions to download this document"
                )
        
        # Verificar se o arquivo existe
        if not os.path.exists(db_document.filePath):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document file not found"
            )
        
        # Retornar arquivo
        return FileResponse(
            path=db_document.filePath,
            filename=db_document.title,
            media_type=db_document.fileType
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading document: {str(e)}")