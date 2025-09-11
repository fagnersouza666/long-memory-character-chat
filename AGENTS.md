# Repository Guidelines

This guide helps contributors work efficiently on the Streamlit chat app and FastAPI backend. It covers structure, setup, commands, style, testing, and PR expectations specific to this repo.

## Project Structure & Module Organization
- `app.py` / `rag_app.py`: Streamlit apps (chat agent and enterprise RAG UI).
- `aiagent.py`, `rag_components/`: Core chat/RAG logic, document processing, auth, FAISS.
- `backend/`: FastAPI + Prisma (PostgreSQL). Routes in `backend/app/api/v1/endpoints/`.
- `docs/`: Architecture/product docs; seeds and examples in subfolders.
- `.env.example`: Copy to `.env` and set required keys.

## Build, Test, and Development Commands
UI (Streamlit):
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py        # chat UI
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
Prisma (when editing schema):
```bash
cd backend && npx prisma migrate dev
```
Tests (backend):
```bash
cd backend && pytest -q
```

## Coding Style & Naming Conventions
- Python: PEP 8, 4 spaces; type hints encouraged.
- Names: `snake_case` (functions/modules), `PascalCase` (classes), `UPPER_SNAKE` (constants).
- FastAPI: Endpoints under `backend/app/api/v1/endpoints/` with clear tags; schemas in `schemas/`; DB access in `models/` and `database/`.
- Streamlit: Use `st.session_state`; keep UI thin and delegate to `rag_components/`.

## Testing Guidelines
- Frameworks: `pytest` for functional tests; some `unittest` for classes.
- Location: `backend/tests/` with files named `test_*.py`.
- Expectations: cover auth, models, organizations, workspaces, memory, search. Add tests for new endpoints and bug fixes.

## Commit & Pull Request Guidelines
- Commits: Conventional Commits (e.g., `feat(api): add search route`, `fix(app): avoid None session`, `refactor(auth): simplify token checks`).
- PRs: Include purpose, linked issues, concise changelog, and testing steps (Streamlit/UVicorn commands). Add screenshots/GIFs for UI changes.

## Security & Configuration
- Copy `.env.example` to `.env`; set `OPENAI_API_KEY`, `GOOGLE_API_KEY`, `ANTHROPIC_API_KEY`, `CHAT_NSFW_PASSWORD`, `ADMIN_PASSWORD`, `DATABASE_URL` (backend).
- Never commit secrets. Use role-based checks for admin-only endpoints and validate inputs on all APIs.

