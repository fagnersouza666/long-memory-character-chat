# PRD - Sistema RAG Empresarial v2.0
**Product Requirements Document**

---

## 1. VISÃO EXECUTIVA

### 1.1 Declaração do Problema
O sistema RAG atual, embora funcional como protótipo, possui limitações críticas para ambientes de produção:
- Arquitetura monolítica baseada em Streamlit que não suporta múltiplos usuários concorrentes
- Isolamento de dados inadequado entre departamentos/organizações
- Processamento síncrono que causa timeouts e experiência de usuário ruim
- Banco SQLite inadequado para alta concorrência
- Falta de escalabilidade e separação de responsabilidades
- **Ausência de isolamento granular** dentro de organizações (ex: Jurídico vs Marketing)

### 1.2 Visão do Produto
Transformar o sistema RAG em uma **plataforma empresarial multi-tenant com workspaces isolados, escalável e segura** que permita:
- Gestão de conhecimento organizacional com **isolamento total** entre organizações e workspaces
- **Workspaces administrativamente isolados** dentro da mesma organização
- Experiência de usuário responsiva com processamento assíncrono
- **Busca híbrida** (semântica + palavra-chave) para máxima flexibilidade
- Arquitetura desacoplada pronta para escalar
- Segurança enterprise-grade com controle granular de acesso
- **Gestão de custos** transparente para tenants

### 1.3 Objetivos de Negócio
- **Performance**: Reduzir tempo de resposta em 80% através do processamento assíncrono
- **Segurança**: 100% de isolamento de dados entre organizações e workspaces
- **Escalabilidade**: Suportar até 1000 usuários concorrentes por instância
- **Confiabilidade**: 99.9% de uptime com arquitetura robusta
- **Rentabilidade**: Controle e transparência total de custos de API por tenant

---

## 2. CONTEXTO E JUSTIFICATIVA

### 2.1 Análise da Arquitetura Atual
**Pontos Fortes Mantidos:**
- Lógica de RAG bem estruturada
- Componentes de negócio claros (RAGAgent, DocumentProcessor, EvaluationManager)
- Interface de usuário funcional

**Limitações Críticas Resolvidas:**
- Streamlit como backend → API REST separada
- SQLite → PostgreSQL com pgvector
- Processamento síncrono → Sistema de filas assíncronas
- FAISS centralizado → Banco vetorial multi-tenant com workspaces
- **Isolamento simples → Workspaces administrativamente isolados**
- **Busca apenas semântica → Busca híbrida (semântica + palavra-chave)**
- **Custos ocultos → Dashboard transparente de custos**

### 2.2 Impacto no Negócio
- **ROI Esperado**: Redução de 60% no tempo de busca por informações
- **Segurança**: Compliance com GDPR/LGPD através do isolamento em camadas
- **Produtividade**: Suporte a 10x mais usuários simultâneos
- **Manutenibilidade**: Arquitetura modular facilita atualizações
- **Controle Financeiro**: Previsibilidade e transparência de custos operacionais

---

## 3. ESPECIFICAÇÕES TÉCNICAS

### 3.1 Nova Arquitetura do Sistema

```
┌─────────────────┐    ┌─────────────────────────────────────┐
│   Frontend      │    │            Backend API              │
│                 │    │                                     │
│  ┌─────────────┐│    │ ┌─────────────┐ ┌─────────────────┐ │
│  │ Streamlit   ││────│▶│ FastAPI     │ │ RAG Components  │ │
│  │   Client    ││    │ │ Endpoints   │ │                 │ │
│  └─────────────┘│    │ └─────────────┘ └─────────────────┘ │
│                 │    │                                     │
│  ┌─────────────┐│    │ ┌─────────────┐ ┌─────────────────┐ │
│  │ React       ││    │ │ Auth +      │ │ Business Logic  │ │
│  │ (Futuro)    ││    │ │ Cost Mgmt   │ │ + Hybrid Search │ │
│  └─────────────┘│    │ └─────────────┘ └─────────────────┘ │
└─────────────────┘    └─────────────────────────────────────┘
                                          │
        ┌─────────────────────────────────┼─────────────────────────────────┐
        │                                 ▼                                 │
┌─────────────────┐    ┌─────────────────────────────────────┐    ┌─────────────────┐
│ Task Processing │    │         Data Layer                  │    │   External      │
│                 │    │                                     │    │   Services      │
│ ┌─────────────┐ │    │ ┌─────────────┐ ┌─────────────────┐ │    │                 │
│ │   Celery    │ │    │ │PostgreSQL   │ │ File Storage    │ │    │ ┌─────────────┐ │
│ │   Workers   │ │    │ │+ pgvector   │ │ (S3/Local)      │ │    │ │ OpenAI/     │ │
│ └─────────────┘ │    │ │+ Full-Text  │ │ Multi-Tenant    │ │    │ │ Gemini/     │ │
│                 │    │ └─────────────┘ └─────────────────┘ │    │ │ Claude      │ │
│ ┌─────────────┐ │    │                                     │    │ └─────────────┘ │
│ │ Redis Cache │ │    │ ┌─────────────┐ ┌─────────────────┐ │    │                 │
│ │ + Broker    │ │    │ │ Workspaces  │ │ Hybrid Search   │ │    │ ┌─────────────┐ │
│ └─────────────┘ │    │ │ Isolation   │ │ Engine          │ │    │ │Cost Monitor │ │
└─────────────────┘    │ └─────────────┘ └─────────────────┘ │    │ │ Dashboard   │ │
                       └─────────────────────────────────────┘    │ └─────────────┘ │
                                                                  └─────────────────┘
```

### 3.2 Stack Tecnológica

**Backend API:**
- **FastAPI**: Framework principal para API REST
- **PostgreSQL**: Banco de dados principal
- **pgvector**: Extensão para busca vetorial
- **PostgreSQL Full-Text Search**: Busca por palavra-chave
- **SQLAlchemy**: ORM para abstração do banco
- **Alembic**: Migração de esquemas

