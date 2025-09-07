# Configuração da sessão do banco de dados
# Esta implementação foi atualizada para usar o Prisma ORM

from prisma import Prisma

# Instância global do cliente Prisma
prisma = Prisma()

async def connect_to_database():
    """Conectar ao banco de dados usando Prisma"""
    if not prisma.is_connected():
        await prisma.connect()

async def disconnect_from_database():
    """Desconectar do banco de dados"""
    await prisma.disconnect()

async def get_db():
    """Dependência para obter a sessão do banco de dados"""
    # Usar a conexão global estabelecida no startup da aplicação
    yield prisma