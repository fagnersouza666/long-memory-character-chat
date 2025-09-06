from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from prisma import Prisma
from datetime import datetime, timedelta
import time

from app.schemas.rate_limit import RateLimit, RateLimitCreate, RateLimitStatus
from app.core.security import get_current_user
from app.models.user import User as UserModel
from app.database.session import get_db

router = APIRouter()

# Armazenamento em memória para rate limiting (em produção, usar Redis ou similar)
rate_limit_storage = {}

@router.post("/", response_model=RateLimit)
async def create_rate_limit(
    rate_limit: RateLimitCreate,
    current_user: UserModel = Depends(get_current_user),
    db: Prisma = Depends(get_db)
):
    """Criar um novo limite de taxa"""
    try:
        # Apenas administradores podem criar limites de taxa
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can create rate limits"
            )
        
        # Criar limite de taxa
        db_rate_limit = await db.ratelimit.create(
            data={
                "userId": rate_limit.userId,
                "organizationId": rate_limit.organizationId,
                "feature": rate_limit.feature,
                "limit": rate_limit.limit,
                "window_seconds": rate_limit.window_seconds
            }
        )
        
        return RateLimit(
            id=db_rate_limit.id,
            userId=db_rate_limit.userId,
            organizationId=db_rate_limit.organizationId,
            feature=db_rate_limit.feature,
            limit=db_rate_limit.limit,
            window_seconds=db_rate_limit.window_seconds,
            createdAt=db_rate_limit.createdAt,
            updatedAt=db_rate_limit.updatedAt
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating rate limit: {str(e)}")

@router.get("/", response_model=List[RateLimit])
async def list_rate_limits(
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(get_current_user),
    db: Prisma = Depends(get_db)
):
    """Listar limites de taxa"""
    try:
        # Apenas administradores podem listar todos os limites de taxa
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can list rate limits"
            )
        
        # Buscar limites de taxa
        db_rate_limits = await db.ratelimit.find_many(
            skip=skip,
            take=limit
        )
        
        rate_limits = [
            RateLimit(
                id=rl.id,
                userId=rl.userId,
                organizationId=rl.organizationId,
                feature=rl.feature,
                limit=rl.limit,
                window_seconds=rl.window_seconds,
                createdAt=rl.createdAt,
                updatedAt=rl.updatedAt
            )
            for rl in db_rate_limits
        ]
        
        return rate_limits
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing rate limits: {str(e)}")

@router.get("/status/", response_model=List[RateLimitStatus])
async def get_rate_limit_status(
    current_user: UserModel = Depends(get_current_user)
):
    """Obter status dos limites de taxa para o usuário atual"""
    try:
        # Esta função verifica o status dos limites de taxa para o usuário
        # Em uma implementação real, isso seria conectado ao sistema de rate limiting
        
        # Para demonstração, retornamos alguns limites de taxa fictícios
        status_list = []
        
        # Verificar limite para buscas
        search_status = check_rate_limit(current_user.id, "search")
        status_list.append(search_status)
        
        # Verificar limite para uploads de documentos
        upload_status = check_rate_limit(current_user.id, "document_upload")
        status_list.append(upload_status)
        
        # Verificar limite para criação de avaliações
        evaluation_status = check_rate_limit(current_user.id, "evaluation_creation")
        status_list.append(evaluation_status)
        
        return status_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching rate limit status: {str(e)}")

def check_rate_limit(user_id: int, feature: str) -> RateLimitStatus:
    """Verificar o status de um limite de taxa para um usuário e recurso"""
    # Esta é uma implementação simplificada
    # Em produção, usar um sistema de armazenamento compartilhado como Redis
    
    key = f"{user_id}:{feature}"
    now = time.time()
    
    if key not in rate_limit_storage:
        rate_limit_storage[key] = {
            "count": 0,
            "reset_time": now + 3600  # 1 hora por padrão
        }
    
    # Resetar contador se o período expirou
    if now > rate_limit_storage[key]["reset_time"]:
        rate_limit_storage[key] = {
            "count": 0,
            "reset_time": now + 3600
        }
    
    # Incrementar contador
    rate_limit_storage[key]["count"] += 1
    
    # Para esta implementação, usamos limites fictícios
    limits = {
        "search": 100,
        "document_upload": 10,
        "evaluation_creation": 50
    }
    
    limit = limits.get(feature, 1000)  # Limite padrão
    remaining = max(0, limit - rate_limit_storage[key]["count"])
    reset_time = datetime.fromtimestamp(rate_limit_storage[key]["reset_time"])
    is_limited = rate_limit_storage[key]["count"] > limit
    
    return RateLimitStatus(
        feature=feature,
        limit=limit,
        remaining=remaining,
        reset_time=reset_time,
        is_limited=is_limited
    )

def enforce_rate_limit(user_id: int, feature: str):
    """Aplicar limite de taxa para um usuário e recurso"""
    status = check_rate_limit(user_id, feature)
    
    if status.is_limited:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded for {feature}. Try again at {status.reset_time}."
        )
    
    return status

# Dependência para aplicar rate limiting em endpoints
async def rate_limit_dependency(
    feature: str,
    current_user: UserModel = Depends(get_current_user)
):
    """Dependência para aplicar rate limiting"""
    enforce_rate_limit(current_user.id, feature)
    return True