**Modelos de IA:**
- **GPT-5-mini**: Modelo padrão para consultas e chat (mais eficiente e econômico)
- **text-embedding-3-small**: Modelo padrão para embeddings
- **Suporte multi-provider**: OpenAI, Anthropic, Google Gemini

**Processamento Assíncrono:**
- **Celery**: Sistema de filas de tarefas
- **Redis**: Message broker, cache e rate limiting
- **Celery Beat**: Agendamento de tarefas

**Frontend:**
- **Streamlit**: Cliente web inicial
- **Preparação para React**: Arquitetura API-first

**Infraestrutura:**
- **Docker**: Containerização
- **Docker Compose**: Orquestração local
- **Nginx**: Proxy reverso
- **Gunicorn**: Servidor WSGI

### 3.3 Modelo de Dados Multi-Tenant com Workspaces

```sql
-- Organizações (Tenants)
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    active BOOLEAN DEFAULT true,
    monthly_cost_limit DECIMAL(10,2), -- Controle de custos
    current_monthly_cost DECIMAL(10,2) DEFAULT 0
);

-- Workspaces dentro de organizações (NOVO)
CREATE TABLE workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true,
    UNIQUE(organization_id, slug)
);

-- Modelos de Embedding suportados (NOVO)
CREATE TABLE embedding_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    provider VARCHAR(50) NOT NULL, -- 'openai', 'cohere', 'huggingface'
    dimension INTEGER NOT NULL,
    cost_per_token DECIMAL(10,8), -- Para cálculo de custos
    is_active BOOLEAN DEFAULT true,
    is_default BOOLEAN DEFAULT false, -- GPT-5-mini será o padrão
    created_at TIMESTAMP DEFAULT NOW()
);

-- Inserir modelo padrão GPT-5-mini
INSERT INTO embedding_models (name, provider, dimension, cost_per_token, is_default, is_active) 
VALUES ('text-embedding-3-small', 'openai', 1536, 0.00000002, true, true);

-- Modelo LLM padrão para consultas
INSERT INTO embedding_models (name, provider, dimension, cost_per_token, is_default, is_active) 
VALUES ('gpt-5-mini', 'openai', 0, 0.000005, true, true); -- 0 dimension for LLM models

-- Usuários com workspace access
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id),
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('super_admin', 'tenant_admin', 'manager', 'employee')),
    created_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true,
    UNIQUE(organization_id, username)
);

-- Relacionamento usuário-workspace (many-to-many)
CREATE TABLE user_workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    workspace_id UUID REFERENCES workspaces(id),
    role VARCHAR(50) NOT NULL CHECK (role IN ('admin', 'member', 'viewer')),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, workspace_id)
);

-- Documentos com isolamento por workspace
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id),
    workspace_id UUID REFERENCES workspaces(id), -- NOVO: Isolamento por workspace
    title VARCHAR(500) NOT NULL,
    file_path VARCHAR(1000) NOT NULL, -- Formato: tenants/{org_id}/workspaces/{ws_id}/documents/{doc_id}/
    file_type VARCHAR(50) NOT NULL,
    file_size BIGINT NOT NULL,
    uploaded_by UUID REFERENCES users(id),
    status VARCHAR(50) DEFAULT 'processing' CHECK (status IN ('processing', 'completed', 'error')),
    embedding_model_id UUID REFERENCES embedding_models(id),
    created_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP,
    error_message TEXT,
    -- Full-text search
    search_vector tsvector GENERATED ALWAYS AS (to_tsvector('portuguese', title || ' ' || COALESCE(content_text, ''))) STORED
);

-- Chunks de documentos com vetores flexíveis
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organizations(id),
    workspace_id UUID REFERENCES workspaces(id), -- NOVO: Isolamento por workspace
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB,
    embedding_model_id UUID REFERENCES embedding_models(id),
    embedding vector, -- Dimensão flexível baseada no modelo
    created_at TIMESTAMP DEFAULT NOW(),
    -- Full-text search
    search_vector tsvector GENERATED ALWAYS AS (to_tsvector('portuguese', content)) STORED
);

-- Índices para busca híbrida
CREATE INDEX idx_chunks_embedding ON document_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX idx_chunks_search ON document_chunks USING gin(search_vector);
CREATE INDEX idx_documents_search ON documents USING gin(search_vector);

-- Conversas com contexto de workspace
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id),
    workspace_id UUID REFERENCES workspaces(id), -- NOVO: Isolamento por workspace
    user_id UUID REFERENCES users(id),
    title VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Mensagens da conversa
CREATE TABLE conversation_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organizations(id),
    workspace_id UUID REFERENCES workspaces(id), -- NOVO: Isolamento por workspace
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Controle de custos por tenant (NOVO)
CREATE TABLE cost_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id),
    workspace_id UUID REFERENCES workspaces(id),
    service_type VARCHAR(50) NOT NULL, -- 'embedding', 'llm_query', 'storage'
    operation_type VARCHAR(50) NOT NULL, -- 'document_processing', 'query', 'chat'
    tokens_used INTEGER,
    cost_usd DECIMAL(10,6),
    created_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB -- Detalhes da operação
);

-- Rate limiting por usuário/tenant (NOVO)
CREATE TABLE rate_limits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id),
    user_id UUID REFERENCES users(id),
    operation_type VARCHAR(50) NOT NULL, -- 'query', 'upload', 'chat'
    count_current INTEGER DEFAULT 0,
    count_limit INTEGER NOT NULL,
    window_start TIMESTAMP DEFAULT NOW(),
    window_duration INTERVAL DEFAULT '1 day'
);

-- Avaliações isoladas por workspace
CREATE TABLE evaluations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id),
    workspace_id UUID REFERENCES workspaces(id), -- NOVO: Isolamento por workspace
    employee_id UUID REFERENCES users(id),
    evaluator_id UUID REFERENCES users(id),
    period VARCHAR(20) NOT NULL,
    score DECIMAL(3,2),
    feedback TEXT,
    goals JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 3.4 Sistema de Armazenamento Multi-Tenant

**Política de Nomenclatura de Arquivos:**
```
Formato S3/Local: 
tenants/{organization_id}/workspaces/{workspace_id}/documents/{document_id}/{original_filename}

