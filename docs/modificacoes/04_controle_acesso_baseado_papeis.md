# Modificação 04: Controle de Acesso Baseado em Papéis

## Data
06/09/2025

## Descrição
Implementação aprimorada do controle de acesso baseado em papéis (RBAC) para o sistema Second Brain. Esta modificação estende as capacidades de gerenciamento de usuários com controles mais granulares e seguros.

## Papéis Implementados

### 1. Administrador (admin)
- Pode gerenciar todos os usuários do sistema
- Pode atribuir papéis a outros usuários
- Pode criar e gerenciar organizações
- Pode acessar todos os recursos do sistema

### 2. Gerente (manager)
- Pode visualizar e gerenciar usuários em seu departamento
- Pode atualizar informações de usuários comuns
- Pode acessar recursos de sua organização/workspace

### 3. Funcionário (employee)
- Pode atualizar seu próprio perfil (com restrições)
- Pode acessar recursos autorizados em sua organização/workspace

## Novos Endpoints da API

### Gerenciamento de Usuários
- `PUT /api/v1/users/me` - Atualizar próprio perfil
- `PUT /api/v1/users/{user_id}` - Atualizar usuário (com permissões baseadas em papéis)
- `DELETE /api/v1/users/{user_id}` - Excluir usuário (apenas administradores)
- `GET /api/v1/users/` - Listar usuários com filtros (apenas administradores e gerentes)
- `POST /api/v1/users/assign-role/{user_id}` - Atribuir papel a usuário (apenas administradores)

## Regras de Segurança Implementadas

### 1. Proteção de Administradores
- Não é possível excluir o último administrador do sistema
- Não é possível remover o papel de administrador do último administrador
- Administradores só podem ser gerenciados por outros administradores

### 2. Hierarquia de Permissões
- Administradores podem gerenciar todos os usuários
- Gerentes podem gerenciar usuários comuns em seus departamentos
- Usuários comuns podem atualizar apenas seus próprios perfis

### 3. Restrições de Auto-Gerenciamento
- Usuários não podem excluir a si mesmos
- Usuários não podem alterar seus próprios papéis
- Campos sensíveis são protegidos durante a atualização do próprio perfil

### 4. Filtros de Listagem
- Administradores e gerentes podem filtrar usuários por papel e departamento
- Usuários comuns não podem listar outros usuários

## Benefícios da Implementação

1. **Segurança Aprimorada**: Proteções contra remoção acidental de administradores
2. **Controle Granular**: Hierarquia de permissões permite gerenciamento refinado
3. **Flexibilidade**: Filtros de listagem facilitam a administração de grandes equipes
4. **Autonomia Controlada**: Usuários podem gerenciar seus próprios perfis com segurança
5. **Governança**: Atribuição de papéis centralizada apenas para administradores