# Long Memory Character Chat — RAG Empresarial

Streamlit apps and a FastAPI backend for a long‑memory chat agent and an enterprise RAG (Retrieval‑Augmented Generation) workflow. The UI lives at the repo root (`app.py`, `rag_app.py`); the API is under `backend/` with Prisma + PostgreSQL.

## Quick Start
- Prereqs: Python 3.9+, PostgreSQL (for backend), optional Node.js (for Prisma dev tooling).
- Copy env: `cp .env.example .env` and set API keys and `ADMIN_PASSWORD`.

UI (root):
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py        # chat UI
# or
streamlit run rag_app.py    # enterprise RAG UI
```

Backend (API):
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql://user:pass@localhost:5432/rag_enterprise
uvicorn app.main:app --reload
```

## Tests
- Backend tests: `cd backend && pytest -q`

## Project Structure
- `aiagent.py`, `rag_components/`: Core agent, FAISS, document and auth utilities.
- `backend/app/api/v1/endpoints/`: FastAPI routes; Prisma schema in `backend/prisma/`.
- `docs/`: Architecture, product docs and examples.

## Contributing
See AGENTS.md for coding style, commands, and PR guidelines.