Exemplo:
tenants/123e4567-e89b-12d3-a456-426614174000/workspaces/456e7890-e89b-12d3-a456-426614174111/documents/789e0123-e89b-12d3-a456-426614174222/relatorio_anual_2024.pdf
```

**Benefícios:**
- Isolamento físico no nível do sistema de arquivos
- Facilita backup por organização/workspace
- Políticas de acesso granulares no S3
- Auditoria e compliance simplificados

---

## 4. FUNCIONALIDADES E REQUISITOS

### 4.1 Funcionalidades Core (MVP)

#### 4.1.1 Sistema de Autenticação Multi-Nível
**Requisitos Funcionais:**
- [REQ-001] Login/logout com isolamento por organização e workspace
- [REQ-002] Controle de acesso baseado em roles:
  - **Super Admin**: Gestão global do sistema
  - **Tenant Admin**: Gestão completa da organização
  - **Workspace Admin**: Gestão de workspace específico
  - **Manager**: Acesso a múltiplos workspaces
  - **Employee**: Acesso a workspaces específicos
- [REQ-003] Isolamento total de dados entre organizações e workspaces
- [REQ-004] Gestão de usuários e workspaces por tenant admin
- [REQ-005] **Hierarquia de permissões**: O papel no workspace (`user_workspaces.role`) **sempre prevalece** sobre o papel organizacional (`users.role`) dentro daquele workspace específico

**Lógica de Autorização:**
```python
# Exemplo de lógica de autorização
def check_workspace_permission(user_id, workspace_id, required_permission):
    """
    O papel no workspace sempre sobrepõe o papel organizacional
    users.role = permissão MÁXIMA na organização
    user_workspaces.role = permissão ESPECÍFICA no workspace
    """
    
    # 1. Verificar papel específico no workspace
    workspace_role = get_user_workspace_role(user_id, workspace_id)
    if workspace_role:
        return has_permission(workspace_role, required_permission)
    
    # 2. Se não há papel específico, usar papel organizacional
    org_role = get_user_org_role(user_id)
    return has_permission(org_role, required_permission)
