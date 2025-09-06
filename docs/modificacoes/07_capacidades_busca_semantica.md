# Modificação 07: Capacidades de Busca Semântica com Busca Híbrida

## Data
06/09/2025

## Descrição
Implementação das capacidades de busca semântica com suporte a busca híbrida (semântica + palavras-chave) para o sistema Second Brain. Esta modificação permite aos usuários encontrar informações relevantes em documentos e avaliações usando linguagem natural.

## Funcionalidades Implementadas

### 1. Tipos de Busca
- **Busca Semântica**: Utiliza embeddings para encontrar conteúdo com significado similar
- **Busca por Palavras-Chave**: Usa TF-IDF para encontrar correspondências exatas
- **Busca Híbrida**: Combina ambos os métodos para resultados mais relevantes

### 2. Fontes de Dados
- Documentos empresariais (PDF, DOCX, TXT)
- Avaliações de funcionários
- Notas e pensamentos pessoais (futuro)

### 3. Filtragem e Contexto
- Filtragem por workspace
- Filtragem por tipo de documento
- Filtragem por período
- Controle de acesso baseado em permissões

## Endpoints da API Criados

### Busca
- `POST /api/v1/search/` - Realizar busca semântica, por palavras-chave ou híbrida

## Estrutura de Requisição

```json
{
  "query": "string",
  "workspace_id": "integer (opcional)",
  "search_type": "semantic|keyword|hybrid",
  "limit": "integer",
  "filters": "object (opcional)"
}
```

## Estrutura de Resposta

```json
{
  "query": "string",
  "results": [
    {
      "id": "string",
      "content": "string",
      "metadata": "object",
      "score": "float",
      "source_type": "document|evaluation|note"
    }
  ],
  "total_results": "integer",
  "search_type": "string"
}
```

## Implementação Técnica

### Busca Semântica
- Utiliza embeddings para representar documentos e consultas
- Calcula similaridade coseno entre embeddings
- Retorna resultados ordenados por relevância semântica

### Busca por Palavras-Chave
- Usa TF-IDF (Term Frequency-Inverse Document Frequency)
- Calcula similaridade coseno entre vetores TF-IDF
- Eficiente para correspondências exatas e frases específicas

### Busca Híbrida
- Combina scores de busca semântica e por palavras-chave
- Usa média ponderada para ranqueamento final
- Fornece equilíbrio entre precisão e recall

## Controle de Acesso

### Permissões de Busca
- Usuários podem buscar apenas em conteúdo ao qual têm acesso
- Administradores podem buscar em todo o sistema
- Gerentes podem buscar em conteúdo de seu departamento
- Funcionários comuns podem buscar apenas em conteúdo pessoal e público

### Filtragem de Resultados
- Resultados são automaticamente filtrados por permissões
- Documentos pessoais visíveis apenas para o autor
- Documentos de workspace visíveis para membros do workspace
- Avaliações visíveis conforme hierarquia organizacional

## Benefícios da Implementação

1. **Precisão**: Combinação de métodos para melhores resultados
2. **Flexibilidade**: Suporte a diferentes tipos de busca
3. **Segurança**: Filtragem automática baseada em permissões
4. **Eficiência**: Limitação de resultados e ordenação por relevância
5. **Escalabilidade**: Estrutura suporta adição de novas fontes de dados
6. **Integração**: Conecta-se perfeitamente com documentos e avaliações existentes

## Considerações Futuras

1. **Melhoria de Embeddings**: Integração com modelos mais avançados
2. **Indexação em Tempo Real**: Atualização automática de índices
3. **Personalização**: Ajuste de pesos com base no histórico do usuário
4. **Multimodalidade**: Suporte a imagens e áudio nas buscas