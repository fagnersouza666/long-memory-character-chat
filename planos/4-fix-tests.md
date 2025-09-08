# Plano 4 — Correção de literais bytes nos testes

Contexto: `pytest` falhou na coleta devido a literais `bytes` com caracteres não‑ASCII (acentos) em `BytesIO`.

Ações
1) Atualizar testes para usar UTF‑8 corretamente:
   - Substituir `io.BytesIO(b"Conteúdo de teste para o documento")` por `io.BytesIO("Conteúdo de teste para o documento".encode("utf-8"))`.
   - Arquivos: `backend/tests/test_document_processing.py`, `backend/tests/test_documents.py`.
2) Reexecutar `pytest -q` no backend e registrar a saída.

Notas
- Mudança mínima, focada apenas nos literais afetados.
- Sem comandos destrutivos.
