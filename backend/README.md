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
│   │   └── token.py
│   ├── database/
│   │   ├── __init__.py
│   │   └── session.py
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
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

3. Iniciar servidor:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```