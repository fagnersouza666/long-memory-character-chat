from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from prisma import Prisma
from datetime import datetime
import asyncio
import uuid

from app.schemas.document_processing import DocumentProcessingTask, DocumentProcessingTaskCreate, DocumentProcessingTaskUpdate, DocumentProcessingResult, ProcessingQueueStatus
from app.core.security import get_current_user
from app.models.user import User as UserModel
from app.database.session import get_db

router = APIRouter()

@router.post("/tasks/", response_model=DocumentProcessingTask)
async def create_processing_task(
    task_data: DocumentProcessingTaskCreate,
    current_user: UserModel = Depends(get_current_user),
    db: Prisma = Depends(get_db)
):
    """Criar uma nova tarefa de processamento de documento"""
    try:
        # Verificar se o usuário tem permissão para processar este documento
        db_document = await db.document.find_unique(
            where={
                "id": task_data.document_id
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
                    detail="Not enough permissions to process this document"
                )
        else:
            # Documento pessoal - apenas o autor pode processar
            if db_document.authorId != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions to process this document"
                )
        
        # Criar tarefa de processamento
        db_task = await db.documentprocessingtask.create(
            data={
                "documentId": task_data.document_id,
                "userId": current_user.id,
                "status": task_data.status,
                "priority": task_data.priority
            }
        )
        
        # Enviar tarefa para fila de processamento (simulado)
        # Em uma implementação real, isso seria enviado para um sistema de filas como Celery ou RabbitMQ
        # await send_to_processing_queue(db_task)
        
        return DocumentProcessingTask(
            id=db_task.id,
            document_id=db_task.documentId,
            user_id=db_task.userId,
            status=db_task.status,
            priority=db_task.priority,
            progress=db_task.progress,
            error_message=db_task.errorMessage,
            result_document_id=db_task.resultDocumentId,
            created_at=db_task.createdAt,
            updated_at=db_task.updatedAt,
            started_at=db_task.startedAt,
            completed_at=db_task.completedAt
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating processing task: {str(e)}")

@router.get("/tasks/", response_model=List[DocumentProcessingTask])
async def list_processing_tasks(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    document_id: int = None,
    current_user: UserModel = Depends(get_current_user),
    db: Prisma = Depends(get_db)
):
    """Listar tarefas de processamento de documentos"""
    try:
        # Construir condição WHERE
        where = {
            "userId": current_user.id
        }
        
        # Filtrar por status
        if status:
            where["status"] = status
        
        # Filtrar por documento
        if document_id:
            where["documentId"] = document_id
        
        # Buscar tarefas
        db_tasks = await db.documentprocessingtask.find_many(
            where=where,
            skip=skip,
            take=limit,
            order={
                "createdAt": "desc"
            }
        )
        
        tasks = [
            DocumentProcessingTask(
                id=task.id,
                document_id=task.documentId,
                user_id=task.userId,
                status=task.status,
                priority=task.priority,
                progress=task.progress,
                error_message=task.errorMessage,
                result_document_id=task.resultDocumentId,
                created_at=task.createdAt,
                updated_at=task.updatedAt,
                started_at=task.startedAt,
                completed_at=task.completedAt
            )
            for task in db_tasks
        ]
        
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing processing tasks: {str(e)}")

@router.get("/tasks/{task_id}", response_model=DocumentProcessingTask)
async def get_processing_task(
    task_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Prisma = Depends(get_db)
):
    """Obter detalhes de uma tarefa de processamento"""
    try:
        # Buscar tarefa
        db_task = await db.documentprocessingtask.find_unique(
            where={
                "id": task_id
            }
        )
        
        if not db_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Processing task not found"
            )
        
        # Verificar permissões
        if db_task.userId != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to access this processing task"
            )
        
        return DocumentProcessingTask(
            id=db_task.id,
            document_id=db_task.documentId,
            user_id=db_task.userId,
            status=db_task.status,
            priority=db_task.priority,
            progress=db_task.progress,
            error_message=db_task.errorMessage,
            result_document_id=db_task.resultDocumentId,
            created_at=db_task.createdAt,
            updated_at=db_task.updatedAt,
            started_at=db_task.startedAt,
            completed_at=db_task.completedAt
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching processing task: {str(e)}")

@router.put("/tasks/{task_id}", response_model=DocumentProcessingTask)
async def update_processing_task(
    task_id: int,
    task_update: DocumentProcessingTaskUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: Prisma = Depends(get_db)
):
    """Atualizar uma tarefa de processamento"""
    try:
        # Buscar tarefa
        db_task = await db.documentprocessingtask.find_unique(
            where={
                "id": task_id
            }
        )
        
        if not db_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Processing task not found"
            )
        
        # Verificar permissões
        if db_task.userId != current_user.id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to update this processing task"
            )
        
        # Atualizar tarefa
        update_data = task_update.dict(exclude_unset=True)
        
        # Se o status estiver sendo atualizado para "processing", definir started_at
        if "status" in update_data and update_data["status"] == "processing":
            update_data["startedAt"] = datetime.now()
        
        # Se o status estiver sendo atualizado para "completed" ou "failed", definir completed_at
        if "status" in update_data and update_data["status"] in ["completed", "failed"]:
            update_data["completedAt"] = datetime.now()
        
        updated_task = await db.documentprocessingtask.update(
            where={
                "id": task_id
            },
            data={
                **update_data,
                "updatedAt": datetime.now()
            }
        )
        
        return DocumentProcessingTask(
            id=updated_task.id,
            document_id=updated_task.documentId,
            user_id=updated_task.userId,
            status=updated_task.status,
            priority=updated_task.priority,
            progress=updated_task.progress,
            error_message=updated_task.errorMessage,
            result_document_id=updated_task.resultDocumentId,
            created_at=updated_task.createdAt,
            updated_at=updated_task.updatedAt,
            started_at=updated_task.startedAt,
            completed_at=updated_task.completedAt
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating processing task: {str(e)}")

@router.delete("/tasks/{task_id}", response_model=DocumentProcessingTask)
async def delete_processing_task(
    task_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Prisma = Depends(get_db)
):
    """Excluir uma tarefa de processamento"""
    try:
        # Buscar tarefa
        db_task = await db.documentprocessingtask.find_unique(
            where={
                "id": task_id
            }
        )
        
        if not db_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Processing task not found"
            )
        
        # Verificar permissões
        if db_task.userId != current_user.id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to delete this processing task"
            )
        
        # Excluir tarefa
        deleted_task = await db.documentprocessingtask.delete(
            where={
                "id": task_id
            }
        )
        
        return DocumentProcessingTask(
            id=deleted_task.id,
            document_id=deleted_task.documentId,
            user_id=deleted_task.userId,
            status=deleted_task.status,
            priority=deleted_task.priority,
            progress=deleted_task.progress,
            error_message=deleted_task.errorMessage,
            result_document_id=deleted_task.resultDocumentId,
            created_at=deleted_task.createdAt,
            updated_at=deleted_task.updatedAt,
            started_at=deleted_task.startedAt,
            completed_at=deleted_task.completedAt
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting processing task: {str(e)}")

@router.get("/queue/status/", response_model=ProcessingQueueStatus)
async def get_queue_status(
    current_user: UserModel = Depends(get_current_user),
    db: Prisma = Depends(get_db)
):
    """Obter status da fila de processamento"""
    try:
        # Contar tarefas por status
        total_tasks = await db.documentprocessingtask.count()
        
        pending_tasks = await db.documentprocessingtask.count(
            where={
                "status": "pending"
            }
        )
        
        processing_tasks = await db.documentprocessingtask.count(
            where={
                "status": "processing"
            }
        )
        
        completed_tasks = await db.documentprocessingtask.count(
            where={
                "status": "completed"
            }
        )
        
        failed_tasks = await db.documentprocessingtask.count(
            where={
                "status": "failed"
            }
        )
        
        # Calcular tempo médio de processamento
        completed_tasks_with_time = await db.documentprocessingtask.find_many(
            where={
                "status": "completed",
                "startedAt": {
                    "not": None
                },
                "completedAt": {
                    "not": None
                }
            }
        )
        
        total_processing_time = 0.0
        for task in completed_tasks_with_time:
            if task.startedAt and task.completedAt:
                processing_time = (task.completedAt - task.startedAt).total_seconds()
                total_processing_time += processing_time
        
        average_processing_time = total_processing_time / len(completed_tasks_with_time) if completed_tasks_with_time else 0.0
        
        return ProcessingQueueStatus(
            total_tasks=total_tasks,
            pending_tasks=pending_tasks,
            processing_tasks=processing_tasks,
            completed_tasks=completed_tasks,
            failed_tasks=failed_tasks,
            average_processing_time=average_processing_time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching queue status: {str(e)}")

@router.post("/tasks/{task_id}/process/", response_model=DocumentProcessingResult)
async def process_document_task(
    task_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Prisma = Depends(get_db)
):
    """Processar uma tarefa de documento (simulação)"""
    try:
        # Buscar tarefa
        db_task = await db.documentprocessingtask.find_unique(
            where={
                "id": task_id
            }
        )
        
        if not db_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Processing task not found"
            )
        
        # Verificar permissões
        if db_task.userId != current_user.id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to process this document"
            )
        
        # Verificar se a tarefa já foi processada
        if db_task.status in ["completed", "failed"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task has already been processed"
            )
        
        # Atualizar status para "processing"
        await db.documentprocessingtask.update(
            where={
                "id": task_id
            },
            data={
                "status": "processing",
                "startedAt": datetime.now(),
                "updatedAt": datetime.now()
            }
        )
        
        # Simular processamento do documento
        # Em uma implementação real, isso seria feito por um worker assíncrono
        result = await simulate_document_processing(db_task.documentId, db)
        
        # Atualizar tarefa com resultado
        await db.documentprocessingtask.update(
            where={
                "id": task_id
            },
            data={
                "status": "completed" if result.status == "success" else "failed",
                "progress": 100,
                "completedAt": datetime.now(),
                "updatedAt": datetime.now(),
                "errorMessage": result.error_message
            }
        )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        # Atualizar tarefa com status de falha
        await db.documentprocessingtask.update(
            where={
                "id": task_id
            },
            data={
                "status": "failed",
                "completedAt": datetime.now(),
                "updatedAt": datetime.now(),
                "errorMessage": str(e)
            }
        )
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

