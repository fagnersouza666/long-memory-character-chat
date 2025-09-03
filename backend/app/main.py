from fastapi import FastAPI
from app.api.v1.api import api_router
from app.database.session import connect_to_database, disconnect_from_database

app = FastAPI(title="Sistema RAG Empresarial")

# Eventos de lifecycle da aplicação
@app.on_event("startup")
async def startup_event():
    """Conectar ao banco de dados na inicialização da aplicação"""
    await connect_to_database()

@app.on_event("shutdown")
async def shutdown_event():
    """Desconectar do banco de dados ao encerrar a aplicação"""
    await disconnect_from_database()

# Incluir rotas da API
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Sistema RAG Empresarial - Backend API"}