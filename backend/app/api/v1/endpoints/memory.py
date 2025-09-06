from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from prisma import Prisma
import uuid
from datetime import datetime

from app.schemas.memory import Conversation, ConversationCreate, ConversationUpdate, Message, MemorySummary, MemorySummaryCreate, Context
from app.core.security import get_current_user
from app.models.user import User as UserModel
from app.database.session import get_db

router = APIRouter()

@router.post("/conversations/", response_model=Conversation)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user: UserModel = Depends(get_current_user),
    db: Prisma = Depends(get_db)
):
    """Criar uma nova conversa"""
    try:
        # Gerar ID único para a conversa
        conversation_id = str(uuid.uuid4())
        
        # Criar conversa no banco de dados
        db_conversation = await db.conversation.create(
            data={
                "id": conversation_id,
                "userId": current_user.id,
                "title": conversation_data.title,
                "metadata": conversation_data.metadata or {}
            }
        )
        
        return Conversation(
            id=db_conversation.id,
            user_id=db_conversation.userId,
            title=db_conversation.title,
            messages=[],
            created_at=db_conversation.createdAt,
            updated_at=db_conversation.updatedAt,
            metadata=db_conversation.metadata
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating conversation: {str(e)}")

@router.get("/conversations/", response_model=List[Conversation])
async def list_conversations(
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(get_current_user),
    db: Prisma = Depends(get_db)
):
    """Listar conversas do usuário"""
    try:
        # Buscar conversas do usuário
        db_conversations = await db.conversation.find_many(
            where={
                "userId": current_user.id
            },
            skip=skip,
            take=limit,
            order={
                "updatedAt": "desc"
            }
        )
        
        conversations = []
        for conv in db_conversations:
            # Buscar mensagens da conversa
            db_messages = await db.message.find_many(
                where={
                    "conversationId": conv.id
                },
                order={
                    "timestamp": "asc"
                }
            )
            
            messages = [
                Message(
                    role=msg.role,
                    content=msg.content,
                    timestamp=msg.timestamp
                )
                for msg in db_messages
            ]
            
            conversations.append(Conversation(
                id=conv.id,
                user_id=conv.userId,
                title=conv.title,
                messages=messages,
                created_at=conv.createdAt,
                updated_at=conv.updatedAt,
                metadata=conv.metadata
            ))
        
        return conversations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing conversations: {str(e)}")

@router.get("/conversations/{conversation_id}", response_model=Conversation)
async def get_conversation(
    conversation_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: Prisma = Depends(get_db)
):
    """Obter detalhes de uma conversa"""
    try:
        # Buscar conversa
        db_conversation = await db.conversation.find_unique(
            where={
                "id": conversation_id
            }
        )
        
        if not db_conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Verificar permissões
        if db_conversation.userId != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to access this conversation"
            )
        
        # Buscar mensagens da conversa
        db_messages = await db.message.find_many(
            where={
                "conversationId": conversation_id
            },
            order={
                "timestamp": "asc"
            }
        )
        
        messages = [
            Message(
                role=msg.role,
                content=msg.content,
                timestamp=msg.timestamp
            )
            for msg in db_messages
        ]
        
        return Conversation(
            id=db_conversation.id,
            user_id=db_conversation.userId,
            title=db_conversation.title,
            messages=messages,
            created_at=db_conversation.createdAt,
            updated_at=db_conversation.updatedAt,
            metadata=db_conversation.metadata
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching conversation: {str(e)}")

@router.put("/conversations/{conversation_id}", response_model=Conversation)
async def update_conversation(
    conversation_id: str,
    conversation_update: ConversationUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: Prisma = Depends(get_db)
):
    """Atualizar uma conversa"""
    try:
        # Buscar conversa
        db_conversation = await db.conversation.find_unique(
            where={
                "id": conversation_id
            }
        )
        
        if not db_conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Verificar permissões
        if db_conversation.userId != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to update this conversation"
            )
        
        # Atualizar conversa
        update_data = conversation_update.dict(exclude_unset=True)
        updated_conversation = await db.conversation.update(
            where={
                "id": conversation_id
            },
            data={
                **update_data,
                "updatedAt": datetime.now()
            }
        )
        
        # Buscar mensagens da conversa
        db_messages = await db.message.find_many(
            where={
                "conversationId": conversation_id
            },
            order={
                "timestamp": "asc"
            }
        )
        
        messages = [
            Message(
                role=msg.role,
                content=msg.content,
                timestamp=msg.timestamp
            )
            for msg in db_messages
        ]
        
        return Conversation(
            id=updated_conversation.id,
            user_id=updated_conversation.userId,
            title=updated_conversation.title,
            messages=messages,
            created_at=updated_conversation.createdAt,
            updated_at=updated_conversation.updatedAt,
            metadata=updated_conversation.metadata
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating conversation: {str(e)}")

@router.delete("/conversations/{conversation_id}", response_model=Conversation)
async def delete_conversation(
    conversation_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: Prisma = Depends(get_db)
):
    """Excluir uma conversa"""
    try:
        # Buscar conversa
        db_conversation = await db.conversation.find_unique(
            where={
                "id": conversation_id
            }
        )
        
        if not db_conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Verificar permissões
        if db_conversation.userId != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to delete this conversation"
            )
        
        # Excluir mensagens da conversa primeiro (devido à chave estrangeira)
        await db.message.delete_many(
            where={
                "conversationId": conversation_id
            }
        )
        
        # Excluir conversa
        deleted_conversation = await db.conversation.delete(
            where={
                "id": conversation_id
            }
        )
        
        return Conversation(
            id=deleted_conversation.id,
            user_id=deleted_conversation.userId,
            title=deleted_conversation.title,
            messages=[],
            created_at=deleted_conversation.createdAt,
            updated_at=deleted_conversation.updatedAt,
            metadata=deleted_conversation.metadata
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting conversation: {str(e)}")

@router.post("/conversations/{conversation_id}/messages/", response_model=Message)
async def add_message(
    conversation_id: str,
    message: Message,
    current_user: UserModel = Depends(get_current_user),
    db: Prisma = Depends(get_db)
):
    """Adicionar uma mensagem a uma conversa"""
    try:
        # Buscar conversa
        db_conversation = await db.conversation.find_unique(
            where={
                "id": conversation_id
            }
        )
        
        if not db_conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Verificar permissões
        if db_conversation.userId != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to add message to this conversation"
            )
        
        # Adicionar mensagem
        db_message = await db.message.create(
            data={
                "conversationId": conversation_id,
                "role": message.role,
                "content": message.content,
                "timestamp": message.timestamp
            }
        )
        
        # Atualizar data de atualização da conversa
        await db.conversation.update(
            where={
                "id": conversation_id
            },
            data={
                "updatedAt": datetime.now()
            }
        )
        
        return Message(
            role=db_message.role,
            content=db_message.content,
            timestamp=db_message.timestamp
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding message: {str(e)}")

@router.post("/memory-summaries/", response_model=MemorySummary)
async def create_memory_summary(
    memory_summary: MemorySummaryCreate,
    current_user: UserModel = Depends(get_current_user),
    db: Prisma = Depends(get_db)
):
    """Criar um resumo de memória"""
    try:
        # Gerar ID único para o resumo
        summary_id = str(uuid.uuid4())
        
        # Criar resumo no banco de dados
        db_summary = await db.memorysummary.create(
            data={
                "id": summary_id,
                "userId": current_user.id,
                "content": memory_summary.content,
                "relevanceScore": memory_summary.relevance_score
            }
        )
        
        return MemorySummary(
            id=db_summary.id,
            user_id=db_summary.userId,
            content=db_summary.content,
            created_at=db_summary.createdAt,
            updated_at=db_summary.updatedAt,
            relevance_score=db_summary.relevanceScore
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating memory summary: {str(e)}")

@router.get("/memory-summaries/", response_model=List[MemorySummary])
async def list_memory_summaries(
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(get_current_user),
    db: Prisma = Depends(get_db)
):
    """Listar resumos de memória do usuário"""
    try:
        # Buscar resumos do usuário
        db_summaries = await db.memorysummary.find_many(
            where={
                "userId": current_user.id
            },
            skip=skip,
            take=limit,
            order={
                "createdAt": "desc"
            }
        )
        
        summaries = [
            MemorySummary(
                id=summary.id,
                user_id=summary.userId,
                content=summary.content,
                created_at=summary.createdAt,
                updated_at=summary.updatedAt,
                relevance_score=summary.relevanceScore
            )
            for summary in db_summaries
        ]
        
        return summaries
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing memory summaries: {str(e)}")

@router.get("/context/{conversation_id}", response_model=Context)
async def get_context(
    conversation_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: Prisma = Depends(get_db)
):
    """Obter contexto para uma conversa"""
    try:
        # Buscar conversa
        db_conversation = await db.conversation.find_unique(
            where={
                "id": conversation_id
            }
        )
        
        if not db_conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Verificar permissões
        if db_conversation.userId != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to access context for this conversation"
            )
        
        # Buscar resumos de memória relevantes
        db_summaries = await db.memorysummary.find_many(
            where={
                "userId": current_user.id
            },
            take=5,  # Limitar a 5 resumos mais relevantes
            order={
                "relevanceScore": "desc"
            }
        )
        
        memory_summaries = [
            MemorySummary(
                id=summary.id,
                user_id=summary.userId,
                content=summary.content,
                created_at=summary.createdAt,
                updated_at=summary.updatedAt,
                relevance_score=summary.relevanceScore
            )
            for summary in db_summaries
        ]
        
        # Para documentos e avaliações relevantes, isso seria determinado
        # por um sistema de busca mais complexo
        relevant_documents = []  # Seria preenchido com IDs de documentos relevantes
        relevant_evaluations = []  # Seria preenchido com IDs de avaliações relevantes
        
        return Context(
            conversation_id=conversation_id,
            user_id=current_user.id,
            relevant_documents=relevant_documents,
            relevant_evaluations=relevant_evaluations,
            memory_summaries=memory_summaries,
            created_at=datetime.now()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching context: {str(e)}")