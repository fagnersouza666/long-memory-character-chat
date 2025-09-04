from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, models

api_router = APIRouter()

# Incluir endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(models.router, prefix="/models", tags=["models"])