```

**Endpoints:**
```
POST /auth/login
POST /auth/logout  
GET  /auth/me
POST /organizations/{org_id}/users
POST /organizations/{org_id}/workspaces
GET  /organizations/{org_id}/workspaces
POST /workspaces/{ws_id}/users
```

#### 4.1.2 Gestão de Documentos Assíncrona com Workspaces
**Requisitos Funcionais:**
- [REQ-005] Upload de documentos com processamento em background por workspace
- [REQ-006] Status em tempo real do processamento
- [REQ-007] Suporte a PDF, DOCX, TXT (até 100MB por arquivo)
- [REQ-008] Metadados estruturados por workspace
- [REQ-009] **Flexibilidade de modelos de embedding** (OpenAI, Cohere, HuggingFace)

**Endpoints:**
```
POST /workspaces/{ws_id}/documents/upload
GET  /workspaces/{ws_id}/documents/{doc_id}/status
GET  /workspaces/{ws_id}/documents
DELETE /workspaces/{ws_id}/documents/{doc_id}
PUT  /workspaces/{ws_id}/documents/{doc_id}/metadata
```

#### 4.1.3 Busca Híbrida Multi-Tenant
**Requisitos Funcionais:**
- [REQ-010] **Busca híbrida**: semântica + palavra-chave + metadados
- [REQ-011] Três modos de busca configuráveis:
  - `semantic`: Apenas similaridade vetorial
  - `keyword`: Apenas full-text search
  - `hybrid`: Combinação ranqueada de ambos
- [REQ-012] Filtros por workspace, tipo, data, autor
- [REQ-013] Citação de fontes com links para documentos originais
- [REQ-014] Histórico de conversas por usuário e workspace

**Endpoint de Busca Aprimorado:**
```
POST /workspaces/{ws_id}/query
{
  "query": "relatório anual 2024",
  "mode": "hybrid", // semantic | keyword | hybrid
  "filters": {
    "document_type": "pdf",
    "date_range": {"start": "2024-01-01", "end": "2024-12-31"}
  },
  "limit": 10
}
```

#### 4.1.4 Dashboard de Custos e Rate Limiting
**Requisitos Funcionais:**
- [REQ-015] **Dashboard de custos** por organização e workspace
- [REQ-016] **Rate limiting** configurável por tenant/usuário
- [REQ-017] **Alertas automáticos** quando próximo do limite de custos
- [REQ-018] **Relatórios de uso** detalhados

**Endpoints:**
```
GET /organizations/{org_id}/costs/dashboard
GET /organizations/{org_id}/costs/history
GET /workspaces/{ws_id}/usage/stats
POST /organizations/{org_id}/limits/configure
```

#### 4.1.5 Painéis de Administração Especializados

**Painel do Super Admin:**
- [REQ-019] Métricas de saúde do sistema
- [REQ-020] Custos totais de API LLM por provider
- [REQ-021] Gestão de tenants ativos
- [REQ-022] Configuração de modelos de embedding disponíveis

**Painel do Tenant Admin:**
- [REQ-023] Gestão de usuários e workspaces da organização
- [REQ-024] Relatórios de uso e custos organizacionais
- [REQ-025] Configuração de limites e políticas
- [REQ-026] Auditoria de acesso a documentos

### 4.2 Requisitos Não-Funcionais

#### 4.2.1 Performance
- [NFR-001] Tempo de resposta < 2s para buscas simples
- [NFR-002] Processamento de documento de 50MB em < 5 minutos
- [NFR-003] Suporte a 1000 usuários concorrentes
- [NFR-004] **Cache agressivo** de consultas idênticas (Redis)

#### 4.2.2 Segurança
- [NFR-005] Autenticação JWT com refresh tokens
- [NFR-006] HTTPS obrigatório em produção
- [NFR-007] Logs de auditoria para todas as operações
- [NFR-008] Criptografia de dados sensíveis em repouso
- [NFR-009] **Isolamento físico** de arquivos por organização/workspace

#### 4.2.3 Confiabilidade
- [NFR-010] Uptime 99.9%
- [NFR-011] Backup automático diário
- [NFR-012] Recovery em < 1 hora
- [NFR-013] Health checks para todos os serviços

#### 4.2.4 Escalabilidade e Custos
- [NFR-014] Horizontal scaling para workers Celery
- [NFR-015] Database connection pooling
- [NFR-016] Load balancing ready
- [NFR-017] Stateless API design
- [NFR-018] **Controle de custos** automatizado com alertas
- [NFR-019] **Rate limiting** para prevenir uso excessivo
- [NFR-020] **Logging estruturado (JSON)** em todos os serviços para correlação de erros

---

## 5. EXPERIÊNCIA DO USUÁRIO

### 5.1 Jornadas de Usuário Críticas

#### 5.1.1 Seleção e Acesso a Workspaces
**Nova Jornada:**
1. Login → Seleção de organização (se múltiplas)
2. Dashboard mostra workspaces disponíveis
3. Seleção de workspace específico
4. Interface contextualizada ao workspace escolhido

#### 5.1.2 Busca Híbrida Inteligente
**Interface Renovada:**
- Campo de busca com seletor de modo (Semântica/Palavra-chave/Híbrida)
- Filtros visuais por workspace, departamento, data, tipo
- Resultados ranqueados com scores de relevância
- Toggle entre visualização semântica e exata
- Citações clicáveis que abrem o documento original

### 5.2 Wireframes Principais

```
┌─────────────────────────────────────────────────────┐
│ RAG Enterprise v2.0    │ Workspace: Jurídico     │⚙️│
├─────────────────────────────────────────────────────┤
│ [📁 Documentos] [💬 Buscar] [📊 Avaliações] [💰 Custos]│
├─────────────────────────────────────────────────────┤
│                                                     │
│  🔍 [Digite sua pergunta aqui...            ] [🔍] │
│      Modo: [Híbrida ▼] [Semântica] [Palavra-chave] │
│                                                     │
│  📂 Filtros:                                        │
│  [ Workspace ▼] [ Tipo ▼] [ Data ▼] [ Autor ▼]     │
│                                                     │
│  💬 Resultado (Score: 0.89):                       │
│  ┌─────────────────────────────────────────────────┐ │
│  │ 🎯 Match Semântico: A política de férias...     │ │
│  │ 🔍 Match Exato: "Relatório Anual 2024"         │ │
│  │                                                 │ │
│  │ 📎 Fontes:                                      │ │
│  │ • Manual RH 2024.pdf (p.15) [abrir] 📊         │ │
│  │ • Políticas Internas.docx (seção 3.2) [abrir]  │ │
│  └─────────────────────────────────────────────────┘ │
│                                                     │
│  💰 Custo desta consulta: $0.003 | Limite mensal: │ │
│      $47.23 / $100.00 ████████░░ 47%               │
└─────────────────────────────────────────────────────┘
```

---

## 6. PLANO DE IMPLEMENTAÇÃO

### 6.1 Fases de Desenvolvimento

#### **Fase 1: Fundação + Workspaces (Semanas 1-5)**
**Objetivos:**
- Migrar arquitetura monolítica para API + Cliente
- Implementar multi-tenancy com workspaces
- Estabelecer processamento assíncrono

**Entregas:**
- FastAPI com endpoints básicos
- PostgreSQL + pgvector + workspaces configurado
- Sistema flexível de embedding models
- Celery workers funcionando
- Streamlit como cliente da API
- Sistema de autenticação JWT multi-nível
- **Semana 3**: Estabelecer baseline do Alembic e primeira migração

**Baseline Alembic (Semana 3):**
```python
# migrations/versions/001_initial_schema.py
def upgrade():
    """Primeira migração - Schema completo do PRD"""
    # Criar todas as tabelas conforme definido no PRD
    # A partir deste ponto: TODAS as alterações via Alembic
    pass

def downgrade():
    """Rollback completo para estado vazio"""
    pass
```

**Critérios de Sucesso:**
- Upload assíncrono funcional
- Isolamento total entre organizações e workspaces
- Performance 5x melhor que versão atual
- **Schema versionado** com Alembic desde o início

#### **Fase 2: Busca Híbrida + Controle de Custos (Semanas 6-9)**
**Objetivos:**
- Implementar busca híbrida robusta
- Sistema de controle de custos
- Rate limiting por tenant

**Entregas:**
- Busca vetorial + full-text combinadas
- Dashboard de custos em tempo real
- Rate limiting configurável
- Cache agressivo de consultas
- Interface de busca aprimorada

**Critérios de Sucesso:**
- Busca híbrida sub-2s em 95% das consultas
- Controle de custos funcionando
- Zero vazamento de dados entre workspaces

#### **Fase 3: Painéis Admin + Features Avançadas (Semanas 10-13)**
**Objetivos:**
- Painéis especializados para diferentes roles
- Avaliações de funcionários por workspace
- Sistema de auditoria
- **Experiência de onboarding aprimorada**

**Entregas:**
- Painel Super Admin completo
- Painel Tenant Admin completo
- **Wizard de Configuração** para novos Tenant Admins
- Módulo de avaliações por workspace
- Logs de auditoria
- Relatórios de uso detalhados

**História de Usuário - Onboarding:**
```
Como um novo Tenant Admin, no meu primeiro login, 
eu quero ser guiado por um 'Wizard de Configuração' 
para criar meu primeiro workspace e convidar meus primeiros usuários,
de forma que eu possa começar a usar o sistema rapidamente 
sem me sentir perdido na complexidade das configurações.

