from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from prisma import Prisma
from datetime import datetime, timedelta

from app.schemas.cost import UsageRecord, UsageRecordCreate, CostDashboard, CostHistory
from app.core.security import get_current_user
from app.models.user import User as UserModel
from app.database.session import get_db

router = APIRouter()

@router.post("/usage/", response_model=UsageRecord)
async def record_usage(
    usage_record: UsageRecordCreate,
    current_user: UserModel = Depends(get_current_user),
    db: Prisma = Depends(get_db)
):
    """Registrar uso de recursos e custos associados"""
    try:
        # Verificar permissões - apenas administradores podem registrar uso para outros usuários
        if usage_record.userId != current_user.id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to record usage for this user"
            )
        
        # Registrar uso
        db_usage_record = await db.usagerecord.create(
            data={
                "userId": usage_record.userId,
                "organizationId": usage_record.organizationId,
                "feature": usage_record.feature,
                "tokens_used": usage_record.tokens_used,
                "cost": usage_record.cost
            }
        )
        
        return UsageRecord(
            id=db_usage_record.id,
            userId=db_usage_record.userId,
            organizationId=db_usage_record.organizationId,
            feature=db_usage_record.feature,
            tokens_used=db_usage_record.tokens_used,
            cost=db_usage_record.cost,
            timestamp=db_usage_record.timestamp
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error recording usage: {str(e)}")

@router.get("/dashboard/", response_model=CostDashboard)
async def get_cost_dashboard(
    organization_id: int = None,
    current_user: UserModel = Depends(get_current_user),
    db: Prisma = Depends(get_db)
):
    """Obter dashboard de custos"""
    try:
        # Determinar o escopo da consulta
        where = {}
        
        if organization_id:
            # Verificar se o usuário tem acesso à organização
            if current_user.role != "admin":
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
                        detail="Not enough permissions to access cost data for this organization"
                    )
            
            where["organizationId"] = organization_id
        else:
            # Para usuários não administradores, mostrar apenas seus próprios custos
            if current_user.role != "admin":
                where["userId"] = current_user.id
            # Administradores podem ver todos os custos (sem filtro)
        
        # Calcular custos totais
        total_cost_record = await db.usagerecord.aggregate(
            where=where,
            _sum={
                "cost": True
            }
        )
        total_cost = total_cost_record._sum.cost or 0.0
        
        # Calcular custos diários (últimas 24 horas)
        daily_start = datetime.now() - timedelta(days=1)
        daily_cost_record = await db.usagerecord.aggregate(
            where={
                **where,
                "timestamp": {
                    "gte": daily_start
                }
            },
            _sum={
                "cost": True
            }
        )
        daily_cost = daily_cost_record._sum.cost or 0.0
        
        # Calcular custos semanais (últimos 7 dias)
        weekly_start = datetime.now() - timedelta(days=7)
        weekly_cost_record = await db.usagerecord.aggregate(
            where={
                **where,
                "timestamp": {
                    "gte": weekly_start
                }
            },
            _sum={
                "cost": True
            }
        )
        weekly_cost = weekly_cost_record._sum.cost or 0.0
        
        # Calcular custos mensais (últimos 30 dias)
        monthly_start = datetime.now() - timedelta(days=30)
        monthly_cost_record = await db.usagerecord.aggregate(
            where={
                **where,
                "timestamp": {
                    "gte": monthly_start
                }
            },
            _sum={
                "cost": True
            }
        )
        monthly_cost = monthly_cost_record._sum.cost or 0.0
        
        # Obter principais recursos por custo
        top_features_result = await db.usagerecord.group_by(
            by=["feature"],
            where=where,
            aggregates={
                "_sum": {
                    "cost": True
                }
            },
            having={
                "_sum": {
                    "cost": {
                        "gt": 0
                    }
                }
            },
            order_by={
                "_sum": {
                    "cost": "desc"
                }
            },
            take=5
        )
        
        top_features = [
            {
                "feature": item.feature,
                "total_cost": item._sum.cost or 0.0
            }
            for item in top_features_result
        ]
        
        # Obter uso por recurso
        usage_by_feature_result = await db.usagerecord.group_by(
            by=["feature"],
            where=where,
            aggregates={
                "_sum": {
                    "cost": True
                },
                "_count": True
            }
        )
        
        usage_by_feature = {
            item.feature: {
                "total_cost": item._sum.cost or 0.0,
                "usage_count": item._count
            }
            for item in usage_by_feature_result
        }
        
        return CostDashboard(
            total_cost=total_cost,
            daily_cost=daily_cost,
            weekly_cost=weekly_cost,
            monthly_cost=monthly_cost,
            top_features=top_features,
            usage_by_feature=usage_by_feature
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching cost dashboard: {str(e)}")

@router.get("/history/", response_model=CostHistory)
async def get_cost_history(
    skip: int = 0,
    limit: int = 100,
    organization_id: int = None,
    feature: str = None,
    start_date: str = None,
    end_date: str = None,
    current_user: UserModel = Depends(get_current_user),
    db: Prisma = Depends(get_db)
):
    """Obter histórico de custos"""
    try:
        # Construir condição WHERE
        where = {}
        
        # Filtrar por organização
        if organization_id:
            # Verificar se o usuário tem acesso à organização
            if current_user.role != "admin":
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
                        detail="Not enough permissions to access cost data for this organization"
                    )
            
            where["organizationId"] = organization_id
        else:
            # Para usuários não administradores, mostrar apenas seus próprios custos
            if current_user.role != "admin":
                where["userId"] = current_user.id
        
        # Filtrar por recurso
        if feature:
            where["feature"] = feature
        
        # Filtrar por datas
        date_filters = {}
        if start_date:
            date_filters["gte"] = datetime.fromisoformat(start_date)
        if end_date:
            date_filters["lte"] = datetime.fromisoformat(end_date)
        
        if date_filters:
            where["timestamp"] = date_filters
        
        # Buscar registros
        db_records = await db.usagerecord.find_many(
            where=where,
            skip=skip,
            take=limit,
            order={
                "timestamp": "desc"
            }
        )
        
        records = [
            UsageRecord(
                id=record.id,
                userId=record.userId,
                organizationId=record.organizationId,
                feature=record.feature,
                tokens_used=record.tokens_used,
                cost=record.cost,
                timestamp=record.timestamp
            )
            for record in db_records
        ]
        
        # Calcular total de registros (para paginação)
        total_records = await db.usagerecord.count(where=where)
        
        # Calcular custo total
        total_cost_record = await db.usagerecord.aggregate(
            where=where,
            _sum={
                "cost": True
            }
        )
        total_cost = total_cost_record._sum.cost or 0.0
        
        return CostHistory(
            records=records,
            total_records=total_records,
            total_cost=total_cost
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching cost history: {str(e)}")