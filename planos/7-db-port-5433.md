# Plano 7 — Evitar conflito da porta 5432 sem ações destrutivas

Contexto: A porta 5432 já está em uso por outro Postgres. Pelas regras, não executaremos ações destrutivas (ex.: remover todos containers). Ajustaremos a porta do container deste projeto.

Passos
1) Atualizar `backend/docker-compose.yml` para usar `ports: ["5433:5432"]`.
2) Atualizar `backend/.env` para apontar para `localhost:5433` em `DATABASE_URL` e `SHADOW_DATABASE_URL`.
3) Subir o container do banco: `cd backend && docker compose up -d db`.
4) Aguardar healthcheck ficar `healthy`.
5) Rodar migrações Prisma: `prisma migrate dev`.
6) Executar testes: `python -m pytest -q`.

Observações
- Sem remoção de containers existentes.
- Caso prefira, podemos apenas parar o Postgres conflitante ao invés de mudar porta.
