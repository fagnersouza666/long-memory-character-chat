# Plano 6 — Subir container PostgreSQL para desenvolvimento

Objetivo: disponibilizar um PostgreSQL local via Docker para o backend (Prisma), incluindo DB de shadow para migrações.

## Passos
1) Adicionar `backend/docker-compose.yml` com serviço `db` (PostgreSQL 16), volume nomeado e healthcheck.
2) Adicionar `backend/docker/initdb.d/init.sql` para criar o DB `rag_enterprise_shadow` na inicialização do container.
3) Ajustar `backend/.env` para apontar para o container:
   - `DATABASE_URL=postgresql://rag:rag@localhost:5432/rag_enterprise`
   - `SHADOW_DATABASE_URL=postgresql://rag:rag@localhost:5432/rag_enterprise_shadow`
4) Subir container: `cd backend && docker compose up -d db` (ou `docker-compose up -d db`).
5) Rodar migrações: `prisma migrate dev`.
6) Executar testes: `python -m pytest -q`.

Notas
- Sem comandos destrutivos. Usamos volume nomeado `pgdata` para persistir dados.
- Caso `docker compose` não exista, usar `docker-compose`.
