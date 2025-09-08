# Plano 5 — Preparar Banco de Dados (PostgreSQL + Prisma)

Objetivo: deixar o backend pronto para migrar o schema e rodar os testes que dependem de banco.

1) Validar variáveis de ambiente do backend
- Necessário: `DATABASE_URL` e `SHADOW_DATABASE_URL` (PostgreSQL). Ex.:
  - `DATABASE_URL=postgresql://user:pass@localhost:5432/rag_enterprise`
  - `SHADOW_DATABASE_URL=postgresql://user:pass@localhost:5432/rag_enterprise_shadow`

2) Criar arquivo `backend/.env` (se ausente)
- Copiar ou criar apenas com as duas variáveis acima (sem expor segredos em logs/commits).

3) Verificar conexão
- Opcional: `psql`/`createdb` (se disponíveis) para criar bases `rag_enterprise` e `rag_enterprise_shadow`.
- Alternativa: garantir que o usuário já possui as bases criadas.

4) Rodar migrações Prisma
- `cd backend && source .venv/bin/activate`
- `prisma migrate dev` (ou `prisma db push` se não houver migrations).

5) Seed de modelos (opcional)
- `python setup_models.py` para popular a tabela de modelos.

6) Validar com testes
- `python -m pytest -q` no `backend`.

Observações
- Sem comandos destrutivos; apenas criação de `.env`, migrações e seed.
- Será solicitada confirmação antes de criar/alterar arquivos e executar comandos.
