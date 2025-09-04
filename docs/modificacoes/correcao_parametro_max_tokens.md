# Correção do Parâmetro `max_tokens` para `max_completion_tokens`

## Data
04/09/2025

## Descrição
Correção do parâmetro `max_tokens` para `max_completion_tokens` nos arquivos do projeto para resolver o erro:
```
Error code: 400 - {'error': {'message': "Unsupported parameter: 'max_tokens' is not supported with this model. Use 'max_completion_tokens' instead.", 'type': 'invalid_request_error', 'param': 'max_tokens', 'code': 'unsupported_parameter'}}
```

## Arquivos Modificados

### 1. `aiagent.py`
- Substituição de `max_tokens` por `max_completion_tokens` nas chamadas à API OpenAI
- Mantido `max_output_tokens` para chamadas ao modelo Gemini (que usa essa nomenclatura específica)

### 2. `document_generator.py`
- Substituição de `max_tokens` por `max_completion_tokens` na chamada à API OpenAI

### 3. `rag_components/rag_agent.py`
- Atualização da assinatura do método `query` para repassar os parâmetros corretamente

### 4. `rag_components/query_processor.py`
- Substituição de `max_tokens` por `max_completion_tokens` na inicialização do LLM
- Atualização do método `query` para aceitar e usar os parâmetros de temperatura e tokens

## Motivação
Alguns modelos de linguagem mais recentes da OpenAI não suportam o parâmetro `max_tokens` e exigem o uso de `max_completion_tokens` em seu lugar. Essa mudança foi implementada para garantir a compatibilidade com os modelos mais atuais.

## Impacto
- Corrige o erro de parâmetro não suportado
- Mantém a funcionalidade original do sistema
- Garante compatibilidade com os modelos mais recentes da OpenAI