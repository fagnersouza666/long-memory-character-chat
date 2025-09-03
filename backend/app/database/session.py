# Configuração da sessão do banco de dados
# Esta implementação foi atualizada para usar o Prisma ORM

from prisma import Prisma

# Instância global do cliente Prisma
prisma = Prisma()

async def connect_to_database():
    """Conectar ao banco de dados usando Prisma"""
    await prisma.connect()

async def disconnect_from_database():
    """Desconectar do banco de dados"""
    await prisma.disconnect()

async def get_db():
    """Dependência para obter a sessão do banco de dados"""
    await connect_to_database()
    try:
        yield prisma
    finally:
        await disconnect_from_database()