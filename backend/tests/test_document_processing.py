import pytest
from fastapi.testclient import TestClient
import io

def test_create_processing_task(test_client, create_test_user):
    """Teste de criação de tarefa de processamento"""
    if not create_test_user:
        pytest.fail("Falha ao criar usuário de teste")
    
    headers = {"Authorization": f"Bearer {create_test_user['token']}"}
    
    # Primeiro, fazer upload de um documento
    test_file = io.BytesIO("Conteúdo de teste para o documento".encode("utf-8"))
    test_file.name = "test_document.txt"
    
    upload_response = test_client.post(
        "/api/v1/documents/",
        files={"file": (test_file.name, test_file, "text/plain")},
        data={"title": "Test Document"},
        headers=headers
    )
    
    assert upload_response.status_code == 200
    document_id = upload_response.json()["id"]
    
    # Criar tarefa de processamento
    response = test_client.post(
        "/api/v1/document-processing/tasks/",
        json={
            "document_id": document_id,
            "user_id": 2,  # ID do usuário de teste
            "status": "pending",
            "priority": 5
        },
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["document_id"] == document_id
    assert data["status"] == "pending"

def test_list_processing_tasks(test_client, create_test_user):
    """Teste de listagem de tarefas de processamento"""
    if not create_test_user:
        pytest.fail("Falha ao criar usuário de teste")
    
    headers = {"Authorization": f"Bearer {create_test_user['token']}"}
    
    # Listar tarefas de processamento
    response = test_client.get("/api/v1/document-processing/tasks/", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_processing_task(test_client, create_test_user):
    """Teste de obtenção de tarefa de processamento específica"""
    if not create_test_user:
        pytest.fail("Falha ao criar usuário de teste")
    
    headers = {"Authorization": f"Bearer {create_test_user['token']}"}
    
    # Primeiro, fazer upload de um documento
    test_file = io.BytesIO("Conteúdo de teste para o documento".encode("utf-8"))
    test_file.name = "test_document.txt"
    
    upload_response = test_client.post(
        "/api/v1/documents/",
        files={"file": (test_file.name, test_file, "text/plain")},
        data={"title": "Test Document"},
        headers=headers
    )
    
    assert upload_response.status_code == 200
    document_id = upload_response.json()["id"]
    
    # Criar tarefa de processamento
    task_response = test_client.post(
        "/api/v1/document-processing/tasks/",
        json={
            "document_id": document_id,
            "user_id": 2,  # ID do usuário de teste
            "status": "pending",
            "priority": 5
        },
        headers=headers
    )
    
    assert task_response.status_code == 200
    task_id = task_response.json()["id"]
    
    # Obter a tarefa de processamento
    response = test_client.get(f"/api/v1/document-processing/tasks/{task_id}", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["document_id"] == document_id

def test_get_queue_status(test_client, create_test_user):
    """Teste de obtenção do status da fila de processamento"""
    if not create_test_user:
        pytest.fail("Falha ao criar usuário de teste")
    
    headers = {"Authorization": f"Bearer {create_test_user['token']}"}
    
    # Obter status da fila de processamento
    response = test_client.get("/api/v1/document-processing/queue/status/", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "total_tasks" in data
    assert "pending_tasks" in data
    assert "processing_tasks" in data
    assert "completed_tasks" in data
    assert "failed_tasks" in data
    assert "average_processing_time" in data
