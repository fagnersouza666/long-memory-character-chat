# Correção do Parâmetro `temperature` para Modelos GPT-5

## Data
04/09/2025

## Descrição
Remoção do parâmetro `temperature` nas chamadas à API dos modelos GPT-5-mini devido a incompatibilidade. 
O erro ocorria com a seguinte mensagem:
```
Error code: 400 - {'error': {'message': "Unsupported value: 'temperature' does not support 0.1 with this model. Only the default (1) value is supported.", 'type': 'invalid_request_error', 'param': 'temperature', 'code': 'unsupported_value'}}
```

## Arquivos Modificados

### 1. `document_generator.py`
- Remoção do parâmetro `temperature=0.1` na chamada à API do GPT-5-mini

### 2. `rag_components/query_processor.py`
- Remoção do parâmetro `temperature` na inicialização do LLM
- Atualização da assinatura do método `query` para não incluir o parâmetro `temperature`

### 3. `rag_components/rag_agent.py`
- Atualização da assinatura do método `query` para não incluir o parâmetro `temperature`
- Ajuste na chamada ao método `query` do QueryProcessor

### 4. `app.py`
- Remoção do parâmetro `temperature` na função `query_agent`
- Remoção do parâmetro `temperature` na chamada ao método `query` do agente

## Motivação
Os modelos da série GPT-5 não suportam o parâmetro `temperature` com valores diferentes do padrão (1). 
Essa mudança foi implementada para garantir a compatibilidade com os modelos mais recentes da OpenAI.

## Impacto
- Corrige o erro de parâmetro não suportado
- Mantém a funcionalidade original do sistema
- Garante compatibilidade com os modelos GPT-5-mini