# Backend - Sistema RAG Empresarial

## Estrutura do Projeto

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── endpoints/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py
│   │   │   │   └── users.py
│   │   │   └── api.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── security.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── token.py
│   │   └── model.py
│   ├── database/
│   │   ├── __init__.py
│   │   └── session.py
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
├── prisma/
│   ├── migrations/
│   │   ├── 20250901180926_init/
│   │   ├── 20250902141024_add_vector_support/
│   │   └── 20250904150000_add_model_table/
│   └── schema.prisma
├── tests/
│   └── ...
├── requirements.txt
└── README.md
```

## Configuração Inicial

1. Instalar dependências:
   ```bash
   pip install -r requirements.txt
   ```

2. Configurar variáveis de ambiente:
   ```bash
   # Database
   DATABASE_URL=postgresql://user:password@localhost:5432/rag_enterprise

   # JWT
   SECRET_KEY=chave_secreta_forte_para_jwt
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30

   # Admin User
   ADMIN_PASSWORD=admin123
   ```

3. Criar as tabelas no banco de dados:
   ```bash
   # Execute o script de migração manualmente ou use:
   # (Instruções específicas dependem do seu ambiente de banco de dados)
   ```

4. Configurar os modelos disponíveis:
   ```bash
   # Executar o script para inserir os modelos padrão:
   python setup_models.py
   ```

5. Iniciar servidor:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```