Critérios de Aceitação:
- Wizard aparece automaticamente no primeiro login
- Guia passo-a-passo para criar organização e workspace
- Interface para convidar primeiros usuários
- Tutorial interativo das funcionalidades básicas
- Opção de pular o wizard (para usuários avançados)
```

**Critérios de Sucesso:**
- Painéis administrativos funcionais
- Sistema de avaliações isolado por workspace
- Auditoria completa implementada
- **90% dos novos tenants completam o onboarding**

#### **Fase 4: Produção + Monitoramento (Semanas 14-17)**
**Objetivos:**
- Deploy em produção
- **Monitoramento avançado com Golden Signals**
- Otimizações finais

**Entregas:**
- Ambiente de produção configurado
- CI/CD pipeline
- **Monitoramento Golden Signals** com Prometheus/Grafana
- Alertas de custos automáticos
- Documentação completa

**Golden Signals para Monitoramento:**

**API FastAPI:**
- **Latência**: P95 de tempo de resposta < 2s (especialmente `/query`)
- **Tráfego**: RPS (requisições por segundo) por endpoint
- **Erros**: Taxa de HTTP 5xx < 0.1%
- **Saturação**: CPU < 80%, Memória < 85%, Connection Pool usage

**Celery Workers:**
- **Latência**: Tempo médio de processamento de documentos
- **Tráfego**: Tarefas processadas por minuto
- **Erros**: Taxa de falha de tarefas < 0.5%
- **Saturação**: Tamanho da fila Redis, Workers ativos vs disponíveis

**PostgreSQL:**
- **Latência**: Tempo médio de consulta (especially vector search)
- **Tráfego**: Consultas por segundo, Conexões ativas
- **Erros**: Queries falhando, Connection timeouts
- **Saturação**: CPU, Memória, Disk I/O, Connection pool

**Configuração Prometheus:**
```yaml
# prometheus.yml - Exemplo de configuração
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'fastapi-rag'
    static_configs:
      - targets: ['api:8000']
    metrics_path: '/metrics'
    
  - job_name: 'celery-workers'
    static_configs:
      - targets: ['worker:9540']
      
  - job_name: 'postgresql'
    static_configs:
      - targets: ['postgres-exporter:9187']
