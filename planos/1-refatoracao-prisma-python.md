# Plano 1 — Refatoração incremental (Prisma Python)

1) Diagnóstico rápido
- Mapear rotas, modelos Prisma, dependências e acoplamentos entre UI/RAG/backend.

2) Settings centralizado (sem novas libs)
- Criar `backend/app/core/settings.py` usando `os.getenv`, carregar `.env` se existir; expor `get_settings()`.

3) Ciclo de vida do Prisma
- Criar `backend/app/core/db.py` com cliente Prisma único (init no lifespan) e injeção simples para repositórios.

4) Logging + request_id
- Middleware no FastAPI com `uuid4`, logs estruturados via `logging` padrão; níveis consistentes.

5) Tratamento global de erros
- Handlers para `HTTPException`/erros de validação e resposta padrão `{data, error}`.

6) Camadas `repositories/` e `services/`
- Introduzir pastas; mover 1 fluxo crítico das rotas para `services/` e acesso a BD para `repositories/` (Prisma Python).

7) Schemas consistentes
- Separar DTOs: `Create/Update/Read` para a entidade escolhida; validações claras.

8) RAG modular
- Definir interfaces mínimas (`Embedder`, `VectorStore`, `Retriever`); isolar FAISS/chunking em `rag_components/`; cache simples por `document_id+model`.

9) Streamlit enxuto
- Encapsular `st.session_state`; criar cliente HTTP central; ajustar 1 chamada para usar a camada de serviço do backend.

10) Testes confiáveis
- Fixtures (`settings`, `client` HTTPX, `db` de teste), rollback por teste; cobrir a rota/serviço refatorados.

11) Qualidade
- Integrar `pre-commit` com `ruff`, `black`, `mypy` se já existirem; caso contrário, solicitar aprovação antes de adicionar.

Critérios
- Mudanças pequenas e iterativas; após cada etapa, rodar `pytest -q` no backend e ajustar.

