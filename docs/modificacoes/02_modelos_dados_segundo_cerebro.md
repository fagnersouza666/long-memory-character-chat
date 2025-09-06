# Modificação 02: Modelos de Dados do Sistema Second Brain

## Data
06/09/2025

## Descrição
Definição dos modelos de dados para o sistema Second Brain com base no design document fornecido. Esta modificação estabelece as estruturas de dados necessárias para suportar as funcionalidades do sistema de gerenciamento de conhecimento pessoal.

## Modelos de Dados

### 1. Modelo de Usuário
Representa os usuários do sistema com informações de autenticação e autorização.

```mermaid
erDiagram
    USER {
        int id PK
        string username
        string email
        string password_hash
        string role
        string department
        datetime created_at
        datetime updated_at
    }
```

### 2. Modelo de Documento
Representa os documentos armazenados no sistema com metadados associados.

```mermaid
erDiagram
    DOCUMENT {
        int id PK
        string title
        string file_path
        string file_type
        string department
        string tags
        int uploaded_by FK
        datetime created_at
        datetime updated_at
    }
```

### 3. Modelo de Avaliação
Representa as avaliações de membros da equipe armazenadas no sistema.

```mermaid
erDiagram
    EVALUATION {
        int id PK
        string employee_id
        string evaluator
        string period
        string content
        float score
        string department
        datetime created_at
        datetime updated_at
    }
```

### 4. Modelo de Configuração
Representa a configuração dos modelos de linguagem disponíveis no sistema.

```mermaid
erDiagram
    MODEL {
        int id PK
        string name
        string displayName
        string prompt
        boolean isActive
        datetime createdAt
        datetime updatedAt
    }
```

## Relacionamentos entre Modelos

Os modelos de dados estão interconectados para fornecer uma experiência integrada:

- Usuários podem fazer upload de documentos
- Documentos são associados aos usuários que os fizeram upload
- Avaliações são vinculadas a funcionários e avaliadores (também usuários)
- Todos os modelos são organizados por workspaces e organizações para isolamento multi-tenant

## Considerações de Segurança

- Senhas são armazenadas com hash usando bcrypt
- Informações sensíveis são protegidas por criptografia
- Controle de acesso baseado em papéis é implementado em todos os níveis
- Isolamento de dados entre tenants é garantido através de relacionamentos de banco de dados