```

**Critérios de Sucesso:**
- Sistema rodando em produção
- SLA de 99.9% uptime
- **Alertas funcionando** para todos os Golden Signals
- Controle de custos automatizado
- Equipe treinada para operação

### 6.2 Recursos Necessários

#### **Equipe:**
- 1 Tech Lead (Full-time)
- 1 Backend Developer Python (Full-time)
- 1 Frontend Developer (Part-time)
- 1 DevOps Engineer (Part-time)
- 1 QA Engineer (Part-time)

#### **Infraestrutura:**
- Servidor de desenvolvimento (32GB RAM, 16 vCPUs)
- PostgreSQL com pgvector (16GB RAM)
- Redis cluster para cache e broker
- Storage para documentos (500GB inicial)
- Ambiente de monitoramento

#### **Orçamento Estimado:**
- Desenvolvimento: R$ 180.000 (4.5 meses)
- Infraestrutura: R$ 8.000/mês
- **Licenças e APIs**: R$ 2.100/mês (economia de 30% com GPT-5-mini)
- Monitoramento: R$ 1.000/mês

---

## 7. RISCOS E MITIGAÇÕES

### 7.1 Riscos Técnicos

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Performance do pgvector | Média | Alto | Benchmarks prévios + fallback para Pinecone |
| Complexidade do multi-workspace | Alta | Alto | Prototipação prévia + testes extensivos |
| Migração de dados | Baixa | Alto | Scripts de migração + ambiente de teste |
| Busca híbrida performance | Média | Médio | Índices otimizados + cache agressivo |

### 7.2 Riscos de Negócio

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| **Custo de APIs escala descontroladamente** | **Alta** | **Alto** | **Rate limiting + dashboard custos + alertas** |
| Resistência à mudança | Alta | Médio | Treinamento + rollout gradual |
| Downtime na migração | Baixa | Alto | Migração blue-green + rollback plan |
| Budget overrun | Média | Médio | Controle semanal + escopo flexível |

### 7.3 Riscos Financeiros (NOVO)

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Custos OpenAI excedem orçamento | Alta | Alto | Limites por tenant + cache agressivo + alertas |
| Usuários abusam do sistema | Média | Médio | Rate limiting rigoroso + monitoramento |
| Crescimento de uso imprevisível | Média | Alto | Dashboard custos + alertas automáticos |

---

## 8. CRITÉRIOS DE SUCESSO

### 8.1 Métricas de Performance
- **Tempo de resposta**: < 2s para 95% das consultas
- **Busca híbrida**: 90%+ de satisfação vs busca apenas semântica
- **Throughput**: 1000+ usuários simultâneos
- **Disponibilidade**: 99.9% uptime
- **Processamento**: 50MB document em < 5min

### 8.2 Métricas de Negócio
- **Adoção**: 80% dos usuários ativos em 30 dias pós-deploy
- **Satisfação**: NPS > 70
- **Produtividade**: 60% redução no tempo de busca por informações
- **Segurança**: Zero vazamentos de dados entre workspaces
- **Controle de custos**: 100% dos tenants com visibilidade de custos
- **Onboarding**: 90% dos novos Tenant Admins completam wizard inicial

### 8.3 Métricas Técnicas
- **Cobertura de testes**: > 90%
- **Performance de build**: < 10min para CI/CD completo
- **Observabilidade**: 100% dos endpoints monitorados
- **Documentação**: APIs 100% documentadas com OpenAPI

### 8.4 Métricas de Controle de Custos (NOVO)
- **Previsibilidade**: 100% dos tenants com limites configurados
- **Transparência**: Dashboard de custos atualizados em tempo real
- **Eficiência**: 80% de cache hit rate para consultas repetidas
- **Alertas**: Alertas automáticos 24h antes de atingir limites

---

## 9. ARQUITETURA DE CUSTOS E CONTROLE FINANCEIRO

### 9.1 Modelo de Controle de Custos

#### 9.1.1 Componentes de Custo Monitorados
```python
# Estrutura de rastreamento de custos
cost_components = {
    "embedding_generation": {
        "provider": "openai",
        "model": "text-embedding-3-small", 
        "cost_per_token": 0.00000002,  # $0.02 / 1M tokens
        "tracking": "per_document_processing"
    },
    "llm_queries": {
        "provider": "openai",
        "model": "gpt-5-mini",  # Modelo padrão atualizado
        "cost_input": 0.000005,   # Estimativa: $5 / 1M input tokens (mais eficiente)
        "cost_output": 0.000015,  # Estimativa: $15 / 1M output tokens (mais eficiente)
        "tracking": "per_conversation_message"
    },
    "vector_storage": {
        "provider": "postgresql",
        "cost_per_gb_month": 0.10,
        "tracking": "storage_used"
    }
}
```

#### 9.1.2 Rate Limiting Estratificado
```python
rate_limits = {
    "employee": {
        "queries_per_day": 100,
        "uploads_per_day": 5,
        "max_document_size_mb": 10
    },
    "manager": {
        "queries_per_day": 500,
        "uploads_per_day": 25,
        "max_document_size_mb": 50
    },
    "tenant_admin": {
        "queries_per_day": 1000,
        "uploads_per_day": 100,
        "max_document_size_mb": 100
    }
}
```

### 9.2 Dashboard de Custos em Tempo Real

#### 9.2.1 Painel Tenant Admin - Controle Financeiro
```
┌─────────────────────────────────────────────────────┐
│ 💰 Controle de Custos - Organização ACME Corp      │
├─────────────────────────────────────────────────────┤
│ Mês Atual: Janeiro 2025                            │
│                                                     │
│ 📊 Resumo Financeiro:                               │
│ ┌─────────────────────────────────────────────────┐ │
│ │ Gasto Atual: $127.45 / $500.00                 │ │
│ │ ████████████░░░░░░░░░ 25.5%                     │ │
│ │                                                 │ │
│ │ Por Serviço:                                    │ │
│ │ • Consultas LLM:    $89.20 (70%)               │ │
│ │ • Embeddings:       $28.15 (22%)               │ │
│ │ • Armazenamento:    $10.10 (8%)                │ │
│ │                                                 │ │
│ │ Por Workspace:                                  │ │
│ │ • Jurídico:         $67.30 (53%)               │ │
│ │ • Marketing:        $35.45 (28%)               │ │
│ │ • RH:              $24.70 (19%)                │ │
│ └─────────────────────────────────────────────────┘ │
│                                                     │
│ ⚠️  Alertas:                                        │
│ • Workspace Jurídico próximo do limite diário      │
│ • Usuário joão.silva@acme.com excedeu 90% do limite│
│                                                     │
│ 📈 Projeção Mensal: $385.20 (dentro do orçamento)  │
└─────────────────────────────────────────────────────┘
```

#### 9.2.2 Painel Super Admin - Visão Global
```
┌─────────────────────────────────────────────────────┐
│ 🏢 Super Admin Dashboard - Visão Global             │
├─────────────────────────────────────────────────────┤
│ Sistema RAG Enterprise - Métricas Globais          │
│                                                     │
│ 📊 Resumo Operacional:                              │
│ ┌─────────────────────────────────────────────────┐ │
│ │ Tenants Ativos: 15                              │ │
│ │ Usuários Online: 247                            │ │
│ │ Documentos Processados (hoje): 1,234            │ │
│ │ Consultas (hora): 5,678                         │ │
│ │                                                 │ │
│ │ 💰 Custos Totais (Janeiro):                     │ │
│ │ Total: $2,847.30                                │ │
│ │ • OpenAI: $2,156.80 (76%)                       │ │
│ │ • Infraestrutura: $520.30 (18%)                 │ │
│ │ • Storage: $170.20 (6%)                         │ │
│ │                                                 │ │
│ │ 🎯 Top 5 Tenants por Uso:                       │ │
│ │ 1. ACME Corp: $347.60                           │ │
│ │ 2. TechStart: $289.45                           │ │
│ │ 3. LegalFirm: $234.20                           │ │
│ │ 4. HealthCare: $198.75                          │ │
│ │ 5. EduInst: $167.30                             │ │
│ └─────────────────────────────────────────────────┘ │
│                                                     │
│ 🚨 Alertas do Sistema:                              │
│ • Tenant "ACME Corp" atingiu 95% do limite mensal  │ │
│ • Worker #3 com alta latência (>30s)               │ │
│ • Banco atingiu 85% da capacidade de storage       │ │
└─────────────────────────────────────────────────────┘
```

### 9.3 Estratégias de Otimização de Custos

#### 9.3.1 Cache Inteligente
- **Cache de Embeddings**: Documentos similares reutilizam embeddings
- **Cache de Respostas**: Perguntas idênticas retornam respostas cached
- **Cache de Contexto**: Chunks relevantes são cached por período
- **Meta Cache**: Cache dos metadados de documentos mais acessados

#### 9.3.2 Rate Limiting Inteligente
- **Burst Allowance**: Permite rajadas ocasionais dentro de limites seguros
- **Quality-Based Limiting**: Consultas de baixa qualidade consomem mais quota
- **Time-Based Scaling**: Limites maiores durante horário comercial
- **Department-Based Quotas**: Diferentes limites por departamento

#### 9.3.3 Otimização de Prompts
- **Prompt Templates**: Templates otimizados para reduzir tokens
- **Context Pruning**: Remove contexto redundante automaticamente
- **Smart Chunking**: Chunks mais precisos reduzem tokens necessários
- **Response Caching**: Respostas similares são reutilizadas

---

## 10. SEGURANÇA E COMPLIANCE

### 10.1 Modelo de Segurança em Camadas

#### 10.1.1 Camada de Network
- **HTTPS Obrigatório**: TLS 1.3 para toda comunicação
- **WAF (Web Application Firewall)**: Proteção contra ataques comuns
- **Rate Limiting Global**: Proteção contra DDoS
- **IP Whitelisting**: Opcional por tenant

#### 10.1.2 Camada de Aplicação
- **JWT Tokens**: Autenticação stateless com refresh
- **RBAC (Role-Based Access Control)**: Controle granular por workspace
- **Input Sanitization**: Validação rigorosa de todas as entradas
- **SQL Injection Prevention**: Prepared statements obrigatórios

#### 10.1.3 Camada de Dados
- **Encryption at Rest**: AES-256 para dados sensíveis
- **Encryption in Transit**: TLS para todas as conexões
- **Database Isolation**: Queries obrigatoriamente filtradas por tenant
- **Backup Encryption**: Backups criptografados com chaves rotacionadas

### 10.2 Compliance e Auditoria

#### 10.2.1 GDPR/LGPD Compliance
```sql
-- Tabela de auditoria para compliance
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id),
    workspace_id UUID REFERENCES workspaces(id),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    -- Índices para consultas de auditoria
    CONSTRAINT audit_logs_retention CHECK (created_at > NOW() - INTERVAL '7 years')
);

