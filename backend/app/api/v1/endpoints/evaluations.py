from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from prisma import Prisma
from datetime import datetime

from app.schemas.evaluation import Evaluation, EvaluationCreate, EvaluationUpdate
from app.core.security import get_current_user
from app.models.user import User as UserModel
from app.database.session import get_db

router = APIRouter()

@router.post("/", response_model=Evaluation)
async def create_evaluation(
    evaluation: EvaluationCreate,
    current_user: UserModel = Depends(get_current_user),
    db: Prisma = Depends(get_db)
):
    """Criar uma nova avaliação de funcionário"""
    try:
        # Verificar se o usuário tem permissão para criar avaliações
        # Apenas administradores e gerentes podem criar avaliações
        if current_user.role not in ["admin", "manager"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to create evaluations"
            )
        
        # Verificar se o funcionário existe
        employee = await db.user.find_unique(
            where={
                "id": evaluation.employeeId
            }
        )
        
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        # Verificar se o usuário tem permissão para avaliar este funcionário
        # Se o usuário for gerente, verificar se o funcionário pertence ao mesmo departamento
        if current_user.role == "manager":
            if current_user.department != employee.department:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Managers can only evaluate employees in their department"
                )
        
        # Criar avaliação
        db_evaluation = await db.evaluation.create(
            data={
                "employeeId": evaluation.employeeId,
                "evaluatorId": current_user.id,
                "period": evaluation.period,
                "content": evaluation.content,
                "score": evaluation.score
            }
        )
        
        # Adicionar ao sistema RAG (simplificado - na implementação completa, isso seria feito de forma assíncrona)
        # await add_evaluation_to_rag_system(db_evaluation)
        
        return db_evaluation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating evaluation: {str(e)}")

@router.get("/", response_model=List[Evaluation])
async def list_evaluations(
    skip: int = 0,
    limit: int = 100,
    employee_id: Optional[int] = None,
    period: Optional[str] = None,
    current_user: UserModel = Depends(get_current_user),
    db: Prisma = Depends(get_db)
):
    """Listar avaliações"""
    try:
        # Construir condição WHERE
        where = {}
        
        # Filtrar por funcionário
        if employee_id is not None:
            # Verificar permissões
            if current_user.role in ["admin"]:
                # Administradores podem ver todas as avaliações
                where["employeeId"] = employee_id
            elif current_user.role == "manager":
                # Gerentes podem ver avaliações de funcionários do mesmo departamento
                employee = await db.user.find_unique(
                    where={
                        "id": employee_id
                    }
                )
                
                if not employee or employee.department != current_user.department:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Managers can only view evaluations of employees in their department"
                    )
                
                where["employeeId"] = employee_id
            else:
                # Funcionários comuns só podem ver suas próprias avaliações
                if employee_id != current_user.id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Employees can only view their own evaluations"
                    )
                
                where["employeeId"] = employee_id
        else:
            # Se não especificar funcionário, filtrar por permissões
            if current_user.role in ["admin"]:
                # Administradores podem ver todas as avaliações
                pass
            elif current_user.role == "manager":
                # Gerentes podem ver avaliações de funcionários do mesmo departamento
                employees_in_dept = await db.user.find_many(
                    where={
                        "department": current_user.department
                    }
                )
                
                employee_ids = [emp.id for emp in employees_in_dept]
                where["employeeId"] = {"in": employee_ids}
            else:
                # Funcionários comuns só podem ver suas próprias avaliações
                where["employeeId"] = current_user.id
        
        # Filtrar por período
        if period:
            where["period"] = period
        
        # Buscar avaliações
        evaluations = await db.evaluation.find_many(
            where=where,
            skip=skip,
            take=limit,
            order={
                "createdAt": "desc"
            }
        )
        
        return evaluations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing evaluations: {str(e)}")

@router.get("/{evaluation_id}", response_model=Evaluation)
async def get_evaluation(
    evaluation_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Prisma = Depends(get_db)
):
    """Obter detalhes de uma avaliação"""
    try:
        # Buscar avaliação
        db_evaluation = await db.evaluation.find_unique(
            where={
                "id": evaluation_id
            }
        )
        
        if not db_evaluation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evaluation not found"
            )
        
        # Verificar permissões
        if current_user.role in ["admin"]:
            # Administradores podem ver qualquer avaliação
            pass
        elif current_user.role == "manager":
            # Gerentes podem ver avaliações de funcionários do mesmo departamento
            employee = await db.user.find_unique(
                where={
                    "id": db_evaluation.employeeId
                }
            )
            
            if not employee or employee.department != current_user.department:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Managers can only view evaluations of employees in their department"
                )
        else:
            # Funcionários comuns só podem ver suas próprias avaliações
            if db_evaluation.employeeId != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Employees can only view their own evaluations"
                )
        
        return db_evaluation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching evaluation: {str(e)}")

@router.put("/{evaluation_id}", response_model=Evaluation)
async def update_evaluation(
    evaluation_id: int,
    evaluation_update: EvaluationUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: Prisma = Depends(get_db)
):
    """Atualizar uma avaliação"""
    try:
        # Buscar avaliação
        db_evaluation = await db.evaluation.find_unique(
            where={
                "id": evaluation_id
            }
        )
        
        if not db_evaluation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evaluation not found"
            )
        
        # Verificar permissões
        # Apenas o avaliador original ou administradores podem atualizar
        if current_user.role != "admin" and db_evaluation.evaluatorId != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the original evaluator or administrators can update this evaluation"
            )
        
        # Verificar se a avaliação não é muito antiga (opcional - implementação de política)
        # Por exemplo, não permitir atualização de avaliações com mais de 30 dias
        # days_since_creation = (datetime.now() - db_evaluation.createdAt).days
        # if days_since_creation > 30 and current_user.role != "admin":
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="Cannot update evaluations older than 30 days"
        #     )
        
        # Atualizar avaliação
        update_data = evaluation_update.dict(exclude_unset=True)
        updated_evaluation = await db.evaluation.update(
            where={
                "id": evaluation_id
            },
            data={
                **update_data,
                "updatedAt": datetime.now()
            }
        )
        
        return updated_evaluation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating evaluation: {str(e)}")

@router.delete("/{evaluation_id}", response_model=Evaluation)
async def delete_evaluation(
    evaluation_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Prisma = Depends(get_db)
):
    """Excluir uma avaliação"""
    try:
        # Buscar avaliação
        db_evaluation = await db.evaluation.find_unique(
            where={
                "id": evaluation_id
            }
        )
        
        if not db_evaluation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evaluation not found"
            )
        
        # Verificar permissões
        # Apenas o avaliador original ou administradores podem excluir
        if current_user.role != "admin" and db_evaluation.evaluatorId != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the original evaluator or administrators can delete this evaluation"
            )
        
        # Excluir avaliação
        deleted_evaluation = await db.evaluation.delete(
            where={
                "id": evaluation_id
            }
        )
        
        return deleted_evaluation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting evaluation: {str(e)}")