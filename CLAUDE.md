# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a comprehensive Enterprise RAG (Retrieval-Augmented Generation) system with multiple components:

- **Backend API**: FastAPI-based REST API with PostgreSQL + Prisma ORM + pgvector for semantic search
- **Frontend Applications**: Three Streamlit applications for different use cases
- **Multi-tenant Architecture**: Organization/workspace structure with role-based access control
- **Document Processing**: Asynchronous processing with support for PDF, DOCX, TXT files
- **Employee Evaluation System**: Built-in performance evaluation and feedback management

## Development Commands

### Backend API Server
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Streamlit Applications
```bash
# Enterprise RAG System (main application)
streamlit run rag_app.py

# Second Brain System (knowledge management)
streamlit run second_brain_app.py

# AI Agent Chat (character-based conversations)
streamlit run aiagent.py
```

### Testing
```bash
cd backend
pytest                    # Run all tests
pytest tests/test_auth.py  # Run specific test file
```

### Database Operations
```bash
cd backend

# Generate and run migrations
npx prisma migrate dev --name description_of_changes

# Reset database and apply all migrations
npx prisma migrate reset

# Initialize models data
python setup_models.py

# Test database connection
python test_db.py
```

### Dependencies
```bash
# Backend dependencies
cd backend && pip install -r requirements.txt

# Root-level dependencies (for Streamlit apps)
pip install -r requirements.txt

# Prisma client generation
cd backend && npx prisma generate
```

## Architecture Overview

### Backend Structure (`backend/`)
- **API Endpoints** (`app/api/v1/endpoints/`): RESTful endpoints for all system functionality
  - `auth.py`: Authentication and user management
  - `documents.py`: Document upload and management
  - `memory.py`: Long-term memory and conversation history
  - `search.py`: Semantic search capabilities
  - `evaluations.py`: Employee evaluation system
  - `workspaces.py`, `organizations.py`: Multi-tenant structure
- **Core** (`app/core/`): Configuration and security utilities
- **Models** (`app/models/`): Prisma ORM models
- **Schemas** (`app/schemas/`): Pydantic validation schemas

### RAG Components (`rag_components/`)
Shared functionality across Streamlit applications:
- `rag_agent.py`: Main RAG orchestration and AI model integration
- `document_processor.py`: Document parsing and chunking
- `faiss_manager.py`: FAISS vector database management
- `query_processor.py`: Query understanding and enhancement
- `evaluation_manager.py`: Performance evaluation workflows
- `auth.py`: Authentication for Streamlit apps

### Database Schema
Multi-tenant PostgreSQL schema with:
- **Users**: Authentication and role management
- **Organizations/Workspaces**: Hierarchical tenant structure
- **Documents/DocumentChunks**: File storage with vector embeddings
- **Evaluations**: Employee performance tracking
- **Models**: AI model configuration management

## Environment Setup

Required environment variables:
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/rag_enterprise
SHADOW_DATABASE_URL=postgresql://user:password@localhost:5432/rag_enterprise_shadow

# Authentication
SECRET_KEY=your_jwt_secret_key
ADMIN_PASSWORD=secure_admin_password

# AI Service APIs
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_key
ANTHROPIC_API_KEY=your_anthropic_key
MISTRAL_API_KEY=your_mistral_key
```

## Key Development Patterns

### Multi-Model AI Support
The system supports multiple AI providers (OpenAI, Google, Anthropic, Mistral) with dynamic model selection based on user preferences and workspace configuration.

### Async Document Processing
Documents are processed asynchronously using background tasks. Check processing status via the API before querying processed content.

### Vector Search Integration
Uses pgvector extension for PostgreSQL to store and query document embeddings. FAISS is used for local vector operations in Streamlit apps.

### Role-Based Access Control
Three-tier access control: Organization → Workspace → Document level permissions with roles: admin, manager, employee.

## Testing Strategy

Comprehensive test suite covers:
- Authentication flows and JWT token validation
- Document upload and processing workflows
- Multi-tenant data isolation
- API endpoint functionality and error handling
- Database migrations and schema validation

## Common Workflows

### Adding a New API Endpoint
1. Create endpoint in appropriate `app/api/v1/endpoints/` file
2. Add Pydantic schemas in `app/schemas/`
3. Update database models in `prisma/schema.prisma` if needed
4. Write tests in corresponding `tests/test_*.py` file
5. Run migrations if schema changed

### Adding New AI Model Support
1. Update model configuration in `app/schemas/model.py`
2. Add model initialization in `setup_models.py`
3. Implement model-specific logic in RAG components
4. Test with different model providers