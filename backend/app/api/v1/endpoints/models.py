from fastapi import APIRouter, HTTPException
from typing import List
import asyncio
from prisma import Prisma

from backend.app.schemas.model import Model

router = APIRouter()

@router.get("/", response_model=List[Model])
async def read_models():
    """Retorna a lista de modelos ativos com seus prompts associados"""
    try:
        # Criar uma nova instância do Prisma para esta operação
        db = Prisma()
        await db.connect()
        
        try:
            # Buscar todos os modelos ativos
            models = await db.model.find_many(where={"isActive": True})
            return models
        finally:
            # Certificar-se de desconectar o banco de dados
            await db.disconnect()
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar modelos: {str(e)}")