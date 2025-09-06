import pytest
from fastapi.testclient import TestClient
import uuid

def test_create_conversation(test_client, create_test_user):
    """Teste de criação de conversa"""
    if not create_test_user:
        pytest.fail("Falha ao criar usuário de teste")
    
    headers = {"Authorization": f"Bearer {create_test_user['token']}"}
    
    response = test_client.post(
        "/api/v1/memory/conversations/",
        json={
            "title": "Test Conversation",
            "metadata": {"topic": "testing"}
        },
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["title"] == "Test Conversation"
    assert data["user_id"] is not None

def test_list_conversations(test_client, create_test_user):
    """Teste de listagem de conversas"""
    if not create_test_user:
        pytest.fail("Falha ao criar usuário de teste")
    
    headers = {"Authorization": f"Bearer {create_test_user['token']}"}
    
    # Criar uma conversa de teste
    test_client.post(
        "/api/v1/memory/conversations/",
        json={
            "title": "Test Conversation",
            "metadata": {"topic": "testing"}
        },
        headers=headers
    )
    
    # Listar conversas
    response = test_client.get("/api/v1/memory/conversations/", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_get_conversation(test_client, create_test_user):
    """Teste de obtenção de conversa específica"""
    if not create_test_user:
        pytest.fail("Falha ao criar usuário de teste")
    
    headers = {"Authorization": f"Bearer {create_test_user['token']}"}
    
    # Criar uma conversa
    create_response = test_client.post(
        "/api/v1/memory/conversations/",
        json={
            "title": "Test Conversation",
            "metadata": {"topic": "testing"}
        },
        headers=headers
    )
    
    assert create_response.status_code == 200
    conversation_id = create_response.json()["id"]
    
    # Obter a conversa
    response = test_client.get(f"/api/v1/memory/conversations/{conversation_id}", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == conversation_id
    assert data["title"] == "Test Conversation"

def test_add_message_to_conversation(test_client, create_test_user):
    """Teste de adição de mensagem a uma conversa"""
    if not create_test_user:
        pytest.fail("Falha ao criar usuário de teste")
    
    headers = {"Authorization": f"Bearer {create_test_user['token']}"}
    
    # Criar uma conversa
    create_response = test_client.post(
        "/api/v1/memory/conversations/",
        json={
            "title": "Test Conversation",
            "metadata": {"topic": "testing"}
        },
        headers=headers
    )
    
    assert create_response.status_code == 200
    conversation_id = create_response.json()["id"]
    
    # Adicionar mensagem
    response = test_client.post(
        f"/api/v1/memory/conversations/{conversation_id}/messages/",
        json={
            "role": "user",
            "content": "Mensagem de teste",
            "timestamp": "2025-09-06T10:00:00"
        },
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "user"
    assert data["content"] == "Mensagem de teste"

def test_create_memory_summary(test_client, create_test_user):
    """Teste de criação de resumo de memória"""
    if not create_test_user:
        pytest.fail("Falha ao criar usuário de teste")
    
    headers = {"Authorization": f"Bearer {create_test_user['token']}"}
    
    response = test_client.post(
        "/api/v1/memory/memory-summaries/",
        json={
            "content": "Resumo importante sobre o projeto",
            "relevance_score": 0.95
        },
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["content"] == "Resumo importante sobre o projeto"
    assert data["relevance_score"] == 0.95