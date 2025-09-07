# Plano 3 — Execução dos Testes do Backend

Objetivo: instalar ferramentas de teste no venv do backend e executar a suíte de testes em `backend/tests` usando Python 3.12.

## Pré‑requisitos
- Ambiente virtual do backend criado e ativo (`backend/.venv`).
- Dependências do backend instaladas (FastAPI, Prisma, etc.).
- Prisma Client gerado (`cd backend && prisma generate`).
- Variáveis em `.env` já configuradas; `DATABASE_URL` acessível.

## Passos
1) Ativar o venv do backend
- `cd backend`
- `source .venv/bin/activate`

2) Instalar ferramentas de teste
- `pip install pytest`
- (Se necessário após primeira execução) `pip install pytest-asyncio httpx`

3) Executar a suíte de testes
- `python -m pytest -q`

4) Registrar saída e diagnosticar
- Anotar testes falhos/erros e mensagens.
- Se falhar por client Prisma não gerado, rodar `prisma generate`.
- Se falhar por import assíncrono, instalar `pytest-asyncio`.

## Observações
- Sem comandos destrutivos. Apenas instalação de pacotes no venv do backend.
- Após correções, reexecutar: `python -m pytest -q`.
