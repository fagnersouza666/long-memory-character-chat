# Plano 2 — Execução do Setup e Validação

Este plano executa os passos do `planos/1.md` de forma sequencial.

1) Preparar venv da UI (raiz)
- Comandos:
  - `python -m venv .venv`
  - `source .venv/bin/activate`
  - `pip install -r requirements.txt`

2) Preparar venv do Backend
- Comandos:
  - `cd backend`
  - `python -m venv .venv`
  - `source .venv/bin/activate`
  - `pip install -r requirements.txt`

3) Configurar variáveis de ambiente
- Ações:
  - Definir `DATABASE_URL=postgresql://user:pass@localhost:5432/rag_enterprise` (ajustar conforme seu banco).

4) Iniciar Backend (validação rápida)
- Comandos:
  - `cd backend`
  - `source .venv/bin/activate`
  - `uvicorn app.main:app --reload`

5) Iniciar UI (validação rápida)
- Comandos:
  - `source .venv/bin/activate`
  - `streamlit run app.py` (ou `streamlit run rag_app.py`)

6) Executar testes do Backend
- Comandos:
  - `cd backend`
  - `source .venv/bin/activate`
  - `pytest -q`

Observações
- Sem comandos destrutivos. Requer sua confirmação para instalar dependências e criar/alterar `.env`.
