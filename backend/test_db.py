import asyncio
from prisma import Prisma

async def main():
    # Inicializar o cliente Prisma
    prisma = Prisma()
    
    try:
        # Conectar ao banco de dados
        await prisma.connect()
        print("Conexão com o banco de dados estabelecida com sucesso!")
        
        # Testar uma consulta simples
        users = await prisma.user.find_many()
        print(f"Número de usuários encontrados: {len(users)}")
        
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
    finally:
        # Desconectar do banco de dados
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(main())