-- Right to be forgotten implementation
CREATE TABLE data_deletion_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id),
    user_id UUID REFERENCES users(id),
    request_type VARCHAR(50) NOT NULL, -- 'user_data', 'organization_data'
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'processing', 'completed'
    requested_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    metadata JSONB
);
```

#### 10.2.2 Logs de Auditoria Estruturados
```python
# Exemplo de log estruturado para auditoria de negócio
audit_event = {
    "timestamp": "2025-01-15T10:30:45Z",
    "organization_id": "123e4567-e89b-12d3-a456-426614174000",
    "workspace_id": "456e7890-e89b-12d3-a456-426614174111", 
    "user_id": "789e0123-e89b-12d3-a456-426614174222",
    "action": "document_access",
    "resource_type": "document",
    "resource_id": "abc12345-e89b-12d3-a456-426614174333",
    "details": {
        "document_name": "contract_template_2024.pdf",
        "access_type": "view",
        "query_used": "encontre o template de contrato mais recente"
    },
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0...",
    "cost_incurred": 0.003
}

# Exemplo de log estruturado para depuração técnica
technical_log = {
    "timestamp": "2025-01-15T10:30:45Z",
    "level": "ERROR",
    "service": "fastapi-api",
    "request_id": "req_abc123def456",  # Para correlação
    "trace_id": "trace_789xyz012",      # Para correlação distribuída
    "user_id": "789e0123-e89b-12d3-a456-426614174222",
    "endpoint": "/workspaces/456/query",
    "method": "POST",
    "status_code": 500,
    "error": {
        "type": "DatabaseConnectionError",
        "message": "Connection to PostgreSQL timed out",
        "stack_trace": "...",
        "context": {
            "query": "SELECT * FROM document_chunks WHERE...",
            "execution_time_ms": 30000,
            "retry_count": 3
        }
    },
    "performance": {
        "response_time_ms": 30045,
        "memory_usage_mb": 245,
        "cpu_usage_percent": 78
    }
}
```

**Requisitos de Logging:**
- [REQ-AUDIT-001] Todos os eventos de negócio devem ser logados na tabela `audit_logs`
- [REQ-TECH-001] Todos os serviços devem emitir logs JSON estruturados
- [REQ-TRACE-001] Cada requisição deve ter `request_id` único para correlação
- [REQ-RETENTION-001] Logs técnicos: 30 dias, Logs de auditoria: 7 anos

---

## 11. PLANO DE MIGRAÇÃO E ROLLOUT

### 11.1 Estratégia de Migração

#### 11.1.1 Migração Blue-Green
```
Fase 1: Setup Paralelo
┌─────────────────┐    ┌─────────────────┐
│   Sistema       │    │   Sistema       │
│   Atual (Blue) │    │   Novo (Green)  │
│                 │    │                 │
│ • SQLite        │    │ • PostgreSQL    │
│ • FAISS         │    │ • pgvector      │  
│ • Streamlit     │    │ • FastAPI       │
│ • Monolito      │    │ • Workspaces    │
└─────────────────┘    └─────────────────┘
        │                       ▲
        │                       │
        └─── Migração Dados ────┘

Fase 2: Teste Paralelo
• Migração de dados de teste
• Validação de funcionalidades
• Performance benchmarks
• Testes de carga

Fase 3: Rollout Gradual
• 10% do tráfego → Green
• 50% do tráfego → Green  
• 100% do tráfego → Green
• Desativação do Blue
```

#### 11.1.2 Scripts de Migração de Dados
```python
# Script de migração de dados
def migrate_documents():
    """Migra documentos do SQLite/FAISS para PostgreSQL/pgvector"""
    
    # 1. Criar organizações padrão
    default_org = create_organization("Organização Padrão")
    default_workspace = create_workspace(default_org.id, "Geral")
    
    # 2. Migrar usuários
    for old_user in old_db.users:
        new_user = create_user(
            organization_id=default_org.id,
            username=old_user.username,
            role=map_old_role_to_new(old_user.role)
        )
        assign_to_workspace(new_user.id, default_workspace.id)
    
    # 3. Migrar documentos e embeddings
    for old_doc in old_db.documents:
        # Upload arquivo para nova estrutura
        new_file_path = f"tenants/{default_org.id}/workspaces/{default_workspace.id}/documents/{doc.id}/{doc.filename}"
        
        # Criar documento
        new_doc = create_document(
            organization_id=default_org.id,
            workspace_id=default_workspace.id,
            title=old_doc.title,
            file_path=new_file_path
        )
        
        # Migrar chunks e embeddings
        for chunk in old_doc.chunks:
            create_document_chunk(
                document_id=new_doc.id,
                content=chunk.content,
                embedding=chunk.embedding,
                embedding_model_id=default_embedding_model.id
            )
