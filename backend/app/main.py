from fastapi import FastAPI
from app.api.v1.api import api_router

app = FastAPI(title="Sistema RAG Empresarial")

# Incluir rotas da API
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Sistema RAG Empresarial - Backend API"}