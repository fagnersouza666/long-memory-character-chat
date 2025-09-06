from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, models, organizations, workspaces, documents, evaluations, search, memory, costs, rate_limits, document_processing

api_router = APIRouter()

# Incluir endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(models.router, prefix="/models", tags=["models"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
api_router.include_router(workspaces.router, prefix="/workspaces", tags=["workspaces"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(evaluations.router, prefix="/evaluations", tags=["evaluations"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(memory.router, prefix="/memory", tags=["memory"])
api_router.include_router(costs.router, prefix="/costs", tags=["costs"])
api_router.include_router(rate_limits.router, prefix="/rate-limits", tags=["rate_limits"])
api_router.include_router(document_processing.router, prefix="/document-processing", tags=["document_processing"])