```

### 11.2 Cronograma de Rollout

#### 11.2.1 Timeline Detalhada
```
Semana 1-2: Preparação
├── Setup ambiente Green
├── Scripts de migração
├── Testes unitários/integração
└── Documentação técnica

Semana 3: Migração Piloto
├── Migrar dados de 1 organização teste
├── Validar funcionalidades básicas
├── Ajustes de performance
└── Feedback inicial

Semana 4: Rollout Gradual
├── Segunda: 10% tráfego → Green
├── Quarta: 25% tráfego → Green
├── Sexta: 50% tráfego → Green
└── Monitoramento constante

Semana 5: Rollout Completo
├── Segunda: 75% tráfego → Green
├── Quarta: 100% tráfego → Green
├── Sexta: Desativar Blue
└── Celebração 🎉
```

---

## 12. CONCLUSÃO E PRÓXIMOS PASSOS

### 12.1 Transformação Proposta

Este PRD evolui o sistema RAG atual de um **protótipo funcional** para uma **plataforma enterprise-grade** que resolve todos os problemas identificados:

#### **Problemas Resolvidos:**
✅ **Isolamento Granular**: Workspaces dentro de organizações  
✅ **Busca Inteligente**: Híbrida (semântica + palavra-chave)  
✅ **Controle de Custos**: Dashboard transparente + rate limiting  
✅ **Escalabilidade**: Arquitetura desacoplada + processamento assíncrono  
✅ **Flexibilidade**: Modelos de embedding agnósticos  
✅ **Segurança**: Isolamento em múltiplas camadas  
✅ **Compliance**: Auditoria completa + GDPR/LGPD ready  

#### **Diferenciais Competitivos:**
🏆 **Multi-Workspace**: Isolamento administrativo dentro de organizações  
🏆 **Busca Híbrida**: Melhor precisão que soluções apenas semânticas  
🏆 **Transparência de Custos**: Controle financeiro em tempo real  
🏆 **Flexibilidade de Modelos**: Não dependência de um único provider  
🏆 **Enterprise Security**: Segurança em camadas para compliance  

### 12.2 ROI Projetado Refinado

#### **Investimento Total (18 meses):**
- Desenvolvimento: R$ 180.000
- Infraestrutura (ano 1): R$ 144.000 (R$ 12k/mês)
- **Operação (ano 1)**: R$ 37.200 (R$ 3.1k/mês - economia 30% com GPT-5-mini)
- **Total**: R$ 361.200

#### **Retorno Esperado (ano 1):**
- Produtividade (60% redução tempo busca): R$ 480.000
- Redução retrabalho (melhor precisão): R$ 120.000
- Compliance automático (evitar multas): R$ 200.000
- **Total**: R$ 800.000

#### **ROI**: 121% no primeiro ano (melhoria devido ao GPT-5-mini)

### 12.3 Próximos Passos Imediatos

#### **Semana 1-2: Validação e Aprovação**
1. ✅ Apresentação do PRD para stakeholders
2. 📋 Validação de requisitos com usuários finais
3. 💰 Aprovação orçamentária
4. 👥 Formação da equipe de desenvolvimento

#### **Semana 3-4: Setup Técnico**
1. 🏗️ Configuração do ambiente de desenvolvimento
2. 📊 Setup do pipeline CI/CD
3. 🔧 Instalação PostgreSQL + pgvector
4. 🐳 Containerização com Docker

#### **Semana 5: Início do Desenvolvimento**
1. 🚀 Kick-off oficial da Fase 1
2. 📈 Setup de métricas e monitoring
3. 📝 Documentação técnica inicial
4. 🧪 Testes de conceito dos componentes críticos

### 12.4 Indicadores de Sucesso (KPIs) Revisados

#### **Mês 1-3: Fundação**
- ✅ Arquitetura desacoplada funcional
- ✅ Multi-tenancy com workspaces implementado
- ✅ Performance 5x superior ao sistema atual

#### **Mês 4-6: Features Core**
- ✅ Busca híbrida com 90%+ satisfação de usuários
- ✅ Dashboard de custos em tempo real
- ✅ Zero vazamentos de dados entre workspaces

#### **Mês 6-9: Enterprise Features**
- ✅ Painéis administrativos funcionais
- ✅ Compliance GDPR/LGPD completo
- ✅ Sistema de auditoria operacional

#### **Mês 9-12: Otimização e Escala**
- ✅ 1000+ usuários concorrentes suportados
- ✅ SLA 99.9% uptime mantido
- ✅ ROI positivo comprovado

---

**Status**: 🚀 **Pronto para Aprovação e Início**  
**Próxima Ação**: Apresentação executiva para aprovação  
**Data Alvo Kick-off**: 2 semanas após aprovação  
**Go-Live Esperado**: 18 semanas após kick-off  

---

*Este PRD representa um plano abrangente para transformar o sistema RAG atual em uma plataforma enterprise-grade líder de mercado. Cada detalhe foi cuidadosamente planejado para garantir sucesso técnico, viabilidade financeira e adoção pelos usuários.*

**Versão**: 2.0  
**Última Atualização**: Janeiro 2025  
**Próxima Revisão**: Após kick-off do projeto