# Repository Guidelines

## Project Structure & Module Organization
- `app.py` / `rag_app.py`: Streamlit apps (chat agent and enterprise RAG UI).
- `aiagent.py` and `rag_components/`: Core chat/RAG logic, document processing, auth, FAISS.
- `backend/`: FastAPI API with Prisma (PostgreSQL). Routes in `backend/app/api/v1/endpoints/`.
- `docs/`: Architecture and product docs; seeds and examples in subfolders.
- `.env.example`: Required environment variables; copy to `.env`.

## Build, Test, and Development Commands
- Python env setup (root UI):
  ```bash
  python -m venv .venv && source .venv/bin/activate
  pip install -r requirements.txt
  streamlit run app.py        # chat UI
  streamlit run rag_app.py    # enterprise RAG UI
  ```
- Backend setup (API):
  ```bash
  cd backend
  python -m venv .venv && source .venv/bin/activate
  pip install -r requirements.txt
  export DATABASE_URL=postgresql://user:pass@localhost:5432/rag_enterprise
  uvicorn app.main:app --reload
  ```
- Prisma (optional, when editing schema):
  ```bash
  cd backend && npx prisma migrate dev
  ```
- Tests (backend):
  ```bash
  cd backend && pytest -q
  ```

## Coding Style & Naming Conventions
- Python: PEP 8, 4-space indent, type hints encouraged.
- Names: `snake_case` for modules/functions, `PascalCase` for classes, `UPPER_SNAKE` for constants.
- FastAPI: group endpoints under `backend/app/api/v1/endpoints/` with clear tags; keep schemas in `schemas/` and DB access in `models/`/`database/`.
- Streamlit: maintain state in `st.session_state`; keep UI logic thin and delegate to `rag_components/`.

## Testing Guidelines
- Frameworks: pytest (functional), unittest (some classes).
- Location: `backend/tests/` with files named `test_*.py`.
- Expectations: cover critical paths (auth, models, organizations, workspaces, memory, search). No strict coverage gate; add tests for new endpoints and bug fixes.

## Commit & Pull Request Guidelines
- Commits: follow Conventional Commits (e.g., `feat(api): ...`, `fix(app): ...`, `refactor(auth): ...`).
- PRs: include purpose, linked issues, concise changelog, and testing steps (commands for Streamlit/UVicorn). Add screenshots/GIFs for UI changes.

## Security & Configuration
- Copy `.env.example` to `.env` and set: `OPENAI_API_KEY`, `GOOGLE_API_KEY`, `ANTHROPIC_API_KEY`, `CHAT_NSFW_PASSWORD`, `ADMIN_PASSWORD`, and `DATABASE_URL` (backend).
- Do not commit secrets. Use role-based checks for admin-only endpoints and validate inputs on all APIs.