async def simulate_document_processing(document_id: int, db: Prisma) -> DocumentProcessingResult:
    """Simular o processamento de um documento"""
    # Esta função simula o processamento real de um documento
    # Em uma implementação real, isso seria feito por um worker separado
    
    try:
        # Buscar documento
        document = await db.document.find_unique(
            where={
                "id": document_id
            }
        )
        
        if not document:
            raise Exception("Document not found")
        
        # Simular extração de texto (baseado no tipo de arquivo)
        content = f"Conteúdo simulado do documento {document.title}"
        
        # Simular divisão em chunks
        chunks = []
        chunk_size = 500
        for i in range(0, len(content), chunk_size):
            chunk_content = content[i:i+chunk_size]
            chunks.append(chunk_content)
        
        # Simular geração de embeddings (valores aleatórios)
        import random
        chunks_with_embeddings = []
        for i, chunk in enumerate(chunks):
            embedding = [random.random() for _ in range(1536)]  # Tamanho típico de embedding
            chunks_with_embeddings.append({
                "documentId": document_id,
                "content": chunk,
                "embedding": embedding,
                "position": i
            })
        
        # Criar chunks no banco de dados
        for chunk_data in chunks_with_embeddings:
            await db.documentchunk.create(
                data={
                    "documentId": chunk_data["documentId"],
                    "content": chunk_data["content"],
                    "embedding": chunk_data["embedding"]
                }
            )
        
        # Retornar resultado
        return DocumentProcessingResult(
            task_id=document_id,
            document_id=document_id,
            chunks_created=len(chunks_with_embeddings),
            embeddings_generated=len(chunks_with_embeddings),
            processing_time_seconds=random.uniform(1.0, 10.0),
            status="success"
        )
    except Exception as e:
        return DocumentProcessingResult(
            task_id=document_id,
            document_id=document_id,
            chunks_created=0,
            embeddings_generated=0,
            processing_time_seconds=0.0,
            status="failed",
            error_message=str(e)
        )